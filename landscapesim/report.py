import os
import tempfile
import zipfile
from base64 import b64encode
from datetime import datetime
from io import StringIO, BytesIO
from shutil import copyfileobj

import pdfkit
from django.conf import settings
from django.template.loader import render_to_string
from geopy.distance import vincenty
from ncdjango.geoimage import image_to_world
from pyproj import Proj, transform

from landscapesim.io.consoles import STSimConsole
from landscapesim.io.utils import get_random_csv
from landscapesim.mapimage import MapImage
from landscapesim.models import Scenario
from landscapesim.serializers.reports import StateClassSummaryReportSerializer
from landscapesim.serializers.scenarios import ScenarioInputServicesSerializer, ScenarioOutputServicesSerializer

PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=getattr(settings, 'WKHTMLTOPDF_BIN'))
PDF_OPTIONS = {
    'quiet': '',
    'encoding': 'UTF-8',
    'footer-right': '[page] of [topage]',
}

BASE_DIR = getattr(settings, 'BASE_DIR')
EXE = getattr(settings, 'STSIM_EXE_PATH')
TEMP_DIR = getattr(settings, 'NC_TEMPORARY_FILE_LOCATION')
DATASET_DOWNLOAD_DIR = getattr(settings, 'DATASET_DOWNLOAD_DIR')

MERCATOR = Proj(init='epsg:3857')
WGS84 = Proj(init='epsg:4326')


