"""
    Utilities for importing the LANDFIRE dataset into LandscapeSim.
"""

import os

from django.conf import settings

"""
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

To create the initial conditions

"""


# Disallow use of module if landfire support is not enabled.
if not os.path.exists(os.path.join(settings.BASE_DIR, 'materials', 'landfire')):
    raise ImportError("LANDFIRE support is not enabled.")


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

    def create_initial_conditions(self, strata, stateclass, reporting_unit):
        """ Retreive the initial conditions from a given reporting unit. """
        pass


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

