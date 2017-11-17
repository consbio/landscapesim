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

import os
import csv

from landscapesim.models import Region, ReportingUnit
from landscapesim.serializers.regions import ReportingUnitSerializer

from rasterstats import zonal_stats
from rasterio.warp import transform_geom
import rasterio

from django.conf import settings


LANDFIRE_DIR = os.path.join(settings.BASE_DIR, 'materials', 'landfire')

# Disallow use of module if landfire support is not enabled.
if not os.path.exists(LANDFIRE_DIR):
    raise ImportError("LANDFIRE support is not enabled.")

BPS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130BPS.tif')
SCLASS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130SCLASS.tif')

with rasterio.open(BPS_TIF, 'r') as src:
    BPS_CRS = src.crs.get('init')

with rasterio.open(SCLASS_TIF, 'r') as src:
    SCLASS_CRS = src.crs.get('init')


BPS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_BPS.csv')
SCLASS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_SCLASS.csv')
SCLASS_SC_FILE = os.path.join(LANDFIRE_DIR, 'LANDFIRE_STSIM_mapping.csv')


def create_mapping(data, src: str, dest: str) -> dict:
    """ Create a dictionary between two types. """

    if isinstance(data, str):
        with open(data, 'r') as f:
            reader = csv.DictReader(f)
            raw_data = [r for r in reader]
    else:
        raw_data = data
    mapping = {int(row[src]): row[dest] for row in raw_data}
    return mapping, raw_data

BPS_MAPPING, _ = create_mapping(BPS_FILE, 'VALUE', 'BPS_MODEL')
SCLASS_MAPPING, _ = create_mapping(SCLASS_FILE, 'Value', 'Label')
SCLASS_A_MAPPING, data = create_mapping(SCLASS_SC_FILE, 'code', 'A')
SCLASS_B_MAPPING = create_mapping(data, 'code', 'B')
SCLASS_C_MAPPING = create_mapping(data, 'code', 'C')
SCLASS_D_MAPPING = create_mapping(data, 'code', 'D')
SCLASS_E_MAPPING = create_mapping(data, 'code', 'E')


# TODO - get stateclass mapping from Landfire stsim library



class Landfire:

    def __init__(self, stratum_path, stateclass_path, reporting_units_path=None):
        self.stratum_path = stratum_path
        self.stateclass_path = stateclass_path
        self.reporting_units_path = reporting_units_path

    def create_strata(self):
        pass

    def create_stateclasses(self):
        pass

    def create_reporting_units(self):
        pass

    def get_initial_conditions(self, reporting_unit: int):
        """ Retreive the initial conditions from a given reporting unit. """

        r = ReportingUnit.objects.get(pk=reporting_unit)
        feature = ReportingUnitSerializer(r).data
        zone_feature = feature.copy()
        zone_feature['geometry'] = transform_geom({'init': 'EPSG:4326'}, BPS_CRS, feature['geometry'])
        bps_stats = zonal_stats(
            zone_feature, BPS_TIF, stats=['count'], categorical=True, category_mapping=BPS_MAPPING, raster_out=True
        )

        # TODO - Get Stateclass stats, convert stateclass raster to bps_sc mapping


        return bps_stats

    def create_strata_raster(self):
        """ Create a stratum raster for importing into ST-Sim. """
        pass

    def create_stateclass_raster(self):
        """ Create a stateclass raster for importing into ST-Sim. """
        pass


    def _calculate_vegetation_statistics(self):
        pass

    def _calculate_stateclass_statistics(self):
        pass

