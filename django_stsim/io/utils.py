import uuid
import csv
import os
from django_stsim.models import RunControl, OutputOption, Stratum, SecondaryStratum, StateClass, TransitionType, \
    TransitionGroup, TransitionTypeGroup, TransitionMultiplierType
from django_stsim.models import DeterministicTransition, Transition, InitialConditionsNonSpatial, \
    InitialConditionsNonSpatialDistribution, TransitionTarget, TransitionMultiplierValue

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
    kwgs = {'pid': project.pid, 'overwrite': True, 'orig': True}
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

    # import secondary strata
    console.export_sheet('STSim_SecondaryStratum', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            SecondaryStratum.objects.create(
                project=project,
                secondary_stratum_id=int(row['ID']) if len(row['ID']) > 0 else -1,
                name=row['Name'],
                description=row['Description']
            )
    print('Imported secondary strata for project {}.'.format(project.name))

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
    console.export_sheet('STSim_TransitionType', tmp_file, **kwgs)
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
    console.export_sheet('STSim_TransitionGroup', tmp_file, **kwgs)
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
    console.export_sheet('STSim_TransitionTypeGroup', tmp_file, **kwgs)
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

    # import transition multiplier types
    console.export_sheet('STSim_TransitionMultiplierType', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            TransitionMultiplierType.objects.create(
                project=project,
                name=row['Name']
            )
    print('Imported transition multiplier types for project {}.'.format(project.name))


# TODO - size dist/priority, state/transition attributes/targets,
def process_scenario_inputs(console, scenario):

    tmp_file = get_random_csv(scenario.project.library.tmp_file)
    project = scenario.project
    kwgs = {'sid': scenario.sid, 'overwrite': True, 'orig': not scenario.is_result}

    # import initial run control
    console.export_sheet('STSim_RunControl', tmp_file, **kwgs)
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
    console.export_sheet('STSim_OutputOptions', tmp_file, **kwgs)
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

    console.export_sheet('STSim_DeterministicTransition', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            age_max = int(row['AgeMax']) if len(row['AgeMax']) > 0 else ''
            stratum_dest = row['StratumIDDest']
            t = DeterministicTransition.objects.create(
                scenario=scenario,
                stratum_src=Stratum.objects.filter(name__exact=row['StratumIDSource'],
                                                   project=project).first(),
                stratum_dest=Stratum.objects.filter(name__exact=row['StratumIDDest'],
                                                    project=project).first(),
                stateclass_src=StateClass.objects.filter(name__exact=row['StateClassIDSource'],
                                                         project=project).first(),
                stateclass_dest=StateClass.objects.filter(name__exact=row['StateClassIDDest'],
                                                          project=project).first(),
                age_min=int(row['AgeMin'])
            )
            if len(stratum_dest) > 0:
                t.stratum_dest = Stratum.objects.filter(name__exact=stratum_dest, project=project).first()
            if type(age_max) is int:
                t.age_max = age_max
            t.save()
    print('Imported deterministic transitions for scenario {}'.format(scenario.sid))

    # import initial probabilistic transition probabilities
    console.export_sheet('STSim_Transition', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            stratum_dest = row['StratumIDDest']
            t = Transition.objects.create(  # omit stratum_dest, no change in stratum per timestep
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
            if len(stratum_dest) > 0:
                t.stratum_dest = Stratum.objects.filter(name__exact=stratum_dest, project=project).first()
                t.save()

    print('Imported transition probabilities for scenario {}'.format(scenario.sid))

    # Import initial conditions non spatial configuration
    console.export_sheet('STSim_InitialConditionsNonSpatial', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        conditions = [r for r in reader][0]
        InitialConditionsNonSpatial.objects.create(
            scenario=scenario,
            total_amount=float(conditions['TotalAmount']),
            num_cells=int(conditions['NumCells']),
            calc_from_dist=conditions['CalcFromDist']
        )
    print('Imported (default) initial conditions configuration for scenario {}'.format(scenario.sid))

    # Import initial conditions non spatial values
    console.export_sheet('STSim_InitialConditionsNonSpatialDistribution', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            secondary_stratum = row['SecondaryStratumID']
            age_min = int(row['AgeMin']) if len(row['AgeMin']) > 0 else ''
            age_max = int(row['AgeMax']) if len(row['AgeMax']) > 0 else ''
            ic = InitialConditionsNonSpatialDistribution.objects.create(
                scenario=scenario,
                stratum=Stratum.objects.filter(name__exact=row['StratumID'],
                                                   project=project).first(),
                stateclass=StateClass.objects.filter(name__exact=row['StateClassID'],
                                                         project=project).first(),
                relative_amount=float(row['RelativeAmount'])
            )
            if type(age_min) is int:
                ic.age_min = age_min
            if type(age_max) is int:
                ic.age_max = age_max
            if len(secondary_stratum) > 0:
                ic.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            ic.save()
    print('Imported (default) initial conditions values for scenario {}'.format(scenario.sid))

    # Import transition targets
    console.export_sheet('STSim_TransitionTarget', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            secondary_stratum = row['SecondaryStratumID']
            iteration = int(row['Iteration']) if len(row['Iteration']) > 0 else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) > 0 else ''
            tt = TransitionTarget.objects.create(
                scenario=scenario,
                stratum=Stratum.objects.filter(name__exact=row['StratumID'], project=project).first(),
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                target_area=float(row['Amount'])
            )
            if type(iteration) is int:
                tt.iteration = iteration
            if type(timestep) is int:
                tt.timestep = timestep
            if len(secondary_stratum) > 0:
                tt.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            tt.save()
    print('Imported transition targets for scenario {}'.format(scenario.sid))

    # Import transition multiplier values
    console.export_sheet('STSim_TransitionMultiplierValue', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            stratum = row['StratumID']
            secondary_stratum = row['SecondaryStratumID']
            stateclass = row['StateClassID']
            iteration = int(row['Iteration']) if len(row['Iteration']) > 0 else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) > 0 else ''
            transition_multiplier_type = row['TransitionMultiplierTypeID']
            tm = TransitionMultiplierValue.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                multiplier=float(row['Amount'])
            )
            if len(stratum) > 0:
                tm.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum) > 0:
                tm.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            if len(stateclass) > 0:
                tm.stateclass = StateClass.objects.filter(name__exact=stateclass, project=project).first()
            if type(iteration) is int:
                tm.iteration = iteration
            if type(timestep) is int:
                tm.timestep = timestep
            if len(transition_multiplier_type) > 0:
                tm.transition_multiplier_type = TransitionMultiplierType.objects.filter(
                    name__exact=transition_multiplier_type, project=project).first()

            tm.save()
    print('Imported transition multiplier values for scenario {}'.format(scenario.sid))

    # Import transition size distribution

    # Import transition size prioritization

    # Import transition spatial multiplier configuration

    # Import state attribute values

    # import transition attribute values

    # import transition attribute targets


    if os.path.exists(tmp_file):
        os.remove(tmp_file)
