from django.apps import AppConfig

"""
    The goal of django_stsim is to expose a RESTful API to the information stored in a library,
    primarily the transition probabilities for populating tables and visualizations on the web.
"""


class DjangoStsimConfig(AppConfig):
    name = 'django_stsim'
