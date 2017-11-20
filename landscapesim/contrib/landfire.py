"""
    Utilities for importing the LANDFIRE dataset into LandscapeSim.

    The ST-Sim model library uses the BPS_MODEL code as the name, which is not suitable for display.

    The goal here is to use the existing metadata to import the appropriate name for the model name, but leave the
    model library untouched.

    BpS_CODE --> Library Model
    BpS_Name --> Descriptive Name
    VegetationType --> Vegetation classification (could be used to filter down)
    Class<A-E>Cover --> Cover Type
    Class<A-E>Struct --> Structural Stage

    State Classes are defined with a unique combination of Cover Type and Structural Stage. The ST-Sim model library
    defines 27 possible state classes, of which a maximum of 5 are used for any vegetation type.
"""

import csv
import os

import numpy
import rasterio
from django.conf import settings
from rasterio.warp import transform_geom
from rasterstats import zonal_stats


from landscapesim.importers import ProjectImporter, ScenarioImporter, ReportImporter

from landscapesim.models import ReportingUnit
from landscapesim.serializers.regions import ReportingUnitSerializer


# Unique identifier for this contributor module.
LIBRARY_NAME = 'LANDFIRE'

# Data file paths
LANDFIRE_DIR = os.path.join(settings.BASE_DIR, 'materials', 'landfire')
BPS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130BPS.tif')
SCLASS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130SCLASS.tif')
BPS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_BPS.csv')
SCLASS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_SCLASS.csv')
BPS_SC_FILE = os.path.join(LANDFIRE_DIR, 'LANDFIRE_BPS_SCLASS_mapping.csv')
SCLASS_ID_FILE = os.path.join(LANDFIRE_DIR, 'LANDFIRE_STSIM_SCLASS_ID_mapping.csv')

# Disallow use of module if Landfire data is not present.
all_data_exist = all(os.path.exists(p) for p in (LANDFIRE_DIR, BPS_TIF, SCLASS_TIF, BPS_TIF, BPS_FILE, SCLASS_FILE,
                                            BPS_SC_FILE, SCLASS_ID_FILE))

if not all_data_exist:
    raise ImportError(
        "LANDFIRE support is not enabled."
        "Check to see that all necessary files exist in <project_root>/materials/landfire"
    )

with rasterio.open(BPS_TIF, 'r') as src:
    BPS_CRS = src.crs.get('init')

with rasterio.open(SCLASS_TIF, 'r') as src:
    SCLASS_CRS = src.crs.get('init')


def create_mapping(path, src, dest, key_type=None) -> dict:
    """ Create a dictionary between two attributes. """
    if key_type is None:
        key_type = int

    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        raw_data = [r for r in reader]
        mapping = {key_type(row[src]): row[dest] for row in raw_data}
    return mapping


BPS_MAPPING = create_mapping(BPS_FILE, 'VALUE', 'BPS_MODEL')
BPS_NAMES = create_mapping(BPS_FILE, 'VALUE', 'BPS_NAME')
SCLASS_MAPPING= create_mapping(SCLASS_FILE, 'Value', 'Label')
SCLASS_A_MAPPING = create_mapping(BPS_SC_FILE, 'code', 'A')
SCLASS_B_MAPPING = create_mapping(BPS_SC_FILE, 'code', 'B')
SCLASS_C_MAPPING = create_mapping(BPS_SC_FILE, 'code', 'C')
SCLASS_D_MAPPING = create_mapping(BPS_SC_FILE, 'code', 'D')
SCLASS_E_MAPPING = create_mapping(BPS_SC_FILE, 'code', 'E')
SCLASS_ID_MAPPING = create_mapping(SCLASS_ID_FILE, 'Name', 'ID', str)
SCLASS_ALL_MAPPINGS = (
    ('A', SCLASS_A_MAPPING),
    ('B', SCLASS_B_MAPPING),
    ('C', SCLASS_C_MAPPING),
    ('D', SCLASS_D_MAPPING),
    ('E', SCLASS_E_MAPPING)
)


class LandfireProjectImporter(ProjectImporter):
    pass


class LandfireScenarioImporter(ScenarioImporter):
    pass


class LandfireReportImporter(ReportImporter):
    pass


PROJECT_IMPORTER_CLASS = LandfireProjectImporter
SCENARIO_IMPORTER_CLASS = LandfireScenarioImporter
REPORT_IMPORTER_CLASS = LandfireReportImporter


def get_initial_conditions(reporting_unit):
    """ Retreive the initial conditions from a given reporting unit. """

    r = ReportingUnit.objects.get(pk=reporting_unit)
    feature = ReportingUnitSerializer(r).data
    zone_feature = feature.copy()
    zone_feature['geometry'] = transform_geom({'init': 'EPSG:4326'}, BPS_CRS, feature['geometry'])
    bps_stats = zonal_stats(
        zone_feature, BPS_TIF, stats=[], categorical=True, raster_out=True
    )[0]
    bps_raster = bps_stats.get('mini_raster_array')

    sclass_stats = zonal_stats(
        zone_feature, SCLASS_TIF, stats=[], raster_out=True
    )[0]
    sclass_raster = sclass_stats.get('mini_raster_array')

    # The count of the area that *is not* masked, i.e. the count within the reporting unit
    count = bps_raster.count()

    initial_conditions = []
    for value in bps_stats:
        if value in BPS_MAPPING:
            # Calculate state class percentages where the vegetation occurs
            try:
                bps_model_code = int(BPS_MAPPING[value])
            except ValueError:
                continue

            bps_model_name = BPS_NAMES[value]
            stateclass_names = []
            for sclass_type, lookup in SCLASS_ALL_MAPPINGS:
                if bps_model_code in lookup:
                    name = lookup[bps_model_code]
                    if name:
                        stateclass_names.append((sclass_type, name))

            sclass_locations = sclass_raster[numpy.where(bps_raster == value)]
            sclass_keys_found, sclass_counts = numpy.unique(sclass_locations, return_counts=True)
            for i, name_tuple in enumerate(stateclass_names):
                name, stateclass = name_tuple
                if i not in sclass_keys_found:
                    relative_amount = 0.0
                else:
                    sclass_idx = list(sclass_keys_found).index(i)
                    relative_amount = sclass_counts[sclass_idx] / count

                initial_conditions.append({
                    'scenario': None,
                    'pk': None,
                    'relative_amount': relative_amount,
                    'stratum': bps_model_name,              # TODO - get foreign key, use name as lookup?
                    'stateclass': stateclass                # TODO - get foreign key, use sclass name as lookup?
                })

    return initial_conditions

def create_strata_raster():
    """ Create a stratum raster for importing into ST-Sim. """
    pass

def create_stateclass_raster():
    """ Create a stateclass raster for importing into ST-Sim. """
    pass


'''
def create_strata():
    pass

def create_stateclasses():
    pass
'''




