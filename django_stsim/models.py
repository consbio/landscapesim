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

    stratum_id = models.IntegerField()
    project = models.ForeignKey('Project', related_name='strata', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)


class StateClass(models.Model):

    stateclass_id = models.IntegerField()
    project = models.ForeignKey('Project', related_name='stateclasses', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    development = models.CharField(max_length=100)
    structure = models.CharField(max_length=100)


