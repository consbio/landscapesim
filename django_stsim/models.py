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


class Project(models.Model):

    library = models.ForeignKey('Library', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    pid = models.PositiveSmallIntegerField()


class Scenario(models.Model):

    project = models.ForeignKey('Project')
    name = models.CharField(max_length=50)
    is_result = models.BooleanField(default=False)
    sid = models.PositiveSmallIntegerField()