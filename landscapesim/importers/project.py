from landscapesim import models
from landscapesim.common import config
from landscapesim.common.types import default_int, empty_or_yes_to_bool
from landscapesim.common.utils import get_random_csv
from .base import ImporterBase
from .filters import *


TERMINOLOGY = (
    'STSim_Terminology',
    models.Terminology,
    config.TERMINOLOGY,
    (str, str, str, str, str, str, str)
)
DISTRIBUTION_TYPE = (
    'Stats_DistributionType',
    models.DistributionType,
    config.DISTRIBUTION_TYPE,
    (str, str, empty_or_yes_to_bool)
)
STRATUM = (
    'STSim_Stratum',
    models.Stratum,
    config.STRATUM,
    (str, str, str, default_int)
)
SECONDARY_STRATUM = (
    'STSim_SecondaryStratum',
    models.SecondaryStratum,
    config.SECONDARY_STRATUM,
    (str, str, default_int)
)
STATECLASS = (
    'STSim_StateClass',
    models.StateClass,
    config.STATECLASS,
    (str, str, str, str, str, default_int)
)
TRANSITION_TYPE = (
    'STSim_TransitionType',
    models.TransitionType,
    config.TRANSITION_TYPE,
    (str, str, str, default_int)
)
TRANSITION_GROUP = (
    'STSim_TransitionGroup',
    models.TransitionGroup,
    config.TRANSITION_GROUP,
    (str, str)
)
TRANSITION_TYPE_GROUP = (
    'STSim_TransitionTypeGroup',
    models.TransitionTypeGroup,
    config.TRANSITION_TYPE_GROUP,
    (TransitionTypeFilter, TransitionGroupFilter, str)
)
TRANSITION_MULTIPLIER_TYPE = (
    'STSim_TransitionMultiplierType',
    models.TransitionMultiplierType,
    config.TRANSITION_MULTIPLIER_TYPE,
    (str,)
)
ATTRIBUTE_GROUP = (
    'STSim_AttributeGroup',
    models.AttributeGroup,
    config.ATTRIBUTE_GROUP,
    (str, str)
)
STATE_ATTRIBUTE_TYPE = (
    'STSim_StateAttributeType',
    models.StateAttributeType,
    config.STATE_ATTRIBUTE_TYPE,
    (str, str, str, AttributeGroupFilter)
)
TRANSITION_ATTRIBUTE_TYPE = (
    'STSim_TransitionAttributeType',
    models.TransitionAttributeType,
    config.TRANSITION_ATTRIBUTE_TYPE,
    (str, str, str, AttributeGroupFilter)
)


class ProjectImporter(ImporterBase):
    """
    The base Project importer, responsible for converting SyncroSim project-related ata into the
    appropriate LandscapeSim project-related data.
    """

    related_model = models.Project

    def __init__(self, console, project=None):
        super().__init__(console, project, get_random_csv(project.library.tmp_file))
        self.sheet_kwargs = {'pid': project.pid, 'overwrite': True, 'orig': True}

    def import_terminology(self):
        self._extract_sheet(TERMINOLOGY)

    def import_distribution_types(self):
        self._extract_sheet(DISTRIBUTION_TYPE)

    def import_stratum(self):
        self._extract_sheet(STRATUM)

    def import_secondary_stratum(self):
        self._extract_sheet(SECONDARY_STRATUM)

    def import_stateclasses(self):
        self._extract_sheet(STATECLASS)

    def import_transition_types(self):
        self._extract_sheet(TRANSITION_TYPE)

    def import_transition_groups(self):
        self._extract_sheet(TRANSITION_GROUP)

    def import_transition_multiplier_types(self):
        self._extract_sheet(TRANSITION_MULTIPLIER_TYPE)

    def import_attribute_groups(self):
        self._extract_sheet(ATTRIBUTE_GROUP)

    def import_state_attribute_types(self):
        self._extract_sheet(STATE_ATTRIBUTE_TYPE)

    def import_transition_attribute_types(self):
        self._extract_sheet(TRANSITION_ATTRIBUTE_TYPE)

    def process_project_definitions(self):
        self.import_terminology()
        self.import_distribution_types()
        self.import_stratum()
        self.import_secondary_stratum()
        self.import_stateclasses()
        self.import_transition_types()
        self.import_transition_groups()
        self.import_transition_multiplier_types()
        self.import_attribute_groups()
        self.import_state_attribute_types()
        self.import_transition_attribute_types()
