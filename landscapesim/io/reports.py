"""
    Report generation utilities.
    Provide the file with the generated report from SyncroSim,
    create the related rows django rows to expose
"""

import csv

from landscapesim.io.utils import default_int
from landscapesim.models import Stratum, SecondaryStratum, StateClass, TransitionType, TransitionGroup, \
    StateAttributeType, TransitionAttributeType, TransitionSummaryReport, TransitionSummaryReportRow, \
    StateClassSummaryReport, StateClassSummaryReportRow, TransitionByStateClassSummaryReport, \
    TransitionByStateClassSummaryReportRow, StateAttributeSummaryReport, StateAttributeSummaryReportRow, \
    TransitionAttributeSummaryReport, TransitionAttributeSummaryReportRow


def create_stateclass_summary(project, scenario, file):
    report = StateClassSummaryReport.objects.create(scenario=scenario)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = StateClassSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                stateclass=StateClass.objects.filter(name__exact=row['StateClassID'], project=project).first(),
                amount=float(row['Amount']),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                proportion_of_landscape=float(row['ProportionOfLandscape']),
                proportion_of_stratum=float(row['ProportionOfStratumID'])
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum, project=project).first()
                r.save()
    return report


def create_transition_summary(project, scenario, file):
    report = TransitionSummaryReport.objects.create(scenario=scenario)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = TransitionSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum, project=project).first()
                r.save()
    return report


def create_transition_sc_summary(project, scenario, file):
    report = TransitionByStateClassSummaryReport.objects.create(scenario=scenario)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = TransitionByStateClassSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                transition_type=TransitionType.objects.filter(
                    name__exact=row['TransitionTypeID'], project=project).first(),
                stateclass_src=StateClass.objects.filter(
                    name__exact=row['StateClassID'], project=project).first(),
                stateclass_dest=StateClass.objects.filter(
                    name__exact=row['EndStateClassID'], project=project).first(),
                amount=float(row['Amount'])
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum, project=project).first()
                r.save()
    return report


def create_state_attribute_summary(project, scenario, file):
    report = StateAttributeSummaryReport.objects.create(scenario=scenario)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = StateAttributeSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                state_attribute_type=StateAttributeType.objects.filter(
                    name__exact=row['StateAttributeTypeID'], project=project).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                      project=project).first()
                r.save()
    return report


def create_transition_attribute_summary(project, scenario, file):
    report = TransitionAttributeSummaryReport.objects.create(scenario=scenario)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = TransitionAttributeSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                transition_attribute_type=TransitionAttributeType.objects.filter(
                    name__exact=row['TransitionAttributeTypeID'], project=project).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                      project=project).first()
                r.save()
    return report