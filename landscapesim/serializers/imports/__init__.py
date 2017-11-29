from .serializers import *

# Configuration flags for initialization
CONFIG_INPUTS = (
    ('run_control', RunControlImport),
    ('output_options', OutputOptionImport),
    ('initial_conditions_nonspatial_settings', InitialConditionsNonSpatialImport),
    #('initial_conditions_spatial_settings', InitialConditionsSpatialImport)
)

# Configuration of input data (probabilities, mappings, etc.)
VALUE_INPUTS = (
    ('deterministic_transitions', DeterministicTransitionImport),
    ('transitions', TransitionImport),
    ('initial_conditions_nonspatial_distributions', InitialConditionsNonSpatialDistributionImport),
    #('transition_targets', TransitionTargetImport),
    #('transition_multiplier_values', TransitionMultiplierValueImport),
    #('transition_size_distributions', TransitionSizeDistributionImport),
    #('transition_size_prioritizations', TransitionSizePrioritizationImport),
    ('transition_spatial_multipliers', TransitionSpatialMultiplierImport),
    #('state_attribute_values', StateAttributeValueImport),
    ('transition_attribute_values', TransitionAttributeValueImport),
    #('transition_attribute_targets', TransitionAttributeTargetImport)
)

__all__ = [
    'BaseImportSerializer',
    'DistributionValueImport',
    'OutputOptionImport',
    'RunControlImport',
    'DeterministicTransitionImport',
    'TransitionImport',
    'InitialConditionsNonSpatialImport',
    'InitialConditionsNonSpatialDistributionImport',
    'InitialConditionsSpatialImport',
    'TransitionTargetImport',
    'TransitionMultiplierValueImport',
    'TransitionSizeDistributionImport',
    'TransitionSizePrioritizationImport',
    'TransitionSpatialMultiplierImport',
    'StateAttributeValueImport',
    'TransitionAttributeValueImport',
    'TransitionAttributeTargetImport',
    'CONFIG_INPUTS',
    'VALUE_INPUTS'
]
