"""
    This creates all of the maps from Django to SyncroSim.
    The module and it's CONSTANTS are intended to be imported wherever a serialization, deserialization, or
    map is required. (E.g. from landscapesim.io import config)
    NOTE: Explicit order is intended to match the order in which the config is imported/exported from SyncroSim.
"""

# Commonly used mapping components
_name = ('name', 'Name')
_color = ('color', 'Color')
_description = ('description', 'Description')
_stratum = ('stratum', 'StratumID')
_stratum_src = ('stratum_src', 'StratumIDSource')
_stratum_dest = ('stratum_dest', 'StratumIDDest')
_secondary_stratum = ('secondary_stratum', 'SecondaryStratumID')
_stateclass = ('stateclass', 'StateClassID')
_stateclass_src = ('stateclass_src', 'StateClassIDSource')
_stateclass_dest = ('stateclass_dest', 'StateClassIDDest')      # Slight table difference for destination state classes
_stateclass_dest_end = ('stateclass_dest', 'EndStateClassID')   # in this line and line above
_transition_group = ('transition_group', 'TransitionGroupID')
_transition_type = ('transition_type', 'TransitionTypeID')
_state_attribute_type = ('state_attribute_type', 'StateAttributeTypeID')
_transition_attribute_type = ('transition_attribute_type', 'TransitionAttributeTypeID')
_transition_multiplier_type = ('transition_multiplier_type', 'TransitionMultiplierTypeID')
_iteration = ('iteration', 'Iteration')
_timestep = ('timestep', 'Timestep')
_age_min = ('age_min', 'AgeMin')
_age_max = ('age_max', 'AgeMax')
_amount = ('amount', 'Amount')
_distribution_type_id = ('distribution_type', 'DistributionTypeID')  # Slight discrepancy in use for distributions.
_distribution_type = ('distribution_type', 'DistributionType')       # Make sure not to use both *type and *type_id
_distribution_sd = ('distribution_sd', 'DistributionSD')             # concurrently.
_distribution_min = ('distribution_min', 'DistributionMin')
_distribution_max = ('distribution_max', 'DistributionMax')

# Common combinations
_time_common = (_timestep, _iteration)
_age_common = (_age_min, _age_max)
_distribution_common = (_distribution_type, _distribution_sd, _distribution_min, _distribution_max)
_project_def = (_name, _description)
_project_def_color = (*_project_def, _color)

# Project-specific mappings
TERMINOLOGY = (
    ('amount_label', 'AmountLabel'),
    ('amount_units', 'AmountUnits'),
    ('state_label_x', 'StateLabelX'),
    ('state_label_y', 'StateLabelY'),
    ('primary_stratum_label', 'PrimaryStratumLabel'),
    ('secondary_stratum_label', 'SecondaryStratumLabel'),
    ('timestep_units', 'TimestepUnits')
)
DISTRIBUTION_TYPE = (
    *_project_def,
    ('is_internal', 'IsInternal')
)
STRATUM = (
    *_project_def_color,
    ('stratum_id', 'ID')
)
SECONDARY_STRATUM = (
    *_project_def,
    ('secondary_stratum_id', 'ID')
)
STATECLASS = (
    *_project_def_color,
    ('state_label_x', 'StateLabelXID'),
    ('state_label_y', 'StateLabelYID'),
    ('stateclass_id', 'ID')
)
TRANSITION_TYPE = (
    *_project_def_color,
    ('transition_type_id', 'ID')
)
TRANSITION_GROUP = (
    *_project_def,
)
TRANSITION_TYPE_GROUP = (
    ('transition_type', 'TransitionTypeID'),
    ('transition_group', 'TransitionGroupID'),
    ('is_primary', 'IsPrimary')
)
TRANSITION_MULTIPLIER_TYPE = (
    _name,
)
ATTRIBUTE_GROUP = (
    *_project_def,
)
STATE_ATTRIBUTE_TYPE = (
    *_project_def,
    ('units', 'Units'),
    ('attribute_group', 'AttributeGroupID')
)
TRANSITION_ATTRIBUTE_TYPE = STATE_ATTRIBUTE_TYPE

# Scenario-specific mappings
DISTRIBUTION_VALUE = (
    _distribution_type_id,
    ('dmin', 'Min'),
    ('dmax', 'Max'),
    ('relative_frequency', 'RelativeFrequency')
)

