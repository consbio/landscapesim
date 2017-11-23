"""


LIBRARY_NAME -> str
get_initial_conditions(reporting_unit: int) -> List[InitialConditionNonSpatialDistributionSerializer]
create_spatial_initial_conditions
"""

import os
import sys
from importlib.util import spec_from_file_location, module_from_spec

from landscapesim.importers import ProjectImporter, ScenarioImporter, ReportImporter

REGISTERED_LIBRARY_PROCESSORS = {}


def _load_library_processors():
    """ Find and import all possible contrib modules to facilitate project, scenario and report imports. """

    # Dont load double underscored filenames
    possible_module_paths = [(os.path.join(os.path.dirname(__file__), x), x)
                             for x in os.listdir(os.path.dirname(__file__)) if '__' not in x]

    # Now try loading each module
    for full_path, file_name in possible_module_paths:
        name = file_name.split('.')[-2]
        module_name = 'landscapesim.contrib.{}'.format(name)
        try:
            spec = spec_from_file_location(module_name, full_path)
            mod = module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            REGISTERED_LIBRARY_PROCESSORS[name] = module_name
        except ImportError:
            print("Could not load {} at path {}.".format(name, full_path))


# Now find available library modules
_load_library_processors()


def find_library_module(library_name):
    """ Find a contrib module based on the STSim library name. """
    for name, mod_name in REGISTERED_LIBRARY_PROCESSORS.items():
        mod = sys.modules[mod_name]
        if getattr(mod, 'LIBRARY_NAME') == library_name:
            return mod
    return None


def get_project_importer_cls(library_name):
    """ Return a ProjectImporter class to handle importing a specific library's project information. """
    lib_module = find_library_module(library_name)
    if lib_module:
        try:
            return lib_module.PROJECT_IMPORTER_CLASS
        except AttributeError:
            pass
    return ProjectImporter


def get_scenario_importer_cls(library_name):
    """ Return a ScenarioImporter class to handle importing a specific library's scenario information. """
    lib_module = find_library_module(library_name)
    if lib_module:
        try:
            return lib_module.SCENARIO_IMPORTER_CLASS
        except AttributeError:
            pass
    return ScenarioImporter


def get_report_importer_cls(library_name):
    """ Return a ReportImporter class to handle importing a specific library's report information. """
    lib_module = find_library_module(library_name)
    if lib_module:
        try:
            return lib_module.REPORT_IMPORTER_CLASS
        except AttributeError:
            pass
    return ReportImporter


def get_initial_conditions(library_name, scenario, reporting_unit=None):
    lib_module = find_library_module(library_name)
    if lib_module and reporting_unit is not None:
        return lib_module.get_initial_conditions(scenario, reporting_unit)
    return None
