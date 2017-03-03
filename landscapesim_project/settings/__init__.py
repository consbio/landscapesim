from django.core.exceptions import ImproperlyConfigured

try:
    from landscapesim_project.settings.custom import *
except ImportError:
    try:
        from landscapesim_project.settings.base import *
    except:
        raise ImproperlyConfigured("No custom.py declared, or there was an error in base.py")