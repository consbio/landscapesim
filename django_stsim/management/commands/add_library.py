"""
    Here is where we will add management commands to add libraries,
    or to update a given library with new variables

    NOTE - the libraries should be sitting in the directory root.
"""

import os
import csv
from shutil import copyfile
from django.core.management.base import BaseCommand
from django_stsim.models import Library, Project, Scenario, Stratum,\
    StateClass, TransitionType, TransitionGroup, TransitionTypeGroup, Transition
from django.conf import settings
from django.db.models import Q

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
        tmp_file = file.split('.ssim')[0] + '_tmp.csv'

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

        # Console works, now create library
        library = Library.objects.create(name=name, file=file, orig_file=orig_file, tmp_file=tmp_file)

        projects = console.list_projects()
        all_scenarios = console.list_scenario_names()
        result_scenarios = console.list_scenario_names(results_only=True)
        orig_scenarios = [s for s in all_scenarios if s not in result_scenarios]

        for pid in projects.keys():
            proj_name = projects[pid]
            project = Project.objects.create(library=library, name=proj_name, pid=int(pid))
            print('Created project {} with pid {}'.format(project.name, project.pid))

            for s in orig_scenarios:
                if s['pid'] == pid:
                    Scenario.objects.create(
                        project=project,
                        name=s['name'],
                        sid=int(s['sid'])
                    )
                    print('Created scenario {}.'.format(s['sid']))

            for s in result_scenarios:
                if s['pid'] == pid:
                    Scenario.objects.create(
                        project=project,
                        name=s['name'],
                        sid=int(s['sid']),
                        is_result=True
                    )
                    print('Created scenario {}.'.format(s['sid']))

            # import strata
            strata = console.export_vegtype_definitions(pid, tmp_file)
            for stratum in strata.keys():
                s = strata[stratum]
                Stratum.objects.create(
                    stratum_id=s['ID'],
                    project=project,
                    name=stratum,
                    color=s['Color'],
                    description=s['Description']
                    )
            print('Imported strata for project {}.'.format(project.name))

            # import stateclasses
            stateclasses = console.export_stateclass_definitions(pid, tmp_file)
            for sc in stateclasses.keys():
                s = stateclasses[sc]
                StateClass.objects.create(
                    stateclass_id=s['ID'],
                    project=project,
                    name=sc,
                    color=s['Color'],
                    description=s['Description'],
                    development=s['Development Stage'],
                    structure=s['Structural Stage']
                    )
            print('Imported state classes for project {}.'.format(project.name))

            # import transition types   # TODO - add stsimpy methods for adding the below
            console.export_sheet('STSim_TransitionType', tmp_file, pid=pid, overwrite=True, orig=True)
            with open(tmp_file, 'r') as sheet:
                reader = csv.DictReader(sheet)
                for row in reader:
                    TransitionType.objects.create(
                        project=project,
                        #transition_type_id=int(row['ID']) if len(row['ID']) > 0 else None,  # TODO - decide what to do with non-existent IDS
                        name=row['Name'],
                        color=row['Color'],
                        description=row['Description']
                    )
            print('Imported transition types for project {}.'.format(project.name))

            # import transition groups
            console.export_sheet('STSim_TransitionGroup', tmp_file, pid=pid, overwrite=True, orig=True)
            with open(tmp_file, 'r') as sheet:
                reader = csv.DictReader(sheet)
                for row in reader:
                    TransitionGroup.objects.create(
                        project=project,
                        name=row['Name'],
                        description=row['Description']
                    )
            print('Imported transition groups for project {}.'.format(project.name))

            # map transition groups to transition types
            console.export_sheet('STSim_TransitionTypeGroup', tmp_file, pid=pid, overwrite=True, orig=True)
            with open(tmp_file, 'r') as sheet:
                reader = csv.DictReader(sheet)
                for row in reader:
                    grp = TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'], project=project).first()
                    ttype = TransitionType.objects.filter(name__exact=row['TransitionTypeID'], project=project).first()
                    TransitionTypeGroup.objects.create(
                        project=project,
                        transition_type=ttype,
                        transition_group=grp,
                        is_primary=row['IsPrimary']
                    )
            print('Imported transition type groups for project {}.'.format(project.name))

            # Now import any scenario-specific information we want to capture
            scenarios = Scenario.objects.filter(project=project)
            for s in scenarios:
                # import initial probabilistic transition probabilities
                console.export_sheet('STSim_Transition', tmp_file, sid=s.sid, overwrite=True, orig=True)
                with open(tmp_file, 'r') as sheet:
                    reader = csv.DictReader(sheet)
                    for row in reader:
                        if len(row['StratumIDDest']) > 0:
                            Transition.objects.create(
                                scenario=s,
                                stratum_src=Stratum.objects.filter(name__exact=row['StratumIDSource'],
                                                                   project=project).first(),
                                stratum_dest=Stratum.objects.filter(name__exact=row['StratumIDDest'],
                                                                    project=project).first(),
                                stateclass_src=StateClass.objects.filter(name__exact=row['StateClassIDSource'],
                                                                         project=project).first(),
                                stateclass_dest=StateClass.objects.filter(name__exact=row['StateClassIDDest'],
                                                                          project=project).first(),
                                transition_type=TransitionType.objects.filter(name__exact=row['TransitionTypeID'],
                                                                              project=project).first(),
                                probability=float(row['Probability']),
                                age_reset=row['AgeReset']
                            )
                        else:
                            Transition.objects.create(  # omit stratum_dest, no change in stratum per timestep
                                scenario=s,
                                stratum_src=Stratum.objects.filter(name__exact=row['StratumIDSource'],
                                                                   project=project).first(),
                                stateclass_src=StateClass.objects.filter(name__exact=row['StateClassIDSource'],
                                                                         project=project).first(),
                                stateclass_dest=StateClass.objects.filter(name__exact=row['StateClassIDDest'],
                                                                          project=project).first(),
                                transition_type=TransitionType.objects.filter(name__exact=row['TransitionTypeID'],
                                                                              project=project).first(),
                                probability=float(row['Probability']),
                                age_reset=row['AgeReset']
                            )
                print('Imported transition probabilities for scenario {} from project {}'.format(s.sid, project.name))
            print("Project {} for library {} successfully imported.".format(project.name, name))
        print("{} successfully added to django_stsim.".format(name))
