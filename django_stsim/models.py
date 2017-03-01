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
# TODO - The above todo would be better solved by using a separate django application interfacing with django_stsim


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


"""
    Project Definitions
"""


class Stratum(models.Model):

    project = models.ForeignKey('Project', related_name='strata', on_delete=models.CASCADE)
    stratum_id = models.IntegerField()
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class StateClass(models.Model):

    project = models.ForeignKey('Project', related_name='stateclasses', on_delete=models.CASCADE)
    stateclass_id = models.IntegerField()
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    development = models.CharField(max_length=100)
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
    pass


"""
    Advanced project definitions
"""
# TODO - Add advanced project definitions


class DistributionType(models.Model):

    pass


class AttributeGroup(models.Model):

    pass


class StateAttributeType(models.Model):

    pass


class TransitionAttributeType(models.Model):

    pass


"""
    Scenario configuration settings
"""


class RunControl(models.Model):
    scenario = models.ForeignKey('Scenario')
    min_iteration = models.IntegerField()
    max_iteration = models.IntegerField()
    min_timestep = models.IntegerField()
    max_timestep = models.IntegerField()
    is_spatial = models.BooleanField(default=False)


class OutputOption(models.Model):
    scenario = models.ForeignKey('Scenario')
    name = models.CharField(max_length=30)
    timestep = models.IntegerField(default=-1)
    enabled = models.BooleanField(default=False)


class DeterministicTransition(models.Model):

    scenario = models.ForeignKey('Scenario')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src_det')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_det')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest_det', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_det')
    age_min = models.IntegerField()
    age_max = models.IntegerField(null=True)
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


class TransitionTarget(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    stratum = models.ForeignKey('Stratum')
    transition_group = models.ForeignKey('TransitionGroup')
    value = models.FloatField()


class TransitionMultiplierValue(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField()
    iteration = models.IntegerField()
    transition_group = models.ForeignKey('TransitionGroup')
    value = models.FloatField()


class TransitionSizeDistribution(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    stratum = models.ForeignKey('Stratum', null=True)
    transition_group = models.ForeignKey('TransitionGroup')
    maximum_area = models.FloatField()
    relative_amount = models.FloatField()


class TransitionSizePrioritization(models.Model):

    scenario = models.ForeignKey('Scenario')
    priority = models.CharField(max_length=25)


class TransitionSpatialMultiplier(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    multiplier_type = models.ForeignKey('TransitionMultiplierType', null=True, blank=True)
    multiplier_file_path = models.FilePathField(match='*.tif')


class StateAttributeValue(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    state_attribute_type = models.ForeignKey('StateAttributeType')
    stateclass = models.ForeignKey('StateClass')
    stratum = models.ForeignKey('Stratum', null=True, blank=True)
    value = models.FloatField()


class TransitionAttributeValue(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    transition_group = models.ForeignKey('TransitionGroup')
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    stratum = models.ForeignKey('Stratum', null=True, blank=True)
    stateclass = models.ForeignKey('StateClass', null=True, blank=True)
    value = models.FloatField()


class TransitionAttributeTargets(models.Model):

    scenario = models.ForeignKey('Scenario')
    timestep = models.IntegerField(null=True, blank=True)
    iteration = models.IntegerField(null=True, blank=True)
    transition_attribute_type = models.ForeignKey('TransitionAttributeType')
    stratum = models.ForeignKey('Stratum', null=True, blank=True)
    value = models.FloatField()


class StateClassSummaryReport(models.Model):

    scenario = models.ForeignKey('Scenario')


class StateClassSummaryReportRow(models.Model):

    report = models.ForeignKey('StateClassSummaryReport', related_name='stateclass_results', on_delete=models.CASCADE)
    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum', related_name='stratum_scr')
    secondary_stratum = models.ForeignKey('Stratum', related_name='secondary_stratum_scr', blank=True, null=True)
    stateclass = models.ForeignKey('StateClass')
    amount = models.FloatField()
    proportion_of_landscape = models.FloatField()
    proportion_of_stratum = models.FloatField()


class TransitionSummaryReport(models.Model):

    scenario = models.ForeignKey('Scenario')


class TransitionSummaryReportRow(models.Model):
    """
        This report shows the amount of changes a stratum changes along a transition group, by time
    """

    report = models.ForeignKey('TransitionSummaryReport', related_name='transition_results', on_delete=models.CASCADE)
    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum', related_name='stratum_tr')
    secondary_stratum = models.ForeignKey('Stratum', related_name='secondary_stratum_tr', blank=True, null=True)
    transition_group = models.ForeignKey('TransitionGroup') # we capture the amount moved as a whole group
    amount = models.FloatField()


class TransitionByStateClassSummaryReport(models.Model):

    scenario = models.ForeignKey('Scenario')


class TransitionByStateClassSummaryReportRow(models.Model):
    """
        This report shows the state class (by stratum) changes along a transition type, by time
    """

    report = models.ForeignKey('TransitionByStateClassSummaryReport', related_name='transition_stateclass_results', on_delete=models.CASCADE)
    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum', related_name='stratum_tscr')
    secondary_stratum = models.ForeignKey('Stratum', related_name='secondary_stratum_tscr', blank=True, null=True)
    transition_type = models.ForeignKey('TransitionType') # we capture the amount moved specifically by timestep
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src_tscr')
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest_tscr')
    amount = models.FloatField()


# TODO - implement the remaining stsim reports below


class StateAttributeSummaryReport(models.Model):

    pass


class StateAttributeSummaryReportRow(models.Model):

    pass


class TransitionAttributeSummaryReport(models.Model):

    pass


class TransitionAttributeSummaryReportRow(models.Model):

    pass


"""
    django_stsim-specific tables for handling celery-related, asyncronous tasks
"""


class AsyncJobModel(models.Model):
    """
        A superclass for models that interact with celery backend results.
        Royally borrowed from ncdjango geoprocessing job model
    """
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
