"""
    The majority of the information we need is stored in the libraries themselves.
    These models take a snapshot of the library when imported so we don't have to
    extract them out each time.
"""
import json
import os
import uuid

from celery.result import AsyncResult
from django.contrib.gis.db import models as gis_models
from django.db import models


class Library(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FilePathField(match="*.ssim")
    orig_file = models.FilePathField(match="*.ssim")
    tmp_file = models.FilePathField()


class Project(models.Model):
    library = models.ForeignKey('Library', related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    pid = models.PositiveSmallIntegerField()


class Scenario(models.Model):
    project = models.ForeignKey('Project', related_name='scenarios', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_result = models.BooleanField(default=False)
    sid = models.PositiveSmallIntegerField()
    parent = models.ForeignKey("self", null=True, blank=True)

    @property
    def library(self):
        return self.project.library

    @property
    def input_directory(self):
        return os.path.join(
            self.library.file + '.input', 'Scenario-' + str(self.sid), 'STSim_InitialConditionsSpatial'
        )

    @property
    def output_directory(self):
        return os.path.join(self.library.file + '.output', 'Scenario-' + str(self.sid), 'Spatial')

    @property
    def multiplier_directory(self):
        return os.path.join(
            self.library.file + '.input', 'Scenario-' + str(self.sid), 'STSim_TransitionSpatialMultiplier'
        )


class LibraryAssets(models.Model):
    library = models.OneToOneField('Library', related_name='assets', on_delete=models.CASCADE)
    stratum_path = models.FilePathField(match="*.tif")
    stateclass_path = models.FilePathField(match="*.tif")
    reporting_units_path = models.FilePathField(match="*.json")


class ReportingUnit(gis_models.Model):
    name = models.CharField(max_length=256)
    polygon = gis_models.GeometryField()


"""
    Project Definitions
"""


class Terminology(models.Model):
    project = models.OneToOneField('Project', related_name='terminology', on_delete=models.CASCADE)
    amount_label = models.CharField(max_length=100)
    amount_units = models.CharField(max_length=100)
    state_label_x = models.CharField(max_length=100)
    state_label_y = models.CharField(max_length=100)
    primary_stratum_label = models.CharField(max_length=100)
    secondary_stratum_label = models.CharField(max_length=100)
    timestep_units = models.CharField(max_length=100)


class DistributionType(models.Model):
    project = models.ForeignKey('Project', related_name='distribution_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    is_internal = models.BooleanField(default=True)  # Shouldn't need to be changed, but still good to capture


class Stratum(models.Model):
    project = models.ForeignKey('Project', related_name='strata', on_delete=models.CASCADE)
    stratum_id = models.IntegerField()
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class SecondaryStratum(models.Model):

    project = models.ForeignKey('Project', related_name='secondary_strata', on_delete=models.CASCADE)
    secondary_stratum_id = models.IntegerField()
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)


class StateClass(models.Model):
    project = models.ForeignKey('Project', related_name='stateclasses', on_delete=models.CASCADE)
    stateclass_id = models.IntegerField()
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    state_label_x = models.CharField(max_length=100)
    state_label_y = models.CharField(max_length=100)


class TransitionType(models.Model):

    project = models.ForeignKey('Project', related_name='transition_types', on_delete=models.CASCADE)
    transition_type_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class TransitionGroup(models.Model):
    project = models.ForeignKey('Project', related_name='transition_groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)


class TransitionTypeGroup(models.Model):
    project = models.ForeignKey('Project', related_name='transition_type_groups', on_delete=models.CASCADE)
    transition_type = models.ForeignKey('TransitionType')
    transition_group = models.ForeignKey('TransitionGroup')
    is_primary = models.CharField(max_length=3, default='')


class TransitionMultiplierType(models.Model):
    project = models.ForeignKey('Project', related_name='transition_multiplier_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class AttributeGroup(models.Model):
    project = models.ForeignKey('Project', related_name='attribute_groups')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


class StateAttributeType(models.Model):
    project = models.ForeignKey('Project', related_name='state_attributes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    attribute_group = models.ForeignKey('AttributeGroup', null=True, blank=True)
    units = models.CharField(max_length=50)
    description = models.CharField(max_length=100)


class TransitionAttributeType(models.Model):
    project = models.ForeignKey('Project', related_name='transition_attributes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    attribute_group = models.ForeignKey('AttributeGroup', null=True, blank=True)
    units = models.CharField(max_length=50)
    description = models.CharField(max_length=100)


""" Scenario configuration settings """

# Tables that could be included but are not currently used include:
# - Transition Order
# - Transition Spread Distribution
# - Transition Patch Prioritization
# - Transition Direction Multipliers
# - DigitalElevationModel setting
# - Transition Slope Multipliers
# - Transition Adjacency Setting/Multipliers


class AgeMixin(models.Model):
    class Meta:
        abstract = True

    age_min = models.IntegerField(default=-1)
    age_max = models.IntegerField(default=-1)


class DistributionValue(models.Model):
    scenario = models.ForeignKey('Scenario', related_name='distribution_values')
    distribution_type = models.ForeignKey('DistributionType')
    dmin = models.FloatField(null=True, blank=True)
    dmax = models.FloatField()
    relative_frequency = models.FloatField(null=True, blank=True)


class RunControl(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='run_control')
    min_iteration = models.IntegerField()
    max_iteration = models.IntegerField()
    min_timestep = models.IntegerField()
    max_timestep = models.IntegerField()
    is_spatial = models.BooleanField(default=False)


class OutputOption(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='output_options')
    sum_sc = models.BooleanField(default=False)
    sum_sc_t = models.IntegerField(null=True)
    sum_sc_zeros = models.BooleanField(default=False)
    raster_sc = models.BooleanField(default=False)
    raster_sc_t = models.IntegerField(null=True)
    sum_tr = models.BooleanField(default=False)
    sum_tr_t = models.IntegerField(null=True)
    sum_tr_interval = models.BooleanField(default=False)
    raster_tr = models.BooleanField(default=False)
    raster_tr_t = models.IntegerField(null=True)
    sum_trsc = models.BooleanField(default=False)
    sum_trsc_t = models.IntegerField(null=True)
    sum_sa = models.BooleanField(default=False)
    sum_sa_t = models.IntegerField(null=True)
    raster_sa = models.BooleanField(default=False)
    raster_sa_t = models.IntegerField(null=True)
    sum_ta = models.BooleanField(default=False)
    sum_ta_t = models.IntegerField(null=True)
    raster_ta = models.BooleanField(default=False)
    raster_ta_t = models.IntegerField(null=True)
    raster_strata = models.BooleanField(default=False)
    raster_strata_t = models.IntegerField(null=True)
    raster_age = models.BooleanField(default=False)
    raster_age_t = models.IntegerField(null=True)
    raster_tst = models.BooleanField(default=True)
    raster_tst_t = models.IntegerField(null=True)
    raster_aatp = models.BooleanField(default=False)
    raster_aatp_t = models.IntegerField(null=True)


class DeterministicTransition(AgeMixin):
    scenario = models.ForeignKey('Scenario', related_name='deterministic_transitions')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src_det')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_det')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest_det', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_det')
    location = models.CharField(max_length=10)


class Transition(AgeMixin):
    scenario = models.ForeignKey('Scenario', related_name='transitions')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest')
    transition_type = models.ForeignKey('TransitionType')
    probability = models.FloatField()
    proportion = models.FloatField(null=True, blank=True)
    age_relative = models.FloatField(null=True, blank=True)
    age_reset = models.BooleanField(default=False)
    tst_min = models.FloatField(null=True, blank=True)
    tst_max = models.FloatField(null=True, blank=True)
    tst_relative = models.FloatField(null=True, blank=True)


class InitialConditionsNonSpatial(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='initial_conditions_nonspatial_settings')
    total_amount = models.FloatField()
    num_cells = models.IntegerField()
    calc_from_dist = models.BooleanField(default=False)


class InitialConditionsNonSpatialDistribution(AgeMixin):
    scenario = models.ForeignKey('Scenario', related_name='initial_conditions_nonspatial_distributions')
    stratum = models.ForeignKey('Stratum', related_name='stratum_ic')
    secondary_stratum = models.ForeignKey('SecondaryStratum', blank=True, null=True)
    stateclass = models.ForeignKey('StateClass')
    relative_amount = models.FloatField()


class InitialConditionsSpatial(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='initial_conditions_spatial_settings')
    num_rows = models.IntegerField()
    num_cols = models.IntegerField()
    num_cells = models.IntegerField()
    cell_size = models.IntegerField()
    cell_size_units = models.CharField(max_length=100)
    cell_area = models.FloatField()
    cell_area_override = models.BooleanField(default=False)
    xll_corner = models.FloatField()
    yll_corner = models.FloatField()
    srs = models.CharField(max_length=500)    # spatial reference
    stratum_file_name = models.CharField(max_length=100)
    secondary_stratum_file_name = models.CharField(max_length=100)
    stateclass_file_name = models.CharField(max_length=100)
    age_file_name = models.CharField(max_length=100)


class TimestepModelBase(models.Model):
    class Meta:
        abstract = True

    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    stratum = models.ForeignKey('Stratum', null=True, blank=True)


class DistributionMixin(models.Model):
    class Meta:
        abstract = True

    distribution_type = models.ForeignKey('DistributionType', null=True, blank=True)
    distribution_sd = models.FloatField(null=True, blank=True)
    distribution_min = models.FloatField(null=True, blank=True)
    distribution_max = models.FloatField(null=True, blank=True)


class SecondaryStratumMixin(models.Model):
    class Meta:
        abstract = True

    secondary_stratum = models.ForeignKey('SecondaryStratum', null=True, blank=True)


class TransitionTarget(TimestepModelBase, SecondaryStratumMixin, DistributionMixin):
    scenario = models.ForeignKey('Scenario', related_name='transition_targets')
    transition_group = models.ForeignKey('TransitionGroup')
    target_area = models.FloatField()


class TransitionMultiplierValue(TimestepModelBase, SecondaryStratumMixin, DistributionMixin):
    scenario = models.ForeignKey('Scenario', related_name='transition_multiplier_values')
    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    transition_multiplier_type = models.ForeignKey('TransitionMultiplierType', null=True, blank=True)
    multiplier = models.FloatField()


class TransitionSizeDistribution(TimestepModelBase):
    scenario = models.ForeignKey('Scenario', related_name='transition_size_distributions')
    transition_group = models.ForeignKey('TransitionGroup')
    maximum_area = models.FloatField()
    relative_amount = models.FloatField()


class TransitionSizePrioritization(TimestepModelBase):
    scenario = models.ForeignKey('Scenario', related_name='transition_size_prioritizations')
    transition_group = models.ForeignKey('TransitionGroup', null=True, blank=True)
    priority = models.CharField(max_length=25)


class TransitionSpatialMultiplier(models.Model):

    scenario = models.ForeignKey('Scenario', related_name='transition_spatial_multipliers')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    transition_multiplier_type = models.ForeignKey('TransitionMultiplierType', null=True, blank=True)
    transition_multiplier_file_name = models.CharField(max_length=100)


class StateAttributeValue(TimestepModelBase, SecondaryStratumMixin):
    scenario = models.ForeignKey('Scenario', related_name='state_attribute_values')
    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    state_attribute_type = models.ForeignKey('StateAttributeType')
    value = models.FloatField()


class TransitionAttributeValue(TimestepModelBase, SecondaryStratumMixin):
    scenario = models.ForeignKey('Scenario', related_name='transition_attribute_values')
    transition_group = models.ForeignKey('TransitionGroup')
    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    value = models.FloatField()


class TransitionAttributeTarget(TimestepModelBase, SecondaryStratumMixin, DistributionMixin):
    scenario = models.ForeignKey('Scenario', related_name='transition_attribute_targets')
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    target = models.FloatField()

"""
    Reports
"""


class SummaryReportRowBase(models.Model):
    """ All summary report rows require the following fields """
    class Meta:
        abstract = True

    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum')
    secondary_stratum = models.ForeignKey('SecondaryStratum', blank=True, null=True)
    amount = models.FloatField()


class StateClassSummaryReport(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='stateclass_summary_report', on_delete=models.CASCADE)


class StateClassSummaryReportRow(SummaryReportRowBase, AgeMixin):
    report = models.ForeignKey('StateClassSummaryReport', related_name='results', on_delete=models.CASCADE)
    stateclass = models.ForeignKey('StateClass')
    proportion_of_landscape = models.FloatField()
    proportion_of_stratum = models.FloatField()


class TransitionSummaryReport(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='transition_summary_report', on_delete=models.CASCADE)


class TransitionSummaryReportRow(SummaryReportRowBase, AgeMixin):
    report = models.ForeignKey('TransitionSummaryReport', related_name='results', on_delete=models.CASCADE)
    transition_group = models.ForeignKey('TransitionGroup')


class TransitionByStateClassSummaryReport(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='transition_by_sc_summary_report', on_delete=models.CASCADE)


class TransitionByStateClassSummaryReportRow(SummaryReportRowBase):
    report = models.ForeignKey('TransitionByStateClassSummaryReport', related_name='results', on_delete=models.CASCADE)
    transition_type = models.ForeignKey('TransitionType')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_tscr')
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_tscr')


class StateAttributeSummaryReport(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='state_attribute_summary_report', on_delete=models.CASCADE)


class StateAttributeSummaryReportRow(SummaryReportRowBase, AgeMixin):
    report = models.ForeignKey('StateAttributeSummaryReport', related_name='results', on_delete=models.CASCADE)
    state_attribute_type = models.ForeignKey('StateAttributeType')


class TransitionAttributeSummaryReport(models.Model):
    scenario = models.OneToOneField('Scenario', related_name='transition_attribute_summary_report', on_delete=models.CASCADE)


class TransitionAttributeSummaryReportRow(SummaryReportRowBase, AgeMixin):
    report = models.ForeignKey('TransitionAttributeSummaryReport', related_name='results', on_delete=models.CASCADE)
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')

"""
    Async models for handling celery-related tasks
"""


class AsyncJobModel(models.Model):
    """
        An abstract class for models that interact with celery backend results.
    """
    class Meta:
        abstract = True

    uuid = models.CharField(max_length=36, default=uuid.uuid4, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    celery_id = models.CharField(max_length=100)
    inputs = models.TextField(null=False, default="{}")
    outputs = models.TextField(null=False, default="{}")

    @property
    def status(self):
        """ The status of the celery task for this job. """

        return AsyncResult(self.celery_id).status.lower()


class RunScenarioModel(AsyncJobModel):
    parent_scenario = models.ForeignKey('Scenario', related_name='parent_scenario')
    result_scenario = models.ForeignKey('Scenario', related_name='result_scenario', null=True)
    model_status = models.TextField(null=False, default='complete')

    @property
    def progress(self):
        """ The progress of the model run. """

        if self.result_scenario:
            # Scan output directory for progress of the model run by 
            # checking the number of files created.
            config = json.loads(self.inputs)['config']
            run_control = config['run_control']

            # Non-spatial runs have no progress
            if run_control.get('IsSpatial') != 'Yes':
                return None

            iterations = run_control['MaximumIteration']
            timesteps = run_control['MaximumTimestep']
            max_num_files = iterations * timesteps + iterations  # t-0 is included in file directory
            outputs = [x for x in os.listdir(self.result_scenario.output_directory) if '.tif' in x]
            progress = len(outputs) / max_num_files
            return progress
        else:
            return None


class ScenarioInputServices(models.Model):
    """
        ncdjango services for a scenario with spatial inputs. Allows input rasters to be utilized in maps and 3D scenes.
    """
    scenario = models.OneToOneField('Scenario', related_name='scenario_input_services')
    stratum = models.ForeignKey('ncdjango.Service', related_name='stratum_input_service', null=True)
    secondary_stratum = models.ForeignKey('ncdjango.Service', related_name='secondary_stratum_input_service', null=True)
    stateclass = models.ForeignKey('ncdjango.Service', related_name='stateclass_input_service', null=True)
    age = models.ForeignKey('ncdjango.Service', related_name='age_input_service', null=True)


class ScenarioOutputServices(models.Model):
    """
        ncdjango services for raster outputs from a result scenario. Allows time-series rasters to be animated in maps.
    """
    scenario = models.OneToOneField('Scenario', related_name='scenario_output_services')
    stateclass = models.ForeignKey('ncdjango.Service', related_name='stateclass_output_service', null=True)
    transition_group = models.ForeignKey('ncdjango.Service', related_name='transition_group_output_service', null=True)
    age = models.ForeignKey('ncdjango.Service', related_name='age_output_service', null=True)
    tst = models.ForeignKey('ncdjango.Service', related_name='tst_output_service', null=True)
    stratum = models.ForeignKey('ncdjango.Service', related_name='stratum_output_service', null=True)
    state_attribute = models.ForeignKey('ncdjango.Service', related_name='state_attribute_output_service', null=True)
    transition_attribute = models.ForeignKey(
        'ncdjango.Service', related_name='transition_attribute_output_service', null=True
    )
    avg_annual_transition_group_probability = models.ForeignKey(
        'ncdjango.Service', related_name='avg_annual_transition_probability_output_service', null=True
    )
