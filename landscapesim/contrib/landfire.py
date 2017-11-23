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
import json
import os

import numpy
import rasterio
from django.conf import settings
from rasterio.warp import transform_geom
from rasterstats import zonal_stats

from landscapesim.importers import ProjectImporter
from landscapesim.importers.project import STRATUM
from landscapesim.models import Stratum, StateClass

# Unique identifier for this contributor module's library name.
LIBRARY_NAME = 'LANDFIRE'

# Data file paths
LANDFIRE_DIR = os.path.join(settings.BASE_DIR, 'materials', 'landfire')
BPS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130BPS.tif')
SCLASS_TIF = os.path.join(LANDFIRE_DIR, 'LANDFIRE_130SCLASS.tif')
BPS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_BPS.csv')
SCLASS_FILE = os.path.join(LANDFIRE_DIR, 'US_130_SCLASS.csv')
BPS_SC_FILE = os.path.join(LANDFIRE_DIR, 'LANDFIRE_BPS_SCLASS_mapping.csv')
SCLASS_ID_FILE = os.path.join(LANDFIRE_DIR, 'LANDFIRE_STSIM_SCLASS_ID_mapping.csv')

# Disallow use of module if data is not present.
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
    """ A custom Project importer that uses more descriptive names than those stored in the SyncroSim database. """

    def _extract_sheet_alternative_names(self, sheet_config, mapping):
        sheet_name, model, sheet_map, type_map = sheet_config
        self.console.export_sheet(sheet_name, self.temp_file, **self.sheet_kwargs)
        with open(self.temp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            data = [r for r in reader]
            for row in data:
                mapped_row = self.map_row(row, sheet_map, type_map)
                row_id = mapped_row['stratum_id']
                descriptive_name = mapping[row_id]
                mapped_row['description'] = descriptive_name
                instance_data = {**self.import_kwargs, **mapped_row}
                model.objects.create(**instance_data)
        print("Imported {} (with customized LANDFIRE descriptions)".format(sheet_name))
        self._cleanup_temp_file()
    
    def import_stratum(self):
        self._extract_sheet_alternative_names(STRATUM, BPS_NAMES)


# Register the importer classes so that LandscapeSim picks them up
PROJECT_IMPORTER_CLASS = LandfireProjectImporter


def get_initial_conditions(scenario, reporting_unit):
    """ Retreive the initial conditions from a given reporting unit. """

    # Transform the geometry to fit the projection
    geom = transform_geom({'init': 'EPSG:4326'}, BPS_CRS, json.loads(reporting_unit.polygon.json))
    feature = dict(geometry=geom, type='Feature', properties={})

    # Collect zonal stats from rasters
    bps_stats = zonal_stats(
        [feature], BPS_TIF, stats=[], categorical=True, raster_out=True
    )[0]
    bps_raster = bps_stats.get('mini_raster_array')

    sclass_stats = zonal_stats(
        [feature], SCLASS_TIF, stats=[], raster_out=True
    )[0]
    sclass_raster = sclass_stats.get('mini_raster_array')

    # The count of the area that *is not* masked, i.e. the count within the reporting unit
    count = bps_raster.count()

    # Yield each set of initial conditions
    for value in bps_stats:
        if value in BPS_MAPPING:

            # If the raster value is not found, skip it
            try:
                bps_model_code = int(BPS_MAPPING[value])
            except ValueError:
                continue

            stratum = Stratum.objects.filter(name=BPS_MAPPING[value], project=scenario.project)

            # Not all BpS vegetation types have a STM model. Since we can't model them, we skip them.
            if not stratum:
                continue
            stratum = stratum.first()

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
                stateclass = StateClass.objects.filter(name=stateclass, project=scenario.project).first()

                yield {
                    'scenario': scenario,
                    'relative_amount': relative_amount,
                    'stratum': stratum,
                    'stateclass': stateclass,
                    'reporting_unit': reporting_unit
                }


def create_strata_raster():
    """ Create a stratum raster for importing into ST-Sim. """
    pass


def create_stateclass_raster():
    """ Create a stateclass raster for importing into ST-Sim. """
    pass
