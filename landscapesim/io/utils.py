import csv
import os
import uuid

from landscapesim import models
from landscapesim.io.services import ServiceGenerator
from landscapesim.io.types import default_int, default_float, empty_or_yes_to_bool

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


class ProjectImporter:

    def __init__(self, project, console):
        self.project = project
        self.console = console

    def process_project_definitions(self):
        tmp_file = get_random_csv(self.project.library.tmp_file)
        kwgs = {'pid': self.project.pid, 'overwrite': True, 'orig': True}

        # Import terminology
        self.console.export_sheet('STSim_Terminology', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            terms = [r for r in reader][0]
            models.Terminology.objects.create(
                project=self.project,
                amount_label=terms['AmountLabel'],
                amount_units=terms['AmountUnits'],
                state_label_x=terms['StateLabelX'],
                state_label_y=terms['StateLabelY'],
                primary_stratum_label=terms['PrimaryStratumLabel'],
                secondary_stratum_label=terms['SecondaryStratumLabel'],
                timestep_units=terms['TimestepUnits']
            )
        print('Imported terminology for project {}.'.format(self.project.name))

        self.console.export_sheet('Stats_DistributionType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.DistributionType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description'],
                    is_internal=empty_or_yes_to_bool(row['IsInternal'])
                )
        print('Imported distribution types for project {}.'.format(self.project.name))

        # Import strata
        self.console.export_sheet('STSim_Stratum', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.Stratum.objects.create(
                    stratum_id=default_int(row['ID']),
                    project=self.project,
                    name=row['Name'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported strata for project {}.'.format(self.project.name))

        # import secondary strata
        self.console.export_sheet('STSim_SecondaryStratum', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.SecondaryStratum.objects.create(
                    project=self.project,
                    secondary_stratum_id=default_int(row['ID']),
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported secondary strata for project {}.'.format(self.project.name))

        # import stateclasses
        self.console.export_sheet('STSim_StateClass', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.StateClass.objects.create(
                    stateclass_id=default_int(row['ID']),
                    project=self.project,
                    name=row['Name'],
                    state_label_x=row['StateLabelXID'],
                    state_label_y=row['StateLabelYID'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported state classes for project {}.'.format(self.project.name))

        # import transition types
        self.console.export_sheet('STSim_TransitionType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionType.objects.create(
                    project=self.project,
                    transition_type_id=default_int(row['ID']),
                    name=row['Name'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported transition types for project {}.'.format(self.project.name))

        # import transition groups
        self.console.export_sheet('STSim_TransitionGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionGroup.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported transition groups for project {}.'.format(self.project.name))

        # map transition groups to transition types
        self.console.export_sheet('STSim_TransitionTypeGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionTypeGroup.objects.create(
                    project=self.project,
                    transition_type=models.TransitionType.objects.filter(
                        name__exact=row['TransitionTypeID'], project=self.project
                    ).first(),
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=self.project
                    ).first(),
                    is_primary=row['IsPrimary']
                )
        print('Imported transition type groups for project {}.'.format(self.project.name))

        # import transition multiplier types
        self.console.export_sheet('STSim_TransitionMultiplierType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionMultiplierType.objects.create(
                    project=self.project,
                    name=row['Name']
                )
        print('Imported transition multiplier types for project {}.'.format(self.project.name))

        # Import attribute groups
        self.console.export_sheet('STSim_AttributeGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.AttributeGroup.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported attribute groups for project {}.'.format(self.project.name))

        # Import state attribute types
        self.console.export_sheet('STSim_StateAttributeType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.StateAttributeType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    attribute_group=models.AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                                         project=self.project).first(),
                    units=row['Units'],
                    description=row['Description']
                )
        print('Imported state attribute types for project {}.'.format(self.project.name))

        # Import transition attribute types
        self.console.export_sheet('STSim_TransitionAttributeType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionAttributeType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    attribute_group=models.AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                                         project=self.project).first(),
                    units=row['Units'],
                    description=row['Description']
                )
        print('Imported transition attribute types for project {}.'.format(self.project.name))


class ScenarioImporter:

    def __init__(self, scenario: models.Scenario, console):
        self.scenario = scenario
        self.console = console

    def process_run_control(self):
        tmp_file = get_random_csv(self.scenario.library.tmp_file)
        kwgs = {'sid': self.scenario.sid, 'overwrite': True, 'orig': not self.scenario.is_result}

        # import initial run control
        self.console.export_sheet('STSim_RunControl', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            run_options = [r for r in reader][0]
            models.RunControl.objects.create(
                scenario=self.scenario,
                min_iteration=int(run_options['MinimumIteration']),
                max_iteration=int(run_options['MaximumIteration']),
                min_timestep=int(run_options['MinimumTimestep']),
                max_timestep=int(run_options['MaximumTimestep']),
                is_spatial=empty_or_yes_to_bool(run_options['IsSpatial'])
            )
        print('Imported run control for scenario {}'.format(self.scenario.sid))

        # import output options
        self.console.export_sheet('STSim_OutputOptions', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            output_options = [r for r in reader]
            oo = models.OutputOption.objects.create(scenario=self.scenario)
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
        print('Imported output options for scenario {}'.format(self.scenario.sid))

    def process_scenario_inputs(self, create_input_services=True):
        tmp_file = get_random_csv(self.scenario.library.tmp_file)
        project = self.scenario.project
        kwgs = {'sid': self.scenario.sid, 'overwrite': True, 'orig': not self.scenario.is_result}

        def add_distribution_to(obj, entry):
            """ Simple helper for adding distributions to models that use them """

            dist_type = entry['DistributionType']
            if len(dist_type):
                obj.distribution_type = models.DistributionType.objects.filter(
                    name__exact=dist_type, project=project
                ).first()
                if len(entry['DistributionSD']):
                    obj.distribution_sd = float(entry['DistributionSD'])
                if len(entry['DistributionMin']):
                    obj.distribution_min = float(entry['DistributionMin'])
                if len(entry['DistributionMax']):
                    obj.distribution_max = float(entry['DistributionMax'])

        self.console.export_sheet('Stats_DistributionValue', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                dmin = float(row['Min']) if len(row['Min']) else ''
                relative_frequency = float(row['RelativeFrequency']) if len(row['RelativeFrequency']) else ''
                dv = models.DistributionValue.objects.create(
                    scenario=self.scenario,
                    distribution_type=models.DistributionType.objects.filter(
                        name__exact=row['DistributionTypeID'], project=project
                    ).first(),
                    dmax=float(row['Max'])
                )
                if type(dmin) is float:
                    dv.dmin = dmin
                if type(relative_frequency) is float:
                    dv.relative_frequency = relative_frequency

                dv.save()
        print('Imported distribution values for scenario {}'.format(self.scenario.sid))

        self.console.export_sheet('STSim_DeterministicTransition', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                stratum_dest = row['StratumIDDest']
                t = models.DeterministicTransition.objects.create(
                    scenario=self.scenario,
                    stratum_src=models.Stratum.objects.filter(
                        name__exact=row['StratumIDSource'], project=project
                    ).first(),
                    stratum_dest=models.Stratum.objects.filter(
                        name__exact=row['StratumIDDest'], project=project
                    ).first(),
                    stateclass_src=models.StateClass.objects.filter(
                        name__exact=row['StateClassIDSource'], project=project
                    ).first(),
                    stateclass_dest=models.StateClass.objects.filter(
                        name__exact=row['StateClassIDDest'], project=project
                    ).first(),
                    age_min=default_int(row['AgeMin']),
                    age_max=default_int(row['AgeMax']),
                    location=row['Location']
                )
                if len(stratum_dest):
                    t.stratum_dest = models.Stratum.objects.filter(name__exact=stratum_dest, project=project).first()
                t.save()
        print('Imported deterministic transitions for scenario {}'.format(self.scenario.sid))

        # import initial probabilistic transition probabilities
        self.console.export_sheet('STSim_Transition', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                stratum_dest = row['StratumIDDest']
                t = models.Transition.objects.create(  # omit stratum_dest, no change in stratum per timestep
                    scenario=self.scenario,
                    stratum_src=models.Stratum.objects.filter(
                        name__exact=row['StratumIDSource'], project=project
                    ).first(),
                    stateclass_src=models.StateClass.objects.filter(
                        name__exact=row['StateClassIDSource'], project=project
                    ).first(),
                    stateclass_dest=models.StateClass.objects.filter(
                        name__exact=row['StateClassIDDest'], project=project
                    ).first(),
                    transition_type=models.TransitionType.objects.filter(
                        name__exact=row['TransitionTypeID'], project=project
                    ).first(),
                    probability=float(row['Probability']),
                    age_reset=empty_or_yes_to_bool(row['AgeReset'])
                )
                if len(stratum_dest):
                    t.stratum_dest = models.Stratum.objects.filter(name__exact=stratum_dest, project=project).first()
                    t.save()

        print('Imported transition probabilities for scenario {}'.format(self.scenario.sid))

        # Import initial conditions non spatial configuration
        self.console.export_sheet('STSim_InitialConditionsNonSpatial', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            conditions = [r for r in reader][0]
            models.InitialConditionsNonSpatial.objects.create(
                scenario=self.scenario,
                total_amount=float(conditions['TotalAmount']),
                num_cells=int(conditions['NumCells']),
                calc_from_dist=empty_or_yes_to_bool(conditions['CalcFromDist'])
            )
        print('Imported initial conditions for scenario {}'.format(self.scenario.sid))

        # Import initial conditions non spatial values
        self.console.export_sheet('STSim_InitialConditionsNonSpatialDistribution', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                secondary_stratum = row['SecondaryStratumID']
                ic = models.InitialConditionsNonSpatialDistribution.objects.create(
                    scenario=self.scenario,
                    stratum=models.Stratum.objects.filter(
                        name__exact=row['StratumID'], project=project).first(),
                    stateclass=models.StateClass.objects.filter(
                        name__exact=row['StateClassID'], project=project
                    ).first(),
                    relative_amount=float(row['RelativeAmount']),
                    age_min=default_int(row['AgeMin']),
                    age_max=default_int(row['AgeMax'])
                )
                if len(secondary_stratum):
                    ic.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                ic.save()
        print('Imported initial conditions values for scenario {}'.format(self.scenario.sid))

        # Import initial conditions spatial
        self.console.export_sheet('STSim_InitialConditionsSpatial', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            init = [r for r in reader]
            if len(init):
                init = init[0]
                models.InitialConditionsSpatial.objects.create(
                    scenario=self.scenario,
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
                if create_input_services:
                    ServiceGenerator(self.scenario).create_input_services()

        print('Imported initial conditions spatial settings for scenario {}'.format(self.scenario.sid))

        # Import transition targets
        self.console.export_sheet('STSim_TransitionTarget', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                stratum = row['StratumID']
                secondary_stratum = row['SecondaryStratumID']
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                tt = models.TransitionTarget.objects.create(
                    scenario=self.scenario,
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=project
                    ).first(),
                    target_area=float(row['Amount'])
                )
                if type(iteration) is int:
                    tt.iteration = iteration
                if type(timestep) is int:
                    tt.timestep = timestep
                if len(stratum):
                    tt.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(secondary_stratum):
                    tt.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                add_distribution_to(tt, row)
                tt.save()
        print('Imported transition targets for scenario {}'.format(self.scenario.sid))

        # Import transition multiplier values
        self.console.export_sheet('STSim_TransitionMultiplierValue', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                stratum = row['StratumID']
                secondary_stratum = row['SecondaryStratumID']
                stateclass = row['StateClassID']
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                transition_multiplier_type = row['TransitionMultiplierTypeID']
                tm = models.TransitionMultiplierValue.objects.create(
                    scenario=self.scenario,
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=project
                    ).first(),
                    multiplier=float(row['Amount'])
                )
                if len(stratum):
                    tm.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(secondary_stratum):
                    tm.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                if len(stateclass):
                    tm.stateclass = models.StateClass.objects.filter(name__exact=stateclass, project=project).first()
                if type(iteration) is int:
                    tm.iteration = iteration
                if type(timestep) is int:
                    tm.timestep = timestep
                if len(transition_multiplier_type):
                    tm.transition_multiplier_type = models.TransitionMultiplierType.objects.filter(
                        name__exact=transition_multiplier_type, project=project).first()
                add_distribution_to(tm, row)
                tm.save()
        print('Imported transition multiplier values for scenario {}'.format(self.scenario.sid))

        # Import transition size distribution
        self.console.export_sheet('STSim_TransitionSizeDistribution', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                stratum = row['StratumID']
                sd = models.TransitionSizeDistribution.objects.create(
                    scenario=self.scenario,
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=project).first(),
                    maximum_area=float(row['MaximumArea']),
                    relative_amount=float(row['RelativeAmount'])
                )
                if type(iteration) is int:
                    sd.iteration = iteration
                if type(timestep) is int:
                    sd.timestep = timestep
                if len(stratum):
                    sd.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()

                sd.save()
        print('Imported transition size distribution for scenario {}'.format(self.scenario.sid))

        # Import transition size prioritization
        self.console.export_sheet('STSim_TransitionSizePrioritization', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            priorities = [r for r in reader]
            if len(priorities):
                priorities = priorities[0]
                iteration = int(priorities['Iteration']) if len(priorities['Iteration']) else ''
                timestep = int(priorities['Timestep']) if len(priorities['Timestep']) else ''
                stratum = priorities['StratumID']
                transition_group = priorities['TransitionGroupID']
                sp = models.TransitionSizePrioritization.objects.create(
                    scenario=self.scenario,
                    priority=priorities['Priority']
                )
                if len(stratum):
                    sp.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(transition_group):
                    sp.transition_group = models.TransitionGroup.objects.filter(
                        name__exact=transition_group, project=project
                    ).first()
                if type(iteration) is int:
                    sp.iteration = iteration
                if type(timestep) is int:
                    sp.timestep = timestep

                sp.save()
        print('Imported transition size prioritization for scenario {}'.format(self.scenario.sid))

        # Import transition spatial multipliers
        self.console.export_sheet('STSim_TransitionSpatialMultiplier', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                transition_multiplier_type = row['TransitionMultiplierTypeID']
                tsm = models.TransitionSpatialMultiplier.objects.create(
                    scenario=self.scenario,
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=project
                    ).first(),
                    transition_multiplier_file_name=row['MultiplierFileName']
                )

                if type(iteration) is int:
                    tsm.iteration = iteration

                if type(timestep) is int:
                    tsm.timestep = timestep

                if len(transition_multiplier_type):
                    tsm.transition_multiplier_type = models.TransitionMultiplierType.objects.filter(
                        name__exact=transition_multiplier_type,
                        project=project).first()

                tsm.save()
        print('Imported transition spatial multipliers for scenario {}'.format(self.scenario.sid))

        # Import state attribute values
        self.console.export_sheet('STSim_StateAttributeValue', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                stratum = row['StratumID']
                secondary_stratum = row['SecondaryStratumID']
                stateclass = row['StateClassID']
                sav = models.StateAttributeValue.objects.create(
                    scenario=self.scenario,
                    state_attribute_type=models.StateAttributeType.objects.filter(
                        name__exact=row['StateAttributeTypeID'], project=project).first(),
                    value=float(row['Value'])
                )
                if len(stratum):
                    sav.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(secondary_stratum):
                    sav.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                if len(stateclass):
                    sav.stateclass = models.StateClass.objects.filter(name__exact=stateclass, project=project).first()
                if type(iteration) is int:
                    sav.iteration = iteration
                if type(timestep) is int:
                    sav.timestep = timestep

                sav.save()
        print('Imported state attribute values for scenario {}'.format(self.scenario.sid))

        # import transition attribute values
        self.console.export_sheet('STSim_TransitionAttributeValue', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                stratum = row['StratumID']
                secondary_stratum = row['SecondaryStratumID']
                stateclass = row['StateClassID']
                tav = models.TransitionAttributeValue.objects.create(
                    scenario=self.scenario,
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=project).first(),
                    transition_attribute_type=models.TransitionAttributeType.objects.filter(
                        name__exact=row['TransitionAttributeTypeID'], project=project).first(),
                    value=float(row['Value'])
                )
                if len(stratum):
                    tav.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(secondary_stratum):
                    tav.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                if len(stateclass):
                    tav.stateclass = models.StateClass.objects.filter(name__exact=stateclass, project=project).first()
                if type(iteration) is int:
                    tav.iteration = iteration
                if type(timestep) is int:
                    tav.timestep = timestep

                tav.save()
        print('Imported transition attribute values for scenario {}'.format(self.scenario.sid))

        # import transition attribute targets
        self.console.export_sheet('STSim_TransitionAttributeTarget', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                iteration = int(row['Iteration']) if len(row['Iteration']) else ''
                timestep = int(row['Timestep']) if len(row['Timestep']) else ''
                stratum = row['StratumID']
                secondary_stratum = row['SecondaryStratumID']
                tat = models.TransitionAttributeTarget.objects.create(
                    scenario=self.scenario,
                    transition_attribute_type=models.TransitionAttributeType.objects.filter(
                        name__exact=row['TransitionAttributeTypeID'], project=project).first(),
                    target=float(row['Amount'])
                )
                if len(stratum):
                    tat.stratum = models.Stratum.objects.filter(name__exact=stratum, project=project).first()
                if len(secondary_stratum):
                    tat.secondary_stratum = models.SecondaryStratum.objects.filter(
                        name__exact=secondary_stratum, project=project
                    ).first()
                if type(iteration) is int:
                    tat.iteration = iteration
                if type(timestep) is int:
                    tat.timestep = timestep

                add_distribution_to(tat, row)
                tat.save()
        print('Imported transition attribute targets for scenario {}'.format(self.scenario.sid))
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
