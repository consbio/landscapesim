from celery import task
from landscapesim.models import Library, Project, Scenario, RunScenarioModel, GenerateReportModel
import json
import os
from landscapesim.io.consoles import STSimConsole
from landscapesim.io.reports import create_stateclass_summary, create_transition_sc_summary, create_transition_summary, \
    create_transition_attribute_summary, create_state_attribute_summary
from landscapesim.io.utils import get_random_csv, process_scenario_inputs

from django.core import exceptions
from django.conf import settings
exe = settings.STSIM_EXE_PATH


@task(bind=True)
def run_model(self, library_name, pid, sid):
    lib = Library.objects.get(name__iexact=library_name)
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    job = RunScenarioModel.objects.get(celery_id=self.request.id)

    try:
        result_sid = int(console.run_model(sid))
    except:
        raise IOError("Error running model")
    scenario_info = [x for x in console.list_scenario_attrs(results_only=True)
                     if int(x['sid']) == result_sid][0]
    scenario = Scenario.objects.create(
        project=job.parent_scenario.project,
        name=scenario_info['name'],
        sid=result_sid,
        is_result=True
    )
    job.result_scenario = scenario
    job.outputs = json.dumps({'result_scenario': {'id': scenario.id, 'sid': scenario.sid}})
    job.save()

    process_scenario_inputs(console, scenario)


@task(bind=True)
def generate_report(self, library_name, pid, sid, report_name):
    lib = Library.objects.get(name__iexact=library_name)
    proj = Project.objects.get(library=lib, pid=pid)
    s = Scenario.objects.filter(project=proj, sid=sid).first()
    console = STSimConsole(exe=exe, lib_path=lib.file, orig_lib_path=lib.orig_file)
    tmp_file = get_random_csv(lib.tmp_file)

    try:
        console.generate_report(report_name, tmp_file, sid)
    except:
        raise IOError("Error generating report")
    if report_name == 'stateclass-summary':
        report = create_stateclass_summary(proj, s, tmp_file)
    elif report_name == 'transition-summary':
        report = create_transition_summary(proj, s, tmp_file)
    elif report_name == 'transition-stateclass-summary':
        report = create_transition_sc_summary(proj, s, tmp_file)
    elif report_name == 'state-attributes':
        report = create_state_attribute_summary(proj, s, tmp_file)
    elif report_name == 'transition-attributes':
        report = create_transition_attribute_summary(proj, s, tmp_file)
    else:
        raise exceptions.ObjectDoesNotExist("The {} report for project {}, scenario {} was not found."
                                            .format(report_name, proj.name, s.sid))

    os.remove(tmp_file)

    job = GenerateReportModel.objects.get(celery_id=self.request.id)
    job.outputs = json.dumps({report_name: report.id})
    job.save()
