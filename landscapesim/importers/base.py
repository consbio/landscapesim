
class Filter:
    """ A utility class for quickly collecting a foreign key for reports. """
    def __init__(self, model):
        self.model = model

    def get(self, name, project):
        return self.model.objects.filter(name__exact=name, project=project).first()
