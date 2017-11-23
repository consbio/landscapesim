import json
import os
import re
import tempfile
import zipfile
from base64 import b64encode
from datetime import datetime
from io import StringIO, BytesIO
from shutil import copyfileobj
from statistics import median

import pdfkit
from django.conf import settings
from django.db.models import Min, Max, Sum
from django.template.loader import render_to_string
from geopy.distance import vincenty
from ncdjango.geoimage import image_to_world
from pyproj import Proj, transform

from landscapesim.common.consoles import STSimConsole
from landscapesim.common.utils import get_random_csv
from landscapesim.mapimage import MapImage
from landscapesim.models import Scenario, StateClassSummaryReportRow
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
STSIM_MULTIPLIER_DIR = getattr(settings, 'STSIM_MULTIPLIER_DIR')

MERCATOR = Proj(init='epsg:3857')
WGS84 = Proj(init='epsg:4326')


class Report:
    """ A class for handling report generation for landscapesim. """

    def __init__(self, report_name, configuration):
        self.configuration = configuration
        self.scenario = Scenario.objects.get(pk=self.configuration['scenario_id'])
        self.report_name = report_name

    @staticmethod
    def _filter_uuid(path):
        # Remove uuid values from multiplier filenames
        regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
        parts = path.split('_')

        match = False
        for p in parts:
            match = bool(regex.match(p))
            if match:
                break

        result = path
        if match:
            result = '_'.join(path.split('_')[1:])
        return result

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

        # Query all related data to this model run
        strata = self.scenario.project.strata.all()
        terms = self.scenario.project.terminology       # TODO - use terminology to specify units for timesteps!

        # TODO - Get author and description from a model description table, and use it in the frontend
        library_author = self.configuration.get('author', "Mike O'Donnell")
        library_description = self.configuration.get('description', "A sample ST-Sim library developed for a semi-arid shrub-steppe ecosystem in southwest Idaho (Castle Creek).")
        library_date = self.configuration.get('date', 2015)

        # Initial vegetation tables
        nonspatial_distributions = self.scenario.initial_conditions_nonspatial_distributions
        initial_veg_composition = []
        for stratum in strata:
            name = stratum.name
            stateclasses = nonspatial_distributions.filter(stratum=stratum).values('stateclass__name', 'relative_amount')
            proportion_of_landscape = nonspatial_distributions.filter(stratum=stratum).aggregate(sum=Sum('relative_amount'))['sum']
            for stateclass in stateclasses:
                relative_amount = stateclass['relative_amount']
                stateclass['proportion_of_stratum'] = round(100 * relative_amount / proportion_of_landscape, 2)
                stateclass['relative_amount'] = round(relative_amount, 2)
            initial_veg_composition.append({
                'name': name,
                'stateclasses': stateclasses,
                'proportion_of_landscape': round(proportion_of_landscape, 2)
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

        def get_legend(service_url, is_output=False):
            split_idx = 5 if is_output else 4
            legend_url = '/'.join(service_url.split('/')[:split_idx] + ['legend'])
            return map_maker.get_legend(legend_url)

        def get_scale(to_world, image_height):
            scale_bar_x = 38
            scale_bar_y = image_height - 15
            scale_bar_start = transform(MERCATOR, WGS84, *to_world(scale_bar_x, scale_bar_y))
            scale_bar_end = transform(MERCATOR, WGS84, *to_world(scale_bar_x + 96, scale_bar_y))
            return '{} mi'.format(round(vincenty(scale_bar_start, scale_bar_end).miles, 1))

        def get_map_context(label, name, service, is_output=False, iteration=None, timestep=None, legend=None):

            service_url = service[name]
            if is_output:
                service_url = service_url.replace('{it}', str(iteration)).replace('{t}', str(timestep))

            image_data, bbox = map_maker.get_image(service_url)
            to_world = image_to_world(bbox, image_data.size)
            bbox = bbox.project(WGS84, edge_points=0)

            image_handle = BytesIO()
            image_data.save(image_handle, 'png')

            scale = get_scale(to_world, image_data.size[1])
            legend_data = get_legend(service_url, is_output) if legend is None else legend

            return {
                'label': label,
                'image_data': b64encode(image_handle.getvalue()),
                'north': format_y_coord(bbox.ymax),
                'east': format_x_coord(bbox.xmax),
                'west': format_x_coord(bbox.xmin),
                'south': format_y_coord(bbox.ymin),
                'scale': scale,
                'legend': legend_data
            }

        # Input images
        input_services = ScenarioInputServicesSerializer(self.scenario.parent.scenario_input_services).data
        initial_conditions_spatial = [
            get_map_context('Stratum', 'stratum', input_services),
            get_map_context('State Classes', 'stateclass', input_services)
        ]

        stratum_legend, stateclass_legend = [x.get('legend') for x in initial_conditions_spatial]
        basic_map_config = {key: initial_conditions_spatial[0][key] for key in ('west', 'south', 'east', 'north')}

        num_iterations = self.scenario.run_control.max_iteration
        num_timesteps = self.scenario.run_control.max_timestep
        timestep_units = 'Years'                    # TODO - use JSON configuration from frontend?
        timestep_interval = self.configuration.get('timestep_interval', 1)

        def format_timestep_label(it, ts):
            return 'Iteration {it} - Timestep ({units}) {ts}'.format(it=it, units=timestep_units, ts=ts)

        # Output images
        output_services = ScenarioOutputServicesSerializer(self.scenario.scenario_output_services).data
        spatial_outputs = []
        is_spatial = self.scenario.run_control.is_spatial
        if is_spatial:
            for it in range(1, num_iterations + 1):
                iteration = []
                for ts in range(1, num_timesteps + 1):
                    
                    if ts % timestep_interval != 0:
                        continue

                    iteration.append(get_map_context(
                        format_timestep_label(it, ts), 'stateclass', output_services, is_output=True, iteration=it,
                        timestep=ts, legend=stateclass_legend
                    ))

                spatial_outputs.append(iteration)

        def get_management_action_map(tsm):
            geojson_file = os.path.join(
                STSIM_MULTIPLIER_DIR, tsm.transition_multiplier_file_name
            ).replace('.tif', '.json')

            with open(geojson_file, 'r') as f:
                polygons = json.load(f)

            transition_group = tsm.transition_group.name
            timestep = int(tsm.transition_multiplier_file_name.split('_')[-1].split('.')[0])
            label = '{} performed on {} {}'.format(transition_group, timestep_units, timestep)
            image_data, bbox = map_maker.get_polygon_image(polygons)
            to_world = image_to_world(bbox, image_data.size)

            image_handle = BytesIO()
            image_data.save(image_handle, 'png')

            return {
                'label': label,
                'image_data': b64encode(image_handle.getvalue()),
                'scale': get_scale(to_world, image_data.size[1]),
                **basic_map_config
            }

        # Management actions list
        has_management_actions = False
        tsms = self.scenario.transition_spatial_multipliers.all()
        management_actions = []
        if is_spatial:
            management_actions = [get_management_action_map(x) for x in tsms]
            has_management_actions = bool(management_actions)

        # Results (charts - SVG, output maps)
        column_charts = self.configuration.get('column_charts')
        stacked_charts = self.configuration.get('stacked_charts')
        charts = []
        
        # Detailed analysis breakdown from StateClass Summary Report
        output_data = StateClassSummaryReportRow.objects.filter(report=self.scenario.stateclass_summary_report)
        stateclasses = self.scenario.project.stateclasses.all()

        for i, column in enumerate(column_charts):
            stacked = stacked_charts[i]

            name = column['vegtype']
            stratum = strata.get(name=name)

            # All output data for the final timestep and all iterations
            veg_output_data = output_data.filter(stratum=stratum)
            column_output_context = []
            for stateclass in stateclasses:
                rows = veg_output_data.filter(stateclass=stateclass, timestep=num_timesteps)
                if rows:
                    column_data = {
                        'name': stateclass.name,
                        'max': round(100 * rows.aggregate(max=Max('proportion_of_landscape'))['max'], 2),
                        'min': round(100 * rows.aggregate(min=Min('proportion_of_landscape'))['min'], 2),
                        'median': round(100 * median(x[0] for x in rows.values_list('proportion_of_landscape')), 2)
                    }
                    column_output_context.append(column_data)
            
            # TODO - how to show this for each iteration? Just use a separate chart for now?
            stacked_output_context = []
            filtered_timesteps = [i for i in range(0, num_timesteps + 1) if i % timestep_interval == 0]
            for stateclass in stateclasses:
                stateclass_data = veg_output_data.filter(iteration=1, stateclass=stateclass)
                if stateclass_data:
                    row_values = [
                        x for i, x in enumerate(stateclass_data.order_by('timestep')
                                                .values('proportion_of_landscape', 'timestep'))
                        if i in filtered_timesteps
                    ]
                    for i, x in enumerate(row_values):
                        value = row_values[i]['proportion_of_landscape']
                        row_values[i]['percent'] = round(value * 100, 2) if value > 0.0 else '--'

                    # Handle case where no measureable value was found at a given timestep, and fill with 0.0
                    if len(row_values) != len(filtered_timesteps):
                        # TODO - solve the more general case, for now the below line is a temporary fix
                        row_values.insert(0, {'timestep': 0, 'proportion_of_landscape': 0.0, 'percent': '--'})

                    stacked_output_context.append({
                        'name': stateclass.name,
                        'values': row_values
                    })

            charts.append({
                'name': name,
                'column': column['svg'],
                'stacked': stacked['svg'],
                'column_values': column_output_context,
                'stacked_values': stacked_output_context,
                'filtered_timesteps': filtered_timesteps
                })

        return {
            'today': datetime.today(),
            'initial_veg_composition': initial_veg_composition,
            'initial_conditions_spatial': initial_conditions_spatial,
            'timestep_interval': timestep_interval,
            'spatial_outputs': spatial_outputs,
            'charts': charts,
            'is_spatial': is_spatial,
            'iteration_is_one': num_iterations == 1,
            'has_management_actions': has_management_actions,
            'management_actions': management_actions,
            'library_name': self.scenario.project.library.name,
            'library_author': library_author,
            'library_description': library_description,
            'library_date': library_date,
            'scale_image_data': scale_image_data,
            'north_image_data': north_image_data,
            'scenario_name': self.scenario.name,
            'num_iterations': num_iterations,
            'num_timesteps': num_timesteps,
            'timestep_units': timestep_units
        }

    def request_pdf_data(self):
        template = render_to_string('pdf/report.html', self.get_context())
        fd, filename = tempfile.mkstemp(prefix=DATASET_DOWNLOAD_DIR + "{}-".format(self.report_name), suffix='.pdf')
        os.close(fd)
        pdfkit.from_string(template, filename, options=PDF_OPTIONS, configuration=PDFKIT_CONFIG)
        return {'filename': os.path.basename(filename), 'actual_name': 'overview.pdf'}

    def request_zip_data(self):
        fd, filename = tempfile.mkstemp(prefix=DATASET_DOWNLOAD_DIR + "{}-".format(self.report_name), suffix='.zip')
        os.close(fd)
        data_dirs = (self.scenario.output_directory, self.scenario.multiplier_directory)

        # Create the archive
        with zipfile.ZipFile(filename, 'w') as zf:
            directories = [x for x in data_dirs if os.path.exists(x)]
            for d in directories:
                tif_files = [x for x in os.listdir(d) if x.split('.')[-1] == 'tif']
                for f in tif_files:
                    full_path = os.path.join(d, f)
                    zf.write(full_path, self._filter_uuid(f))

        return {'filename': os.path.basename(filename), 'actual_name': 'spatial-data.zip'}
