from landscapesim.models import Stratum, StateClass, SecondaryStratum, TransitionGroup, TransitionType, AttributeGroup,\
    StateAttributeType, TransitionAttributeType, TransitionMultiplierType, DistributionType


class ProjectFilter:
    """ A utility class for quickly collecting a foreign key from project-level definitions """
    def __init__(self, model):
        self.model = model

    def get(self, name, project):
        return self.model.objects.filter(name__exact=name, project=project).first()


# Common filters
StratumFilter = ProjectFilter(Stratum)
StateClassFilter = ProjectFilter(StateClass)
SecondaryStratumFilter = ProjectFilter(SecondaryStratum)
TransitionGroupFilter = ProjectFilter(TransitionGroup)
TransitionTypeFilter = ProjectFilter(TransitionType)
AttributeGroupFilter = ProjectFilter(AttributeGroup)
StateAttributeTypeFilter = ProjectFilter(StateAttributeType)
TransitionAttributeTypeFilter = ProjectFilter(TransitionAttributeType)
TransitionMultiplierTypeFilter = ProjectFilter(TransitionMultiplierType)
DistributionTypeFilter = ProjectFilter(DistributionType)
