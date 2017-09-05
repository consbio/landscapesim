import csv
import os
import uuid

from landscapesim.io.rasters import process_input_rasters, process_output_rasters
from landscapesim.models import DistributionType, Terminology, Stratum, SecondaryStratum, StateClass, TransitionType, \
    TransitionGroup, TransitionTypeGroup, TransitionMultiplierType, \
    DistributionValue, RunControl, OutputOption, DeterministicTransition, Transition, InitialConditionsNonSpatial, \
    InitialConditionsNonSpatialDistribution, InitialConditionsSpatial, TransitionTarget, TransitionMultiplierValue, \
    AttributeGroup, StateAttributeType, TransitionAttributeType, TransitionSizeDistribution, \
    TransitionSizePrioritization, TransitionSpatialMultiplier, StateAttributeValue, TransitionAttributeValue, \
    TransitionAttributeTarget

M2_TO_ACRES = 0.000247105


# meters squared to acres
def cells_to_acres(numcells, res):
    return pow(res, 2) * M2_TO_ACRES * numcells


def order():
    return lambda t: t[0]


def get_random_csv(file):
    return file.replace('.csv', str(uuid.uuid4()) + '.csv')


def color_to_rgba(colorstr):
    r, g, b, a = colorstr.split(',')
    return {'r': r, 'g': g, 'b': b, 'a': a}


def default_int(value):
    return int(value) if len(value) else -1


def default_int_to_empty_or_int(value):
    return value if value != -1 else ''


def default_float(value):
    return float(value) if len(value) else -1


def default_float_to_empty_or_float(value):
    return value if value != -1 else ''


def empty_or_yes_to_bool(value):
    return value == 'Yes'


def bool_to_empty_or_yes(value):
    return 'Yes' if value else ''


