from celery import task
from django_stsim.models import Library, Project, Scenario, AsyncJobModel
import json

from django_stsim.io.consoles import STSimConsole
from django.conf import settings
exe = settings.STSIM_EXE_PATH


@task(bind=True)
def run_model(self, library_name, pid, sid):
    library = Library.objects.get(name__iexact=library_name)
    console = STSimConsole(exe=exe, lib_path=library.file, orig_lib_path=library.orig_file)
    try:
        result_sid = int(console.run_model(sid))
    except IOError:
        return
    scenario_info = [x for x in console.list_scenario_names(results_only=True)
                     if int(x['sid']) == result_sid][0]
    scenario = Scenario.objects.create(
        project=Project.objects.get(library=library, pid=int(pid)),
        name=scenario_info['name'],
        sid=result_sid,
        is_result=True
    )
    job = AsyncJobModel.objects.get(celery_id=self.request.id)
    job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
    job.save()