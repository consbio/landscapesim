import os
from shutil import copyfile

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from landscapesim import contrib
from landscapesim.common.consoles import STSimConsole
from landscapesim.models import Library, Project, Scenario

STSIM_LIBRARY_DIRECTORY = getattr(settings, 'STSIM_LIBRARY_DIRECTORY')


class Command(BaseCommand):

    help = 'Registers a .ssim library based on the file path.'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str)
        parser.add_argument('file', nargs=1, type=str)

    def handle(self, name, file, *args, **options):
        file = file[0]
        name = name[0]

        file = os.path.join(STSIM_LIBRARY_DIRECTORY, file)
        orig_file = file.split('.ssim')[0] + '_orig.ssim'
        tmp_file = file.split('.ssim')[0] + '_tmp.csv'

        if Library.objects.filter(file__iexact=file).exists():
            print('The library located at {} already exists in the database.'.format(file))
            return

        if not os.path.exists(orig_file):
            message = 'A copy of the library does not exist. Create one now or cancel? '
            if input(message).lower() not in {'y', 'yes'}:
                print("Abort - Cannot continue without replicating the library values.")
                return
            else:
                copyfile(file, orig_file)

        console = STSimConsole(lib_path=file, orig_lib_path=orig_file, exe=settings.STSIM_EXE_PATH)

        with transaction.atomic():

            # Console works, now create library
            library = Library.objects.create(name=name, file=file, orig_file=orig_file, tmp_file=tmp_file)

            projects = console.list_projects()
            all_scenarios = console.list_scenario_attrs()
            result_scenarios = console.list_scenario_attrs(results_only=True)
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

                # At this point, there may be slightly different ways to import a library. We check to see
                # if there are any contributor modules that might handle them. Otherwise, we do a normal import.
                project_importer = contrib.get_project_importer_cls(name)
                project_importer(console, project).process_project_definitions()

                # Now import any scenario-specific information we want to capture
                scenarios = Scenario.objects.filter(project=project)
                for s in scenarios:
                    # Import scenario inputs (transition probabilities, distributions, initial conditions, etc.)
                    scenario_importer = contrib.get_scenario_importer_cls(name)(console, s)
                    scenario_importer.import_run_control()
                    scenario_importer.import_output_options()
                    scenario_importer.import_post_processed_sheets()

                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)

                    if s.is_result:

                        # Import all available reports from result scenarios
                        report_importer = contrib.get_report_importer_cls(name)
                        report_importer(s, console).create_all_summaries()

                        # Import output rasters
                        # TODO - decide whether this should be allowed on initial import
                        # ServiceGenerator(s).create_output_services()

                    print("Scenario {} successfully imported into project {}.".format(s.sid, project.name))
                print("Project {} successfully imported into landscapesim.".format(project.name))
            print("Library {} successfully added to landscapesim.".format(name))
