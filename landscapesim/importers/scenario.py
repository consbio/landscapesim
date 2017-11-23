from landscapesim import models
from landscapesim.common import config
from landscapesim.common.services import ServiceGenerator
from landscapesim.common.types import default_int, default_float, empty_or_yes_to_bool, time_int
from landscapesim.common.utils import get_random_csv
from .base import ImporterBase
from .filters import *

_distribution_types = (DistributionTypeFilter, default_float, default_float, default_float)

RUN_CONTROL = (
    'STSim_RunControl',
    models.RunControl,
    config.RUN_CONTROL,
    (int, int, int, int, empty_or_yes_to_bool)
)
OUTPUT_OPTIONS = (
    'STSim_OutputOptions',
    models.OutputOption,
    config.OUTPUT_OPTION,
    (empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, empty_or_yes_to_bool, default_int, empty_or_yes_to_bool,
     default_int, empty_or_yes_to_bool, empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int,
     empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int,
     empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int,
     empty_or_yes_to_bool, default_int, empty_or_yes_to_bool, default_int)
)
DISTRIBUTION_VALUE = (
    'Stats_DistributionValue',
    models.DistributionValue,
    config.DISTRIBUTION_VALUE,
    (DistributionTypeFilter, default_float, default_float, default_float)
)
DETERMINISTIC_TRANSITION = (
    'STSim_DeterministicTransition',
    models.DeterministicTransition,
    config.DETERMINISTIC_TRANSITION,
    (StratumFilter, StateClassFilter, StratumFilter, StateClassFilter, default_int, default_int, str)
)
TRANSITION = (
    'STSim_Transition',
    models.Transition,
    config.TRANSITION,
    (StratumFilter, StateClassFilter, StratumFilter, StateClassFilter, TransitionTypeFilter, float,
     None, None, empty_or_yes_to_bool, None, None, None, None, None)
)
INITIAL_CONDITIONS_NON_SPATIAL = (
    'STSim_InitialConditionsNonSpatial',
    models.InitialConditionsNonSpatial,
    config.INITIAL_CONDITIONS_NON_SPATIAL,
    (float, int, empty_or_yes_to_bool)
)
INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION = (
    'STSim_InitialConditionsNonSpatialDistribution',
    models.InitialConditionsNonSpatialDistribution,
    config.INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION,
    (StratumFilter, SecondaryStratumFilter, StateClassFilter, float, default_int, default_int)
)
INITIAL_CONDITIONS_SPATIAL = (
    'STSim_InitialConditionsSpatial',
    models.InitialConditionsSpatial,
    config.INITIAL_CONDITIONS_SPATIAL,
    (default_int, default_int, default_int, default_float, str, default_float, empty_or_yes_to_bool, default_float,
     default_float, str, str, str, str, str)
)
TRANSITION_TARGET = (
    'STSim_TransitionTarget',
    models.TransitionTarget,
    config.TRANSITION_TARGET,
    (time_int, time_int, StratumFilter, SecondaryStratumFilter, TransitionGroupFilter, float, *_distribution_types)
)
TRANSITION_MULTIPLIER_VALUE = (
    'STSim_TransitionMultiplierValue',
    models.TransitionMultiplierValue,
    config.TRANSITION_MULTIPLIER_VALUE,
    (time_int, time_int, StratumFilter, SecondaryStratumFilter, StateClassFilter, TransitionGroupFilter,
     TransitionMultiplierTypeFilter, float, *_distribution_types)
)
TRANSITION_SIZE_DISTRIBUTION = (
    'STSim_TransitionSizeDistribution',
    models.TransitionSizeDistribution,
    config.TRANSITION_SIZE_DISTRIBUTION,
    (time_int, time_int, StratumFilter, TransitionGroupFilter, float)
)
TRANSITION_SIZE_PRIORITIZATION = (
    'STSim_TransitionSizePrioritization',
    models.TransitionSizePrioritization,
    config.TRANSITION_SIZE_PRIORITIZATION,
    (time_int, time_int, StratumFilter, TransitionGroupFilter, str)
)
TRANSITION_SPATIAL_MULTIPLIER = (
    'STSim_TransitionSpatialMultiplier',
    models.TransitionSpatialMultiplier,
    config.TRANSITION_SPATIAL_MULTIPLIER,
    (time_int, time_int, TransitionGroupFilter, TransitionMultiplierTypeFilter, str)
)
STATE_ATTRIBUTE_VALUE = (
    'STSim_StateAttributeValue',
    models.StateAttributeValue,
    config.STATE_ATTRIBUTE_VALUE,
    (time_int, time_int, StratumFilter, SecondaryStratumFilter, StateClassFilter, StateAttributeTypeFilter, float)
)
TRANSITION_ATTRIBUTE_VALUE = (
    'STSim_TransitionAttributeValue',
    models.TransitionAttributeValue,
    config.TRANSITION_ATTRIBUTE_VALUE,
    (time_int, time_int, StratumFilter, SecondaryStratumFilter, TransitionGroupFilter, StateClassFilter,
     TransitionAttributeTypeFilter, float)
)
TRANSITION_ATTRIBUTE_TARGET = (
    'STSim_TransitionAttributeTarget',
    models.TransitionAttributeTarget,
    config.TRANSITION_ATTRIBUTE_TARGET,
    (time_int, time_int, StratumFilter, SecondaryStratumFilter, TransitionAttributeTypeFilter, float,
     *_distribution_types)
)