RUN_CONTROL = (
    ('min_iteration', 'MinimumIteration'),
    ('max_iteration', 'MaximumIteration'),
    ('min_timestep', 'MinimumTimestep'),
    ('max_timestep', 'MaximumTimestep'),
    ('is_spatial', 'IsSpatial')
)
OUTPUT_OPTION = (
    ('sum_sc', 'SummaryOutputSC'),
    ('sum_sc_t', 'SummaryOutputSCTimesteps'),
    ('sum_sc_zeros', 'SummaryOutputSCZeroValues'),
    ('raster_sc', 'RasterOutputSC'),
    ('raster_sc_t', 'RasterOutputSCTimesteps'),
    ('sum_tr', 'SummaryOutputTR'),
    ('sum_tr_t', 'SummaryOutputTRTimesteps'),
    ('sum_tr_interval', 'SummaryOutputTRIntervalMean'),
    ('raster_tr', 'RasterOutputTR'),
    ('raster_tr_t', 'RasterOutputTRTimesteps'),
    ('sum_trsc', 'SummaryOutputTRSC'),
    ('sum_trsc_t', 'SummaryOutputTRSCTimesteps'),
    ('sum_sa', 'SummaryOutputSA'),
    ('sum_sa_t', 'SummaryOutputSATimesteps'),
    ('raster_sa', 'RasterOutputSA'),
    ('raster_sa_t', 'RasterOutputSATimesteps'),
    ('sum_ta', 'SummaryOutputTA'),
    ('sum_ta_t', 'SummaryOutputTATimesteps'),
    ('raster_ta', 'RasterOutputTA'),
    ('raster_ta_t', 'RasterOutputTATimesteps'),
    ('raster_strata', 'RasterOutputST'),
    ('raster_strata_t', 'RasterOutputSTTimesteps'),
    ('raster_age', 'RasterOutputAge'),
    ('raster_age_t', 'RasterOutputAgeTimesteps'),
    ('raster_tst', 'RasterOutputTST'),
    ('raster_tst_t', 'RasterOutputTSTTimesteps'),
    ('raster_aatp', 'RasterOutputAATP'),
    ('raster_aatp_t', 'RasterOutputAATPTimesteps')
)
DETERMINISTIC_TRANSITION = (
    _stratum_src,
    _stateclass_src,
    _stratum_dest,
    _stateclass_dest,
    *_age_common,
    ('location', 'Location')
)
TRANSITION = (
    _stratum_src,
    _stateclass_src,
    _stratum_dest,
    _stateclass_dest,
    _transition_type,
    ('probability', 'Probability'),
    ('proportion', 'Proportion'),
    ('age_relative', 'AgeRelative'),
    ('age_reset', 'AgeReset'),
    *_age_common,
    ('tst_min', 'TSTMin'),
    ('tst_max', 'TSTMax'),
    ('tst_relative', 'TSTRelative')
)
INITIAL_CONDITIONS_NON_SPATIAL = (
    ('total_amount', 'TotalAmount'),
    ('num_cells', 'NumCells'),
    ('calc_from_dist', 'CalcFromDist')
)
INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION = (
    _stratum,
    _secondary_stratum,
    _stateclass,
    ('relative_amount', 'RelativeAmount'),
    *_age_common
)
INITIAL_CONDITIONS_SPATIAL = (
    ('num_rows', 'NumRows'),
    ('num_cols', 'NumColumns'),
    ('num_cells', 'NumCells'),
    ('cell_size', 'CellSize'),
    ('cell_size_units', 'CellSizeUnits'),
    ('cell_area', 'CellArea'),
    ('cell_area_override', 'CellAreaOverride'),
    ('xll_corner', 'XLLCorner'),
    ('yll_corner', 'YLLCorner'),
    ('srs', 'SRS'),
    ('stratum_file_name', 'StratumFileName'),
    ('secondary_stratum_file_name', 'SecondaryStratumFileName'),
    ('stateclass_file_name', 'StateClassFileName'),
    ('age_file_name', 'AgeFileName')
)
TRANSITION_TARGET = (
    *_time_common,
    _stratum,
    _secondary_stratum,
    _transition_group,
    ('target_area', 'Amount'),
    *_distribution_common
)
TRANSITION_MULTIPLIER_VALUE = (
    *_time_common,
    _stratum,
    _secondary_stratum,
    _stateclass,
    _transition_group,
    _transition_multiplier_type,
    ('multiplier', 'Amount'),
    *_distribution_common
)
TRANSITION_SIZE_DISTRIBUTION = (
    *_time_common,
    _stratum,
    _transition_group,
    ('relative_amount', 'RelativeAmount')
)
TRANSITION_SIZE_PRIORITIZATION = (
    *_time_common,
    _stratum,
    _transition_group,
    ('priority', 'Priority')
)
TRANSITION_SPATIAL_MULTIPLIER = (
    *_time_common,
    _transition_group,
    _transition_multiplier_type,
    ('transition_multiplier_file_name', 'MultiplierFileName')
)
STATE_ATTRIBUTE_VALUE = (
    *_time_common,
    _stratum,
    _secondary_stratum,
    _stateclass,
    _state_attribute_type,
    ('value', 'Value')
)
TRANSITION_ATTRIBUTE_VALUE = (
    *_time_common,
    _stratum,
    _secondary_stratum,
    _transition_group,
    _stateclass,
    _transition_attribute_type,
    ('value', 'Value')
)
TRANSITION_ATTRIBUTE_TARGET = (
    *_time_common,
    _stratum,
    _secondary_stratum,
    _transition_attribute_type,
    ('target', 'Amount'),
    *_distribution_common
)
STATECLASS_SUMMARY_ROW = (
    *_time_common,
    _stratum,
    _stateclass,
    _amount,
    *_age_common,
    ('proportion_of_landscape', 'ProportionOfLandscape'),
    ('proportion_of_stratum', 'ProportionOfStratumID'),
    _secondary_stratum
)
TRANSITION_SUMMARY_ROW = (
    *_time_common,
    _stratum,
    _transition_group,
    *_age_common,
    _amount,
    _secondary_stratum
)
TRANSITION_STATECLASS_SUMMARY_ROW = (
    *_time_common,
    _stratum,
    _transition_type,
    _stateclass,
    _stateclass_dest_end,
    _amount,
    _secondary_stratum
)
STATE_ATTRIBUTE_SUMMARY_ROW = (
    *_time_common,
    _stratum,
    _state_attribute_type,
    *_age_common,
    _amount,
    _secondary_stratum
)
TRANSITION_ATTRIBUTE_SUMMARY_ROW = (
    *_time_common,
    _stratum,
    _transition_attribute_type,
    *_age_common,
    _amount,
    _secondary_stratum
)
# Configuration of run outputs, time control, distributions, etc.
CONFIG_IMPORTS = (
    ('run_control', 'STSim_RunControl', RUN_CONTROL),
    ('output_options', 'STSim_OutputOptions', OUTPUT_OPTION),
    ('initial_conditions_nonspatial_settings', 'STSim_InitialConditionsNonSpatial', INITIAL_CONDITIONS_NON_SPATIAL),
    #('initial_conditions_spatial_settings', 'STSim_InitialConditionsSpatial', INITIAL_CONDITIONS_SPATIAL)
)
# Configuration of input data (probabilities, mappings, etc.)
VALUE_IMPORTS = (
    ('deterministic_transitions', 'STSim_DeterministicTransition', DETERMINISTIC_TRANSITION),
    ('transitions', 'STSim_Transition', TRANSITION),
    (
        'initial_conditions_nonspatial_distributions', 'STSim_InitialConditionsNonSpatialDistribution',
        INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION
     ),
    #('transition_targets', 'STSim_TransitionTarget', TRANSITION_TARGET),
    #('transition_multiplier_values', 'STSim_TransitionMultiplierValue', TRANSITION_MULTIPLIER_VALUE),
    #('transition_size_distributions', 'STSim_TransitionSizeDistribution', TRANSITION_SIZE_DISTRIBUTION),
    #('transition_size_prioritizations', 'STSim_TransitionSizePrioritization', TRANSITION_SIZE_PRIORITIZATION),
    ('transition_spatial_multipliers', 'STSim_TransitionSpatialMultiplier', TRANSITION_SPATIAL_MULTIPLIER),
    #('state_attribute_values', 'STSim_StateAttributeValue', STATE_ATTRIBUTE_VALUE),
    ('transition_attribute_values', 'STSim_TransitionAttributeValue', TRANSITION_ATTRIBUTE_VALUE),
    #('transition_attribute_targets', 'STSim_TransitionAttributeTarget', TRANSITION_ATTRIBUTE_TARGET)
)
