from django.db import models

# Create your models here.
"""
    The majority of the information we need is stored in the libraries themselves,
    so its not very useful to extract the information out of the library itself.
"""


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
    transition_type_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class TransitionGroup(models.Model):

    project = models.ForeignKey('Project', related_name='transition_groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    transition_types = models.ManyToManyField(TransitionType)
    # TODO - use the TransitionTypeGroup sheet to build the many to many relationship


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
    """
        Created when a stateclass-summary report is generated
    """

    report = models.ForeignKey('StateClassSummaryReport', related_name='stateclass_results', on_delete=models.CASCADE)
    iteration = models.IntegerField()
    timestep = models.IntegerField()
    stratum = models.ForeignKey('Stratum', related_name='stratum')
    secondary_stratum = models.ForeignKey('Stratum', related_name='secondary_stratum')
    stateclass = models.ForeignKey('StateClass')
    amount = models.FloatField()
    proportion_of_landscape = models.FloatField()
    proportion_of_stratum = models.FloatField()


    