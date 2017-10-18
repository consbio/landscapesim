import os
from io import StringIO
from shutil import copyfileobj

from django.conf import settings

from landscapesim.io.consoles import STSimConsole
from landscapesim.io.utils import get_random_csv
from landscapesim.models import Scenario

EXE = getattr(settings, 'STSIM_EXE_PATH')
TEMP_DIR = getattr(settings, 'NC_TEMPORARY_FILE_LOCATION')


class Report:
    """ A class for handling report generation for landscapesim. """

    def __init__(self, configuration, zoom=None, tile_layers=None):
        self.configuration = configuration
        self.report_name = self.configuration['report_name']
        self.zoom = zoom
        self.tile_layers = tile_layers

    def get_csv_data(self):
        scenario = Scenario.objects.get(pk=self.configuration['scenario_id'])
        lib = scenario.project.library
        temp_file = get_random_csv(lib.tmp_file)
        STSimConsole(exe=EXE, lib_path=lib.file, orig_lib_path=lib.orig_file) \
            .generate_report(self.report_name, temp_file, scenario.sid)
        result = StringIO()
        with open(temp_file, 'r') as src:
            copyfileobj(src, result)
        os.remove(temp_file)
        return result