def process_project_definitions(console, project):

    tmp_file = get_random_csv(project.library.tmp_file)
    kwgs = {'pid': project.pid, 'overwrite': True, 'orig': True}

    # Import terminology
    console.export_sheet('STSim_Terminology', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        terms = [r for r in reader][0]
        Terminology.objects.create(
            project=project,
            amount_label=terms['AmountLabel'],
            amount_units=terms['AmountUnits'],
            state_label_x=terms['StateLabelX'],
            state_label_y=terms['StateLabelY'],
            primary_stratum_label=terms['PrimaryStratumLabel'],
            secondary_stratum_label=terms['SecondaryStratumLabel'],
            timestep_units=terms['TimestepUnits']
        )
    print('Imported terminology for project {}.'.format(project.name))

    console.export_sheet('Stats_DistributionType', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            DistributionType.objects.create(
                project=project,
                name=row['Name'],
                description=row['Description'],
                is_internal=empty_or_yes_to_bool(row['IsInternal'])
            )
    print('Imported distribution types for project {}.'.format(project.name))

    # Import strata
    console.export_sheet('STSim_Stratum', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            Stratum.objects.create(
                stratum_id=default_int(row['ID']),
                project=project,
                name=row['Name'],
                color=row['Color'],
                description=row['Description']
            )
    print('Imported strata for project {}.'.format(project.name))

    # import secondary strata
    console.export_sheet('STSim_SecondaryStratum', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            SecondaryStratum.objects.create(
                project=project,
                secondary_stratum_id=default_int(row['ID']),
                name=row['Name'],
                description=row['Description']
            )
    print('Imported secondary strata for project {}.'.format(project.name))

    # import stateclasses
    console.export_sheet('STSim_StateClass', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            StateClass.objects.create(
                stateclass_id=default_int(row['ID']),
                project=project,
                name=row['Name'],
                state_label_x=row['StateLabelXID'],
                state_label_y=row['StateLabelYID'],
                color=row['Color'],
                description=row['Description']
            )
    print('Imported state classes for project {}.'.format(project.name))

    # import transition types
    console.export_sheet('STSim_TransitionType', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            TransitionType.objects.create(
                project=project,
                transition_type_id=default_int(row['ID']),
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

    # Import attribute groups
    console.export_sheet('STSim_AttributeGroup', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            AttributeGroup.objects.create(
                project=project,
                name=row['Name'],
                description=row['Description']
            )
    print('Imported attribute groups for project {}.'.format(project.name))

    # Import state attribute types
    console.export_sheet('STSim_StateAttributeType', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            StateAttributeType.objects.create(
                project=project,
                name=row['Name'],
                attribute_group=AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                              project=project).first(),
                units=row['Units'],
                description=row['Description']
            )
    print('Imported state attribute types for project {}.'.format(project.name))

    # Import transition attribute types
    console.export_sheet('STSim_TransitionAttributeType', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            TransitionAttributeType.objects.create(
                project=project,
                name=row['Name'],
                attribute_group=AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                              project=project).first(),
                units=row['Units'],
                description=row['Description']
            )
    print('Imported transition attribute types for project {}.'.format(project.name))


def process_scenario_inputs(console, scenario):

    tmp_file = get_random_csv(scenario.project.library.tmp_file)
    project = scenario.project
    kwgs = {'sid': scenario.sid, 'overwrite': True, 'orig': not scenario.is_result}

    def add_distribution_to(obj, entry):
        """ Simple helper for adding distributions to models that use them """

        dist_type = entry['DistributionType']
        if len(dist_type):
            obj.distribution_type = DistributionType.objects.filter(name__exact=dist_type, project=project).first()
            if len(entry['DistributionSD']):
                obj.distribution_sd = float(entry['DistributionSD'])
            if len(entry['DistributionMin']):
                obj.distribution_min = float(entry['DistributionMin'])
            if len(entry['DistributionMax']):
                obj.distribution_max = float(entry['DistributionMax'])

    console.export_sheet('Stats_DistributionValue', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            dmin = float(row['Min']) if len(row['Min']) else ''
            relative_frequency = float(row['RelativeFrequency']) if len(row['RelativeFrequency']) else ''
            dv = DistributionValue.objects.create(
                scenario=scenario,
                distribution_type=DistributionType.objects.filter(name__exact=row['DistributionTypeID'],
                                                                  project=project).first(),
                dmax=float(row['Max'])
            )
            if type(dmin) is float:
                dv.dmin = dmin
            if type(relative_frequency) is float:
                dv.relative_frequency = relative_frequency

            dv.save()
    print('Imported distribution values for scenario {}'.format(scenario.sid))

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
            is_spatial=empty_or_yes_to_bool(run_options['IsSpatial'])
        )
    print('Imported run control for scenario {}'.format(scenario.sid))

    # import output options
    console.export_sheet('STSim_OutputOptions', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        output_options = [r for r in reader]
        oo = OutputOption.objects.create(scenario=scenario)
        if len(output_options):
            output_options = output_options[0]
            oo.sum_sc = empty_or_yes_to_bool(output_options['SummaryOutputSC'])
            oo.sum_sc_t = default_int(output_options['SummaryOutputSCTimesteps'])
            oo.sum_sc_zeros = empty_or_yes_to_bool(output_options['SummaryOutputSCZeroValues'])
            oo.raster_sc = empty_or_yes_to_bool(output_options['RasterOutputSC'])
            oo.raster_sc_t = default_int(output_options['RasterOutputSCTimesteps'])
            oo.sum_tr = empty_or_yes_to_bool(output_options['SummaryOutputTRIntervalMean'])
            oo.sum_tr_t = default_int(output_options['SummaryOutputTRTimesteps'])
            oo.sum_tr_interval = empty_or_yes_to_bool(output_options['SummaryOutputTRIntervalMean'])
            oo.raster_tr = empty_or_yes_to_bool(output_options['RasterOutputTR'])
            oo.raster_tr_t = default_int(output_options['RasterOutputTRTimesteps'])
            oo.sum_trsc = empty_or_yes_to_bool(output_options['SummaryOutputTRSC'])
            oo.sum_trsc_t = default_int(output_options['SummaryOutputTRSCTimesteps'])
            oo.sum_sa = empty_or_yes_to_bool(output_options['SummaryOutputSA'])
            oo.sum_sa_t = default_int(output_options['SummaryOutputSATimesteps'])
            oo.raster_sa = empty_or_yes_to_bool(output_options['RasterOutputSA'])
            oo.raster_sa_t = default_int(output_options['RasterOutputSATimesteps'])
            oo.sum_ta = empty_or_yes_to_bool(output_options['SummaryOutputTA'])
            oo.sum_ta_t = default_int(output_options['SummaryOutputTATimesteps'])
            oo.raster_ta = empty_or_yes_to_bool(output_options['RasterOutputTA'])
            oo.raster_ta_t = default_int(output_options['RasterOutputTATimesteps'])
            oo.raster_strata = empty_or_yes_to_bool(output_options['RasterOutputST'])
            oo.raster_strata_t = default_int(output_options['RasterOutputSTTimesteps'])
            oo.raster_age = empty_or_yes_to_bool(output_options['RasterOutputAge'])
            oo.raster_age_t = default_int(output_options['RasterOutputAgeTimesteps'])
            oo.raster_tst = empty_or_yes_to_bool(output_options['RasterOutputTST'])
            oo.raster_tst_t = default_int(output_options['RasterOutputTSTTimesteps'])
            oo.raster_aatp = empty_or_yes_to_bool(output_options['RasterOutputAATP'])
            oo.raster_aatp_t = default_int(output_options['RasterOutputAATPTimesteps'])
            oo.save()
    print('Imported output options for scenario {}'.format(scenario.sid))

    console.export_sheet('STSim_DeterministicTransition', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
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
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax']),
                location=row['Location']
            )
            if len(stratum_dest):
                t.stratum_dest = Stratum.objects.filter(name__exact=stratum_dest, project=project).first()
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
                age_reset=empty_or_yes_to_bool(row['AgeReset'])
            )
            if len(stratum_dest):
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
            calc_from_dist=empty_or_yes_to_bool(conditions['CalcFromDist'])
        )
    print('Imported initial conditions for scenario {}'.format(scenario.sid))

    # Import initial conditions non spatial values
    console.export_sheet('STSim_InitialConditionsNonSpatialDistribution', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            secondary_stratum = row['SecondaryStratumID']
            ic = InitialConditionsNonSpatialDistribution.objects.create(
                scenario=scenario,
                stratum=Stratum.objects.filter(name__exact=row['StratumID'],
                                                   project=project).first(),
                stateclass=StateClass.objects.filter(name__exact=row['StateClassID'],
                                                         project=project).first(),
                relative_amount=float(row['RelativeAmount']),
                age_min=default_int(row['AgeMin']),
                age_max=default_int(row['AgeMax'])
            )
            if len(secondary_stratum):
                ic.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            ic.save()
    print('Imported initial conditions values for scenario {}'.format(scenario.sid))

    # Import initial conditions spatial
    console.export_sheet('STSim_InitialConditionsSpatial', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        init = [r for r in reader]
        if len(init):
            init = init[0]
            ics = InitialConditionsSpatial.objects.create(
                scenario=scenario,
                num_rows=default_int(init['NumRows']),
                num_cols=default_int(init['NumColumns']),
                num_cells=default_int(init['NumCells']),
                cell_size=default_float(init['CellSize']),
                cell_size_units=init['CellSizeUnits'],
                cell_area=default_float(init['CellArea']),
                cell_area_override=empty_or_yes_to_bool(init['CellAreaOverride']),
                xll_corner=default_float(init['XLLCorner']),
                yll_corner=default_float(init['YLLCorner']),
                srs=init['SRS'],
                stratum_file_name=init['StratumFileName'],
                secondary_stratum_file_name=init['SecondaryStratumFileName'],
                stateclass_file_name=init['StateClassFileName'],
                age_file_name=init['AgeFileName']
            )

            # Create map services
            process_input_rasters(ics)

    print('Imported initial conditions spatial settings for scenario {}'.format(scenario.sid))

    # Import transition targets
    console.export_sheet('STSim_TransitionTarget', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            stratum = row['StratumID']
            secondary_stratum = row['SecondaryStratumID']
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            tt = TransitionTarget.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                target_area=float(row['Amount'])
            )
            if type(iteration) is int:
                tt.iteration = iteration
            if type(timestep) is int:
                tt.timestep = timestep
            if len(stratum):
                tt.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum):
                tt.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            add_distribution_to(tt, row)
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
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            transition_multiplier_type = row['TransitionMultiplierTypeID']
            tm = TransitionMultiplierValue.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                multiplier=float(row['Amount'])
            )
            if len(stratum):
                tm.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum):
                tm.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                       project=project).first()
            if len(stateclass):
                tm.stateclass = StateClass.objects.filter(name__exact=stateclass, project=project).first()
            if type(iteration) is int:
                tm.iteration = iteration
            if type(timestep) is int:
                tm.timestep = timestep
            if len(transition_multiplier_type):
                tm.transition_multiplier_type = TransitionMultiplierType.objects.filter(
                    name__exact=transition_multiplier_type, project=project).first()
            add_distribution_to(tm, row)
            tm.save()
    print('Imported transition multiplier values for scenario {}'.format(scenario.sid))

    # Import transition size distribution
    console.export_sheet('STSim_TransitionSizeDistribution', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            stratum = row['StratumID']
            sd = TransitionSizeDistribution.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                maximum_area=float(row['MaximumArea']),
                relative_amount=float(row['RelativeAmount'])
            )
            if type(iteration) is int:
                sd.iteration = iteration
            if type(timestep) is int:
                sd.timestep = timestep
            if len(stratum):
                sd.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()

            sd.save()
    print('Imported transition size distribution for scenario {}'.format(scenario.sid))

    # Import transition size prioritization
    console.export_sheet('STSim_TransitionSizePrioritization', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        priorities = [r for r in reader]
        if len(priorities):
            priorities = priorities[0]
            iteration = int(priorities['Iteration']) if len(priorities['Iteration']) else ''
            timestep = int(priorities['Timestep']) if len(priorities['Timestep']) else ''
            stratum = priorities['StratumID']
            transition_group = priorities['TransitionGroupID']
            sp = TransitionSizePrioritization.objects.create(
                scenario=scenario,
                priority=priorities['Priority']
            )
            if len(stratum):
                sp.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(transition_group):
                sp.transition_group = TransitionGroup.objects.filter(name__exact=transition_group,
                                                                     project=project).first()
            if type(iteration) is int:
                sp.iteration = iteration
            if type(timestep) is int:
                sp.timestep = timestep

            sp.save()
    print('Imported transition size prioritization for scenario {}'.format(scenario.sid))

    # Import transition spatial multipliers
    console.export_sheet('STSim_TransitionSpatialMultiplier', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            transition_multiplier_type = row['TransitionMultiplierTypeID']
            tsm = TransitionSpatialMultiplier.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(name__exact=row['TransitionGroupID'],
                                                                project=project).first(),
                transition_multiplier_file_name=row['MultiplierFileName']
            )

            if type(iteration) is int:
                tsm.iteration = iteration

            if type(timestep) is int:
                tsm.timestep = timestep

            if len(transition_multiplier_type):
                tsm.transition_multiplier_type = TransitionMultiplierType.objects.filter(
                    name__exact=transition_multiplier_type,
                    project=project).first()

            tsm.save()
    print('Imported transition spatial multipliers for scenario {}'.format(scenario.sid))

    # Import state attribute values
    console.export_sheet('STSim_StateAttributeValue', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            stratum = row['StratumID']
            secondary_stratum = row['SecondaryStratumID']
            stateclass = row['StateClassID']
            sav = StateAttributeValue.objects.create(
                scenario=scenario,
                state_attribute_type=StateAttributeType.objects.filter(
                    name__exact=row['StateAttributeTypeID'], project=project).first(),
                value=float(row['Value'])
            )
            if len(stratum):
                sav.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum):
                sav.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                        project=project).first()
            if len(stateclass):
                sav.stateclass = StateClass.objects.filter(name__exact=stateclass, project=project).first()
            if type(iteration) is int:
                sav.iteration = iteration
            if type(timestep) is int:
                sav.timestep = timestep

            sav.save()
    print('Imported state attribute values for scenario {}'.format(scenario.sid))

    # import transition attribute values
    console.export_sheet('STSim_TransitionAttributeValue', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            stratum = row['StratumID']
            secondary_stratum = row['SecondaryStratumID']
            stateclass = row['StateClassID']
            tav = TransitionAttributeValue.objects.create(
                scenario=scenario,
                transition_group=TransitionGroup.objects.filter(
                    name__exact=row['TransitionGroupID'], project=project).first(),
                transition_attribute_type=TransitionAttributeType.objects.filter(
                    name__exact=row['TransitionAttributeTypeID'], project=project).first(),
                value=float(row['Value'])
            )
            if len(stratum):
                tav.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum):
                tav.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                        project=project).first()
            if len(stateclass):
                tav.stateclass = StateClass.objects.filter(name__exact=stateclass, project=project).first()
            if type(iteration) is int:
                tav.iteration = iteration
            if type(timestep) is int:
                tav.timestep = timestep

            tav.save()
    print('Imported transition attribute values for scenario {}'.format(scenario.sid))

    # import transition attribute targets
    console.export_sheet('STSim_TransitionAttributeTarget', tmp_file, **kwgs)
    with open(tmp_file, 'r') as sheet:
        reader = csv.DictReader(sheet)
        for row in reader:
            iteration = int(row['Iteration']) if len(row['Iteration']) else ''
            timestep = int(row['Timestep']) if len(row['Timestep']) else ''
            stratum = row['StratumID']
            secondary_stratum = row['SecondaryStratumID']
            tat = TransitionAttributeTarget.objects.create(
                scenario=scenario,
                transition_attribute_type=TransitionAttributeType.objects.filter(
                    name__exact=row['TransitionAttributeTypeID'], project=project).first(),
                target=float(row['Amount'])
            )
            if len(stratum):
                tat.stratum = Stratum.objects.filter(name__exact=stratum, project=project).first()
            if len(secondary_stratum):
                tat.secondary_stratum = SecondaryStratum.objects.filter(name__exact=secondary_stratum,
                                                                        project=project).first()
            if type(iteration) is int:
                tat.iteration = iteration
            if type(timestep) is int:
                tat.timestep = timestep

            add_distribution_to(tat, row)
            tat.save()
    print('Imported transition attribute targets for scenario {}'.format(scenario.sid))

    # TODO - Determine whether this scenario is a dependency of another scenario, or has dependencies that rely on this

    if os.path.exists(tmp_file):
        os.remove(tmp_file)
