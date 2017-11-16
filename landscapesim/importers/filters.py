from landscapesim.models import Stratum, StateClass, SecondaryStratum, TransitionGroup, TransitionType, AttributeGroup,\
    StateAttributeType, TransitionAttributeType


class Filter:
    """ A utility class for quickly collecting a foreign key for reports. """
    def __init__(self, model):
        self.model = model

    def get(self, name, project):
        return self.model.objects.filter(name__exact=name, project=project).first()


# Common filters
StratumFilter = Filter(Stratum)
StateClassFilter = Filter(StateClass)
SecondaryStratumFilter = Filter(SecondaryStratum)
TransitionGroupFilter = Filter(TransitionGroup)
TransitionTypeFilter = Filter(TransitionType)
AttributeGroupFilter = Filter(AttributeGroup)
StateAttributeFilter = Filter(StateAttributeType)
TransitionAttributeFilter = Filter(TransitionAttributeType)
