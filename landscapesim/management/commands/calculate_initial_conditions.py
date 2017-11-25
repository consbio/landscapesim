from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from landscapesim.contrib import find_library_module
from landscapesim.models import Library, Region, InitialConditionsNonSpatialDistribution


class Command(BaseCommand):

    help = 'Calculate the initial conditions across a region for a given library.'

    def add_arguments(self, parser):
        parser.add_argument('library_name', nargs=1, type=str)
        parser.add_argument('region_name', nargs=1, type=str)
        parser.add_argument('scenario_name', nargs=1, type=str)

    def handle(self, library_name, region_name, scenario_name, *args, **options):
        library_name = library_name[0]
        region_name = region_name[0]
        scenario_name = scenario_name[0]

        # Check for scenario existence
        lib = Library.objects.filter(name__exact=library_name)

        if not lib.exists():
            print('Library name {} does not exist in the database.'.format(library_name))
            return
        lib = lib.first()

        # Get this library's module. If there isn't one, then there is nothing to be done.
        mod = find_library_module(library_name)
        if mod is None:
            print('No importing module exists for this library. Check to make sure the library '
                  'you are calculating initial conditions for has a module located in '
                  'landscapesim.contrib')

        region = Region.objects.filter(name__exact=region_name)
        if not region.exists():
            print('Region name {} does not exist in the database.'.format(region_name))
            return
        region = region.first()

        # Check for scenario existence
        projects_with_scenario = lib.projects.filter(scenarios__name=scenario_name)
        if not projects_with_scenario.exists():
            print('Scenario name {} does not exist for Library {}.'.format(scenario_name, library_name))
            return
        scenario = projects_with_scenario.first().scenarios.get(name=scenario_name)

        # Now perform initial conditions calculations
        reporting_units = region.reporting_units.all()
        with transaction.atomic():
            for unit in tqdm(reporting_units):
                for initial_condition in mod.get_initial_conditions(scenario, unit):
                    InitialConditionsNonSpatialDistribution.objects.create(**initial_condition)
