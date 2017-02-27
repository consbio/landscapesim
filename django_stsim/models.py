from django.db import models

# Create your models here.
"""
    The majority of the information we need is stored in the libraries themselves.
    These models take a snapshot of the library when imported so we don't have to
    extract them out each time.
"""

# TODO - add a lookup field for the project when it is necessary.
#        could be something like "has_lookup" and a fk to the lookup table
#        WILL be needed for the landfire library, and then represented
#        in the serializer as a lookup map (i.e. KEY from stsim -> lookup value)


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


class RunControl(models.Model):

    scenario = models.ForeignKey('Scenario')
    min_iteration = models.IntegerField()
    max_iteration = models.IntegerField()
    min_timestep = models.IntegerField()
    max_timestep = models.IntegerField()
    is_spatial = models.BooleanField(default=False)


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


class Transition(models.Model):
    """
        NOTE: probability will store the initial values from the library when imported
    """

    scenario = models.ForeignKey('Scenario')
    stratum_src = models.ForeignKey('Stratum', related_name='stratum_src')
    stateclass_src = models.ForeignKey('StateClass', related_name='stateclass_src')
    stratum_dest = models.ForeignKey('Stratum', related_name='stratum_dest', on_delete=models.CASCADE, blank=True, null=True)
    stateclass_dest = models.ForeignKey('StateClass', related_name='stateclass_dest')
    transition_type = models.ForeignKey('TransitionType')
    probability = models.FloatField(default=0.0)
    age_reset = models.CharField(default='No', max_length=3)


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


class OutputOption(models.Model):

    scenario = models.ForeignKey('Scenario')
    name = models.CharField(max_length=30)
    timestep = models.IntegerField(default=-1)
    enabled = models.BooleanField(default=False)

