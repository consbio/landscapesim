""" TODO - create ReportingUnits that can be used in any library. """

"""

The goal is to create a script that simply imports the necessary reporting unit data,
and associates it with a frontend such that any frontend can use the reporint unit.

The reason for
having a table as opposed to just a simple geojson file is because we will want to use the ID of the
reporting unit to link that reporting unit to a raster creation process for initial conditions. This was,
we can both query a library's large spatial extent for initial conditions for a specific area. This is
better handled by a database than the frontend user code.

"""



from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.gis.geos import LinearRing, Polygon
from django.contrib.gis.geos.collections import MultiPolygon
import fiona

from landscapesim.models import ReportingUnit

class Command(BaseCommand):
    help = 'Adds ReportingUnits to the database, using polygon data from a GeoJSON or Shapefile'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str)
        parser.add_argument('file', nargs=1, type=str)

    def handle(self, name, file, *args, **options):
        name = name[0]
        file = file[0]



