"""
    Report generation utilities.
    Provide the file with the generated report from SyncroSim,
    create the related rows django rows to expose
"""

import csv
import os

from landscapesim import models
from landscapesim.io.utils import default_int


def create_stateclass_summary(s, file):
    report = models.StateClassSummaryReport.objects.create(scenario=s)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = models.StateClassSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=models.Stratum.objects.filter(name__exact=row['StratumID'], project=s.project).first(),
                stateclass=models.StateClass.objects.filter(name__exact=row['StateClassID'], project=s.project).first(),
                amount=float(row['Amount']),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                proportion_of_landscape=float(row['ProportionOfLandscape']),
                proportion_of_stratum=float(row['ProportionOfStratumID'])
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = models.SecondaryStratum.objects.filter(
                    name__exact=secondary_stratum, project=s.project
                ).first()
                r.save()
    return report


def create_transition_summary(s, file):
    report = models.TransitionSummaryReport.objects.create(scenario=s)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = models.TransitionSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=models.Stratum.objects.filter(name__exact=row['StratumID'], project=s.project).first(),
                transition_group=models.TransitionGroup.objects.filter(
                    name__exact=row['TransitionGroupID'], project=s.project
                ).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = models.SecondaryStratum.objects.filter(
                    name__exact=secondary_stratum, project=s.project
                ).first()
                r.save()
    return report


def create_transition_sc_summary(s, file):
    report = models.TransitionByStateClassSummaryReport.objects.create(scenario=s)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = models.TransitionByStateClassSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=models.Stratum.objects.filter(name__exact=row['StratumID'], project=s.project).first(),
                transition_type=models.TransitionType.objects.filter(
                    name__exact=row['TransitionTypeID'], project=s.project
                ).first(),
                stateclass_src=models.StateClass.objects.filter(
                    name__exact=row['StateClassID'], project=s.project
                ).first(),
                stateclass_dest=models.StateClass.objects.filter(
                    name__exact=row['EndStateClassID'], project=s.project
                ).first(),
                amount=float(row['Amount'])
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = models.SecondaryStratum.objects.filter(
                    name__exact=secondary_stratum, project=s.project
                ).first()
                r.save()
    return report


def create_state_attribute_summary(s, file):
    report = models.StateAttributeSummaryReport.objects.create(scenario=s)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = models.StateAttributeSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=models.Stratum.objects.filter(name__exact=row['StratumID'], project=s.project).first(),
                state_attribute_type=models.StateAttributeType.objects.filter(
                    name__exact=row['StateAttributeTypeID'], project=s.project).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = models.SecondaryStratum.objects.filter(
                    name__exact=secondary_stratum, project=s.project
                ).first()
                r.save()
    return report


def create_transition_attribute_summary(s, file):
    report = models.TransitionAttributeSummaryReport.objects.create(scenario=s)
    with open(file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            r = models.TransitionAttributeSummaryReportRow.objects.create(
                report=report,
                iteration=int(row['Iteration']),
                timestep=int(row['Timestep']),
                stratum=models.Stratum.objects.filter(name__exact=row['StratumID'], project=s.project).first(),
                transition_attribute_type=models.TransitionAttributeType.objects.filter(
                    name__exact=row['TransitionAttributeTypeID'], project=s.project
                ).first(),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                amount=float(row['Amount']),
            )
            secondary_stratum = row['SecondaryStratumID']
            if len(secondary_stratum) > 0:
                r.secondary_stratum = models.SecondaryStratum.objects.filter(
                    name__exact=secondary_stratum, project=s.project
                ).first()
                r.save()
    return report


def process_reports(console, s, tmp_file):
    """ Convenient shortcut to processing all reports """

    # import state class reports,
    console.generate_report('stateclass-summary', tmp_file, s.sid)
    create_stateclass_summary(s, tmp_file)

    print('Imported stateclass summary report for scenario {}.'.format(s.sid))
    os.remove(tmp_file)

    # import transition summary reports
    #console.generate_report('transition-summary', tmp_file, s.sid)
    #create_transition_summary(s, tmp_file)

    #print('Imported transition summary report for scenario {}.'.format(s.sid))
    #os.remove(tmp_file)

    # import transition-stateclass summary reports
    #console.generate_report('transition-stateclass-summary', tmp_file, s.sid)
    #create_transition_sc_summary(s, tmp_file)

    #print('Imported transition-by-stateclass summary report for scenario {}.'.format(s.sid))
    #os.remove(tmp_file)

    # import state-attribute summary reports
    #console.generate_report('state-attributes', tmp_file, s.sid)
    #create_state_attribute_summary(s, tmp_file)

    #print('Imported state-attribute summary report for scenario {}.'.format(s.sid))
    #os.remove(tmp_file)

    # import transition-attribute summary reports
    #console.generate_report('transition-attributes', tmp_file, s.sid)
    #create_transition_attribute_summary(s, tmp_file)

    #print('Imported transition-attribute summary report for scenario {}.'.format(s.sid))
    #os.remove(tmp_file)
