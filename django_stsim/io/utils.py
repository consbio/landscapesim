import uuid
import csv

from django_stsim.models import RunControl, OutputOption, Stratum, StateClass, TransitionType, TransitionGroup,\
    TransitionTypeGroup, Transition

M2_TO_ACRES = 0.000247105


# meters squard to acres
def cells_to_acres(numcells, res):
    return pow(res, 2) * M2_TO_ACRES * numcells


def order():
    return lambda t: t[0]


def get_random_csv(file):
    return file.replace('.csv', str(uuid.uuid4()) + '.csv')


def color_to_rgba(colorstr):
    r, g, b, a = colorstr.split(',')
    return {'r': r, 'g': g, 'b': b, 'a': a}


def process_project_definitions(console, project):

    # import strata
    tmp_file = get_random_csv(project.library.tmp_file)
    strata = console.export_vegtype_definitions(project.pid, tmp_file)
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
    stateclasses = console.export_stateclass_definitions(project.pid, tmp_file)
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

    # import transition types
    console.export_sheet('STSim_TransitionType', tmp_file, pid=project.pid, overwrite=True, orig=True)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            TransitionType.objects.create(
                project=project,
                transition_type_id=int(row['ID']) if len(row['ID']) > 0 else -1,
                name=row['Name'],
                color=row['Color'],
                description=row['Description']
            )
    print('Imported transition types for project {}.'.format(project.name))

    # import transition groups
    console.export_sheet('STSim_TransitionGroup', tmp_file, pid=project.pid, overwrite=True, orig=True)
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
    console.export_sheet('STSim_TransitionTypeGroup', tmp_file, pid=project.pid, overwrite=True, orig=True)
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

# TODO - Add deterministic transitions, initial_conditions_nonspatial, transition targets, multiplier values, size dist/priority, state/transition attributes/targets,
def process_scenario_inputs(console, scenario):
    # import initial run control
    tmp_file = get_random_csv(scenario.project.library.tmp_file)
    project = scenario.project
    console.export_sheet('STSim_RunControl', tmp_file, sid=scenario.sid, overwrite=True, orig=True)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        run_options = [r for r in reader][0]
        RunControl.objects.create(
            scenario=scenario,
            min_iteration=int(run_options['MinimumIteration']),
            max_iteration=int(run_options['MaximumIteration']),
            min_timestep=int(run_options['MinimumTimestep']),
            max_timestep=int(run_options['MaximumTimestep']),
            is_spatial=True if run_options['IsSpatial'] == 'Yes' else False
        )
    print('Imported (initial) run control for scenario {}'.format(scenario.sid))

    # import output options
    console.export_sheet('STSim_OutputOptions', tmp_file, sid=scenario.sid, overwrite=True, orig=True)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        output_options = [r for r in reader][0]
        for opt in output_options.keys():
            if len(output_options[opt]) > 0:  # a integer, or 'Yes', else ''
                if 'Timesteps' in opt:
                    timestep = int(output_options[opt])
                else:
                    timestep = -1  # default, won't be used
                enabled = True
            else:
                enabled = False
                timestep = -1
            OutputOption.objects.create(
                scenario=scenario,
                name=opt,
                timestep=timestep,
                enabled=enabled
            )
    print('Imported (initial) output options for scenario {}'.format(scenario.sid))

    # import initial probabilistic transition probabilities
    console.export_sheet('STSim_Transition', tmp_file, sid=scenario.sid, overwrite=True, orig=True)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            if len(row['StratumIDDest']) > 0:
                Transition.objects.create(
                    scenario=scenario,
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
                    scenario=scenario,
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
    print('Imported transition probabilities for scenario {}'.format(scenario.sid))
