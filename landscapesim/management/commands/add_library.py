"""
    add_library: Imports an existing .ssim library into landscapesim.
"""
import os
from shutil import copyfile
from landscapesim.models import Library, Project, Scenario
from landscapesim.io.utils import process_scenario_inputs, process_project_definitions
from landscapesim.io.reports import create_transition_summary, create_transition_sc_summary, create_stateclass_summary
from landscapesim.io.consoles import STSimConsole
from django.core.management.base import BaseCommand
from django.conf import settings


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
            print('The library located at {} already exists in the database.')
            return

        if not os.path.exists(orig_file):
            message = 'A copy of the library does not exist. Create one now or cancel? '
            if input(message).lower() not in {'y', 'yes'}:
                print("Abort - Cannot continue without replicating the library values.")
                return
            else:
                copyfile(file, orig_file)

        console = STSimConsole(lib_path=file, orig_lib_path=orig_file, exe=settings.STSIM_EXE_PATH)

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

            # Create original scenarios
            for s in orig_scenarios:
                if s['pid'] == pid:
                    Scenario.objects.create(
                        project=project,
                        name=s['name'],
                        sid=int(s['sid'])
                    )
                    print('Created scenario {}.'.format(s['sid']))

            # Create result scenarios
            for s in result_scenarios:
                if s['pid'] == pid:
                    Scenario.objects.create(
                        project=project,
                        name=s['name'],
                        sid=int(s['sid']),
                        is_result=True
                    )
                    print('Created scenario {}.'.format(s['sid']))

            # Import all project definitions
            process_project_definitions(console, project)

            # Now import any scenario-specific information we want to capture
            scenarios = Scenario.objects.filter(project=project)
            for s in scenarios:

                # Import scenario inputs (transition probabilities, distributions, initial conditions, etc.)
                process_scenario_inputs(console, s)

                if os.path.exists(tmp_file):
                    os.remove(tmp_file)

                # if the scenario is a result scenario
                if s.is_result:

                    # import state class reports,
                    console.generate_report('stateclass-summary', tmp_file, s.sid)
                    create_stateclass_summary(project, s, tmp_file)

                    print('Imported stateclass summary report for scenario {}.'.format(s.sid))
                    os.remove(tmp_file)

                    # import transition summary reports
                    console.generate_report('transition-summary', tmp_file, s.sid)
                    create_transition_summary(project, s, tmp_file)

                    print('Imported transition summary report for scenario {}.'.format(s.sid))
                    os.remove(tmp_file)

                    # import transition-stateclass summary reports
                    console.generate_report('transition-stateclass-summary', tmp_file, s.sid)
                    create_transition_sc_summary(project, s, tmp_file)

                    print('Imported transition-by-stateclass summary report for scenario {}.'.format(s.sid))
                    os.remove(tmp_file)

                    # TODO - add remaining reports

                print("Scenario {} successfully imported into project {}.".format(s.sid, project.name))
            print("Project {} successfully imported into landscapesim".format(project.name))
        print("Library {} successfully added to landscapesim.".format(name))