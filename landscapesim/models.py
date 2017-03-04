"""
    The majority of the information we need is stored in the libraries themselves.
    These models take a snapshot of the library when imported so we don't have to
    extract them out each time.
"""
from django.db import models
import uuid
from celery.result import AsyncResult

# TODO - add a lookup field for the project when it is necessary.
#        could be something like "has_lookup" and a fk to the lookup table
#        WILL be needed for the landfire library, and then represented
#        in the serializer as a lookup map (i.e. KEY from stsim -> lookup value)
# TODO - The above todo would be better solved by using a separate django application interfacing with landscapesim


class Library(models.Model):

    name = models.CharField(max_length=50)
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

    # TODO - Add detection for scenario dependencies (as a console action)
    # Note - A scenario can itself have scenarios as dependencies, but a top level scenario won't be a dependency
    is_dependency_of = models.ForeignKey("self", null=True, blank=True)

"""
    Project Definitions
"""


class Terminology(models.Model):

    project = models.ForeignKey('Project', related_name='terminology', on_delete=models.CASCADE)
    amount_label = models.CharField(max_length=100)
    amount_units = models.CharField(max_length=100)
    state_label_x = models.CharField(max_length=100)
    state_label_y = models.CharField(max_length=100)
    primary_stratum_label = models.CharField(max_length=100)
    secondary_stratum_label = models.CharField(max_length=100)
    timestep_units = models.CharField(max_length=100)


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
    structure = models.CharField(max_length=100)


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

"""
    Scenario configuration settings
"""


class ScenarioMixin(models.Model):

    class Meta:
        abstract = True

    scenario = models.ForeignKey('Scenario')


class AgeMixin(models.Model):

    class Meta:
        abstract = True

    age_min = models.IntegerField(default=-1)
    age_max = models.IntegerField(default=-1)


class RunControl(models.Model):
    scenario = models.ForeignKey('Scenario')
    min_iteration = models.IntegerField()
    max_iteration = models.IntegerField()
    min_timestep = models.IntegerField()
    max_timestep = models.IntegerField()
    is_spatial = models.BooleanField(default=False)


class OutputOption(models.Model):
    scenario = models.ForeignKey('Scenario')
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

    scenario = models.ForeignKey('Scenario')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src_det')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_det')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest_det', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_det')
    location = models.CharField(max_length=10)


class Transition(models.Model):

    scenario = models.ForeignKey('Scenario')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest')
    transition_type = models.ForeignKey('TransitionType')
    probability = models.FloatField(default=0.0)
    age_reset = models.CharField(default='No', max_length=3)


class InitialConditionsNonSpatial(models.Model):

    scenario = models.ForeignKey('Scenario')
    total_amount = models.FloatField()
    num_cells = models.IntegerField()
    calc_from_dist = models.CharField(max_length=10)


class InitialConditionsNonSpatialDistribution(AgeMixin):

    scenario = models.ForeignKey('Scenario')
    stratum = models.ForeignKey('Stratum', related_name='stratum_ic')
    secondary_stratum = models.ForeignKey('SecondaryStratum', blank=True, null=True)
    stateclass = models.ForeignKey('StateClass')
    relative_amount = models.FloatField()


# TODO - Add distribution types, sd, min and max

class TimestepModelBase(models.Model):

    class Meta:
        abstract = True

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    stratum = models.ForeignKey('Stratum', null=True, blank=True)


class SecondaryStratumMixin(models.Model):

    class Meta:
        abstract = True

    secondary_stratum = models.ForeignKey('SecondaryStratum', null=True, blank=True)


class TransitionTarget(TimestepModelBase, SecondaryStratumMixin):

    transition_group = models.ForeignKey('TransitionGroup')
    target_area = models.FloatField()


class TransitionMultiplierValue(TimestepModelBase, SecondaryStratumMixin):

    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    transition_multiplier_type = models.ForeignKey('TransitionMultiplierType', null=True, blank=True)
    multiplier = models.FloatField()


class TransitionSizeDistribution(TimestepModelBase):

    transition_group = models.ForeignKey('TransitionGroup')
    maximum_area = models.FloatField()
    relative_amount = models.FloatField()


class TransitionSizePrioritization(TimestepModelBase):

    transition_group = models.ForeignKey('TransitionGroup', null=True, blank=True)
    priority = models.CharField(max_length=25)


class TransitionSpatialMultiplier(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    multiplier_type = models.ForeignKey('TransitionMultiplierType', null=True, blank=True)
    multiplier_file_path = models.FilePathField(match='*.tif')


class StateAttributeValue(TimestepModelBase, SecondaryStratumMixin):

    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    state_attribute_type = models.ForeignKey('StateAttributeType')
    value = models.FloatField()


class TransitionAttributeValue(TimestepModelBase, SecondaryStratumMixin):

    transition_group = models.ForeignKey('TransitionGroup')
    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    value = models.FloatField()


class TransitionAttributeTarget(TimestepModelBase, SecondaryStratumMixin):

    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    target = models.FloatField()

"""
    Reports
"""


class SummaryReportBase(models.Model):
    """
    Summary reports only need to know the scenario they were generated from
    """

    class Meta:
        abstract = True

    scenario = models.ForeignKey('Scenario')


class SummaryReportRowBase(models.Model):
    """
    All summary report rows require the following fields
    """

    class Meta:
        abstract = True

    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum')
    secondary_stratum = models.ForeignKey('SecondaryStratum', blank=True, null=True)
    amount = models.FloatField()


class StateClassSummaryReport(SummaryReportBase):

    pass


class StateClassSummaryReportRow(SummaryReportRowBase, AgeMixin):

    report = models.ForeignKey('StateClassSummaryReport', on_delete=models.CASCADE)
    stateclass = models.ForeignKey('StateClass')
    proportion_of_landscape = models.FloatField()
    proportion_of_stratum = models.FloatField()


class TransitionSummaryReport(SummaryReportBase):

    pass


class TransitionSummaryReportRow(SummaryReportRowBase, AgeMixin):

    report = models.ForeignKey('TransitionSummaryReport', on_delete=models.CASCADE)
    transition_group = models.ForeignKey('TransitionGroup')


class TransitionByStateClassSummaryReport(SummaryReportBase):

    pass


class TransitionByStateClassSummaryReportRow(SummaryReportRowBase):

    report = models.ForeignKey('TransitionByStateClassSummaryReport', on_delete=models.CASCADE)
    transition_type = models.ForeignKey('TransitionType')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_tscr')
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_tscr')


class StateAttributeSummaryReport(SummaryReportBase):

    pass


class StateAttributeSummaryReportRow(SummaryReportRowBase, AgeMixin):

    report = models.ForeignKey('StateAttributeSummaryReport', related_name='state_attribute_results', on_delete=models.CASCADE)
    state_attribute_type = models.ForeignKey('StateAttributeType')


class TransitionAttributeSummaryReport(SummaryReportBase):
    pass


class TransitionAttributeSummaryReportRow(SummaryReportRowBase, AgeMixin):

    report = models.ForeignKey('TransitionAttributeSummaryReport', related_name='transition_attribute_results', on_delete=models.CASCADE)
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


class GenerateReportModel(AsyncJobModel):

    report_name = models.CharField(max_length=100)