class ScenarioImporter(ImporterBase):
    """ Scenario importer class, used for pulling all Scenario-level information from SyncroSim into LandscapeSim. """

    related_model = models.Scenario

    def __init__(self, console, scenario):
        super().__init__(console, scenario, get_random_csv(scenario.library.tmp_file))
        self.sheet_kwargs = {'sid': scenario.sid, 'overwrite': True, 'orig': not scenario.is_result}

    def import_run_control(self):
        self._extract_sheet(RUN_CONTROL)

    def import_output_options(self):
        self._extract_sheet(OUTPUT_OPTIONS)

    def import_distribution_values(self):
        self._extract_sheet(DISTRIBUTION_VALUE)

    def import_deterministic_transitions(self):
        self._extract_sheet(DETERMINISTIC_TRANSITION)

    def import_probabilistic_transitions(self):
        self._extract_sheet(TRANSITION)

    def import_initial_conditions_non_spatial(self):
        self._extract_sheet(INITIAL_CONDITIONS_NON_SPATIAL)

    def import_initial_conditions_non_spatial_distribution(self):
        self._extract_sheet(INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION)

    def import_initial_conditions_spatial(self, create_input_services=True):
        if self.scenario.run_control.is_spatial:
            self._extract_sheet(INITIAL_CONDITIONS_SPATIAL)
            if create_input_services:
                ServiceGenerator(self.scenario).create_input_services()

    def import_transition_targets(self):
        self._extract_sheet(TRANSITION_TARGET)

    def import_transition_multiplier_values(self):
        self._extract_sheet(TRANSITION_MULTIPLIER_VALUE)

    def import_transition_size_distributions(self):
        self._extract_sheet(TRANSITION_SIZE_DISTRIBUTION)

    def import_transition_size_prioritizations(self):
        self._extract_sheet(TRANSITION_SIZE_PRIORITIZATION)

    def import_transition_spatial_multipliers(self):
        self._extract_sheet(TRANSITION_SPATIAL_MULTIPLIER)

    def import_state_attribute_values(self):
        self._extract_sheet(STATE_ATTRIBUTE_VALUE)

    def import_transition_attribute_values(self):
        self._extract_sheet(TRANSITION_ATTRIBUTE_VALUE)

    def import_transition_attribute_targets(self):
        self._extract_sheet(TRANSITION_ATTRIBUTE_TARGET)

    def import_post_processed_sheets(self, create_input_services=True):
        self.import_deterministic_transitions()
        self.import_probabilistic_transitions()
        self.import_initial_conditions_non_spatial()
        self.import_initial_conditions_non_spatial_distribution()
        self.import_initial_conditions_spatial(create_input_services=create_input_services)
        self.import_transition_targets()
        self.import_transition_multiplier_values()
        self.import_transition_spatial_multipliers()
        self.import_state_attribute_values()
        self.import_transition_attribute_values()
        self.import_transition_attribute_targets()
