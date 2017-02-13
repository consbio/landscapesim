"""
    Here is where we will add management commands to add libraries,
    or to update a given library with new variables

    NOTE - the libraries should be sitting in the directory root.
"""

import glob
import os
from shutil import copyfile
from django.core.management.base import BaseCommand
from django.db import transaction
from django_stsim.models import Library, Project, Scenario

from django.conf import settings
from stsimpy import STSimConsole

from pprint import pprint

exe = settings.STSIM_EXE_PATH

class Command(BaseCommand):

    help = 'Registers a .ssim library based on the file path.'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str)
        parser.add_argument('file', nargs=1, type=str)

    def handle(self, name, file, *args, **options):
        file = file[0]
        name = name[0]
        orig_file = file.split('.ssim')[0] + '_orig.ssim'

        if Library.objects.filter(file__iexact=file).exists():
            message = (
                'WARNING: This will override an existing library with the same filename: {}. '
                'Do you want to continue?'.format(file)
            )
            if input(message).lower() not in {'y', 'yes'}:
                return

        if not os.path.exists(orig_file):
            message = ('A copy of the library does not exist. Create one now or cancel?')
            if input(message).lower() not in {'y', 'yes'}:
                return
            else:
                copyfile(file, orig_file)


        console = STSimConsole(lib_path=file, orig_lib_path=orig_file, exe=exe)


        with transaction.atomic():
            library = Library.objects.create(name=name, file=file, orig_file=orig_file)


        projects = console.list_projects()
        all_scenarios = console.list_scenario_names()
        result_scenarios = console.list_scenario_names(results_only=True)
        orig_scenarios = [s for s in all_scenarios if s not in result_scenarios]

        print('\nImporting projects...')
        pprint(projects)
        print('Importing original scenarios...')
        pprint(orig_scenarios)
        print('\nImporting result scenarios...')
        pprint(result_scenarios)

        for pid in projects.keys():
            proj_name = projects[pid]
            project = Project.objects.create(library=library, name=proj_name, pid=int(pid))

            for s in orig_scenarios:
                if s['pid'] == pid:
                    with transaction.atomic():
                        Scenario.objects.create(
                            project=project,
                            name=s['name'],
                            sid=int(s['sid'])
                        )

            for s in result_scenarios:
                if s['pid'] == pid:
                    with transaction.atomic():
                        Scenario.objects.create(
                            project=project,
                            name=s['name'],
                            sid=int(s['sid']),
                            is_result=True
                        )