class Report:
    """ A class for handling report generation for landscapesim. """

    def __init__(self, report_name, configuration):
        self.configuration = configuration
        self.scenario = Scenario.objects.get(pk=self.configuration['scenario_id'])
        self.report_name = report_name

    def get_csv_data(self):
        lib = self.scenario.project.library
        temp_file = get_random_csv(lib.tmp_file)
        STSimConsole(exe=EXE, lib_path=lib.file, orig_lib_path=lib.orig_file) \
            .generate_report(self.report_name, temp_file, self.scenario.sid)
        result = StringIO()
        with open(temp_file, 'r') as src:
            copyfileobj(src, result)
        os.remove(temp_file)
        return result.getvalue()

    def get_context(self):
        # TODO - use our map services, etc, and design a PDF report

        # Query all related data to this model run
        strata = self.scenario.project.strata.all()
        stateclasses = self.scenario.project.stateclasses.all()
        terms = self.scenario.project.terminology
        nonspatial_distributions = self.scenario.initial_conditions_nonspatial_distributions
        initial_veg_composition = [
            {
                'name': stratum.name,
                'stateclasses': nonspatial_distributions.filter(stratum=stratum).values(
                    'stateclass__name',
                    'relative_amount'
                ),
                'proportion_of_landscape':
                    round(sum(
                        x['relative_amount'] for x in nonspatial_distributions.filter(
                            stratum=stratum
                        ).values('relative_amount')
                    ), 3)
            } for stratum in strata]

        initial_veg_composition = []
        for stratum in strata:
            name = stratum.name
            stateclasses = nonspatial_distributions.filter(stratum=stratum).values('stateclass__name', 'relative_amount')
            proportion_of_landscape = round(sum(x['relative_amount'] for x in stateclasses), 2)
            for stateclass in stateclasses:
                stateclass['relative_amount'] = "{}%".format(round(stateclass['relative_amount'], 2))
            initial_veg_composition.append({
                'name': name,
                'stateclasses': stateclasses,
                'proportion_of_landscape': proportion_of_landscape
            })

        # Map context info
        with open(os.path.join(BASE_DIR, 'landscapesim', 'static', 'img', 'report', 'scale.png'), 'rb') as f:
            scale_image_data = b64encode(f.read())

        with open(os.path.join(BASE_DIR, 'landscapesim', 'static', 'img', 'report', 'north.png'), 'rb') as f:
            north_image_data = b64encode(f.read())

        map_maker = MapImage(
            self.configuration['center'],
            self.configuration['bbox'],
            self.configuration['zoom'],
            self.configuration['basemap'],
            self.configuration['opacity']
        )

        def format_x_coord(x):
            return '{}&deg; W'.format(round(abs(x), 2)) if x < 0 else '{}&deg; E'.format(round(x, 2))

        def format_y_coord(y):
            return '{}&deg; S'.format(round(abs(y), 2)) if y < 0 else '{}&deg; N'.format(round(y, 2))

        def get_image_data(label, service_url):

            image_data, bbox = map_maker.get_image(service_url)
            to_world = image_to_world(bbox, image_data.size)
            bbox = bbox.project(WGS84, edge_points=0)

            image_handle = BytesIO()
            image_data.save(image_handle, 'png')

            scale_bar_x = 38
            scale_bar_y = image_data.size[1] - 15
            scale_bar_start = transform(MERCATOR, WGS84, *to_world(scale_bar_x, scale_bar_y))
            scale_bar_end = transform(MERCATOR, WGS84, *to_world(scale_bar_x + 96, scale_bar_y))
            scale = '{} mi'.format(round(vincenty(scale_bar_start, scale_bar_end).miles, 1))

            return {
                'label': label,
                'image_data': b64encode(image_handle.getvalue()),
                'north': format_y_coord(bbox.ymax),
                'east': format_x_coord(bbox.xmax),
                'west': format_x_coord(bbox.xmin),
                'south': format_y_coord(bbox.ymin),
                'scale': scale,
                # TODO - add legend information for a given service
            }

        # Input images
        input_services = ScenarioInputServicesSerializer(self.scenario.parent.scenario_input_services).data
        initial_conditions_spatial = [
            get_image_data('State Classes', input_services['stateclass']),
            get_image_data('Stratum', input_services['stratum'])
        ]

        num_iterations = self.scenario.run_control.max_iteration
        num_timesteps = self.scenario.run_control.max_timestep
        timestep_units = 'Years'  # TODO - use JSON configuration from frontend?

        # Output images
        output_services = ScenarioOutputServicesSerializer(self.scenario.scenario_output_services).data
        spatial_outputs = []
        is_spatial = self.scenario.run_control.is_spatial

        if is_spatial:
            for it in range(1, num_iterations + 1):
                iteration = []
                for ts in range(1, num_timesteps + 1):
                    label = 'Iteration {ts} - Timestep ({units}) {ts}'.format(it=it, units=timestep_units, ts=ts)
                    url = output_services['stateclass'].replace('{it}', str(it)).replace('{t}', str(ts))
                    iteration.append(get_image_data(label, url))
                spatial_outputs.append(iteration)

        # Results (charts - SVG, output maps)
        column_charts = self.configuration.get('column_charts')
        stacked_charts = self.configuration.get('stacked_charts')
        charts = []
        for i, column in enumerate(column_charts):
            stacked = stacked_charts[i]
            charts.append({'name': column['vegtype'], 'column': column['svg'], 'stacked': stacked['svg']})

        # Detailed analysis breakdown from StateClass Summary Report
        stateclass_summary = StateClassSummaryReportSerializer(
            self.scenario.stateclass_summary_report
        ).data.get('results')


        return {
            'today': datetime.today(),
            'initial_veg_composition': initial_veg_composition,
            'initial_conditions_spatial': initial_conditions_spatial,
            'spatial_outputs': spatial_outputs,
            'charts': charts,
            'is_spatial': is_spatial,
            'library_name': self.scenario.project.library.name,
            'scale_image_data': scale_image_data,
            'north_image_data': north_image_data,
            'scenario_name': self.scenario.name,
            'num_iterations': num_iterations,
            'num_timesteps': num_timesteps,
            'timestep_units': timestep_units
        }

    def get_pdf_data(self):
        template = render_to_string('pdf/report.html', self.get_context())
        result = pdfkit.from_string(template, False, options=PDF_OPTIONS, configuration=PDFKIT_CONFIG)
        return result

    def request_zip_data(self):
        fd, filename = tempfile.mkstemp(prefix=DATASET_DOWNLOAD_DIR + "{}-".format(self.report_name), suffix='.zip')
        os.close(fd)
        with zipfile.ZipFile(filename, 'w') as zf:
            tif_files = [x for x in os.listdir(self.scenario.output_directory) if '.tif' in x]
            for f in tif_files:
                full_path = os.path.join(self.scenario.output_directory, f)
                zf.write(full_path, f)

        return {'filename': os.path.basename(filename)}
