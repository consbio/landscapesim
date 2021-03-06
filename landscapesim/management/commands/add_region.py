import os

import fiona
from django.conf import settings
from django.contrib.gis.geos import LinearRing, Polygon, MultiPolygon
from django.core.management.base import BaseCommand
from django.db import transaction

from landscapesim.models import Region, ReportingUnit

REGIONS_DIR = os.path.join(settings.BASE_DIR, 'materials', 'regions')


class Command(BaseCommand):
    help = 'Adds ReportingUnits to the database, using polygon data from a GeoJSON or Shapefile'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str)
        parser.add_argument('file', nargs=1, type=str)

    def handle(self, name, file, *args, **options):
        name = name[0]
        file = file[0]

        if Region.objects.filter(name__iexact=name).exists():
            message = (
                'WARNING: This will replace an existing region with the same name: {}. Do you want to continue? [y/n]'
            ).format(name)
            if input(message).lower() not in {'y', 'yes'}:
                return
            else:
                Region.objects.filter(name__iexact=name).delete()

        path = os.path.join(REGIONS_DIR, file)
        if not os.path.exists(path):
            raise ValueError(
                "The file {} could not be found. Ensure that it is located with the regions directory "
                "(../materials/regions/<file>).".format(file)
            )

        region = Region.objects.create(name=name, path=path)
        with fiona.open(path, 'r') as shp:
            with transaction.atomic():
                for i, feature in enumerate(shp):
                    properties = feature['properties']
                    geometry = feature['geometry']
                    geom_type = geometry.get('type')
                    if geom_type == 'MultiPolygon':
                        polygon = MultiPolygon(
                            *[Polygon(*[LinearRing(x) for x in g]) for g in geometry['coordinates']]
                        )
                    elif geom_type == 'Polygon':
                        polygon = Polygon(*[LinearRing(x) for x in geometry['coordinates']])
                    else:
                        continue    # No support for non-polygon geometries

                    feature_name = properties.get('NAME')
                    ReportingUnit.objects.create(
                        region=region, unit_id=i, name=feature_name, polygon=polygon
                    )
