from celery import task
from django_stsim.models import Library, Project, Scenario, AsyncJobModel
import json
import os
import uuid
from django_stsim.io.consoles import STSimConsole
from django_stsim.io.reports import create_stateclass_summary, create_transition_sc_summary, create_transition_summary

from django.core import exceptions
from django.conf import settings
exe = settings.STSIM_EXE_PATH


@task(bind=True)
def run_model(self, library_name, pid, sid):
    lib = Library.objects.get(name__iexact=library_name)
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    try:
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")
    scenario_info = [x for x in console.list_scenario_names(results_only=True)
                     if int(x['sid']) == result_sid][0]
    scenario = Scenario.objects.create(
        project=Project.objects.get(library=lib, pid=int(pid)),
        name=scenario_info['name'],
        sid=result_sid,
        is_result=True
    )
    job = AsyncJobModel.objects.get(celery_id=self.request.id)
    job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
    job.save()


@task(bind=True)
def generate_report(self, library_name, pid, sid, report_name):
    lib = Library.objects.get(name__iexact=library_name)
    proj = Project.objects.get(library=lib, pid=pid)
    s = Scenario.objects.filter(project=proj, sid=sid)
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    tmp_file = lib.tmp_file.replace('.csv', uuid.uuid4() + '.csv')

    try:
        console.generate_report(report_name, tmp_file, sid)
    except:
        raise IOError("Error generating report")
    if report_name == 'stateclass-summary':
        report = create_stateclass_summary(proj, s, tmp_file)
    elif report_name == 'transition-summary':
        report = create_transition_sc_summary(proj, s, tmp_file)
    elif report_name == 'transition-summary':
        report = create_transition_sc_summary(proj, s, tmp_file)
    else:
        raise exceptions.ObjectDoesNotExist("The {} report for project {}, scenario {} was not found."
                                            .format(report_name, proj.name, s.sid))

    os.remove(tmp_file)

    job = AsyncJobModel.objects.get(celery_id=self.request.id)
    job.outputs = json.dumps({report_name: report.id})
    job.save()
