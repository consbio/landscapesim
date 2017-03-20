"""
    This creates all of the maps from Django to SyncroSim.
    The whole module is intended to be imported wherever the map is required.
    (E.g. from landscapesim.io import config)
    NOTE: Order is intended to match the order in which the config is imported/exported.
"""

# Commonly used mapping components
_stratum = ('stratum', 'StratumID')
_stratum_src = ('stratum_src', 'StratumIDSource')
_stratum_dest = ('stratum_dest', 'StratumIDDest')
_secondary_stratum = ('secondary_stratum', 'SecondaryStratumID')
_stateclass = ('stateclass', 'StateClassID')
_stateclass_src = ('stateclass_src', 'StateClassIDSource')
_stateclass_dest = ('stateclass_dest', 'StateClassIDDest')
_transition_group = ('transition_group', 'TransitionGroupID')
_transition_type = ('transition_type', 'TransitionTypeID')
_state_attribute_type = ('state_attribute_type', 'StateAttributeTypeID')
_transition_attribute_type = ('transition_attribute_type', 'TransitionAttributeTypeID')
_transition_multiplier_type = ('transition_multiplier_type', 'TransitionMultiplierTypeID')
_iteration = ('iteration', 'Iteration')
_timestep = ('timestep', 'Timestep')
_age_min = ('age_min', 'AgeMin')
_age_max = ('age_max', 'AgeMax')
_distribution_type = ('distribution_type', 'DistributionTypeID')
_distribution_sd = ('distribution_sd', 'DistributionSD')
_distribution_min = ('distribution_min', 'DistributionMin')
_distribution_max = ('distribution_max', 'DistributionMax')

# Common combinations
_time_common = (_timestep, _iteration)
_age_common = (_age_min, _age_max)
_distribution_common = (_distribution_type, _distribution_sd, _distribution_min, _distribution_max)


DISTRIBUTION_VALUE = (_distribution_type,
                      ('dmin', 'Min'),
                      ('dmax', 'Max'),
                      ('relative_frequency', 'RelativeFrequency'))

RUN_CONTROL = (('min_iteration', 'MinimumIteration'),
               ('max_iteration', 'MaximumIteration'),
               ('min_timestep', 'MinimumTimestep'),
               ('max_timestep', 'MaximumTimestep'),
               ('is_spatial', 'IsSpatial'))

OUTPUT_OPTION = (('sum_sc', 'SummaryOutputSC'),
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
                 ('raster_aatp_t', 'RasterOutputAATPTimesteps'))

DETERMINISTIC_TRANSITION = (_stratum_src,
                            _stateclass_src,
                            _stratum_dest,
                            _stateclass_dest,
                            *_age_common,
                            ('location', 'Location'))

TRANSITION = (_stratum_src,
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
              ('tst_relative', 'TSTRelative'))

INITIAL_CONDITIONS_NON_SPATIAL = (('total_amount', 'TotalAmount'),
                                  ('num_cells', 'NumCells'),
                                  ('calc_from_dist', 'CalcFromDist'))

INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION = (_stratum,
                                               _secondary_stratum,
                                               _stateclass,
                                               ('relative_amount', 'RelativeAmount'),
                                               *_age_common)

INITIAL_CONDITIONS_SPATIAL = (('num_rows', 'NumRows'),
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
                              ('age_file_name', 'AgeFileName'))

TRANSITION_TARGET = (*_time_common,
                     _stratum,
                     _secondary_stratum,
                     _transition_group,
                     ('target_area', 'Amount'),
                     *_distribution_common)

TRANSITION_MULTIPLIER_VALUE = (*_time_common,
                               _stratum,
                               _secondary_stratum,
                               _stateclass,
                               _transition_group,
                               _transition_multiplier_type,
                               ('multiplier', 'Amount'),
                               *_distribution_common)

TRANSITION_SIZE_DISTRIBUTION = (*_time_common,
                                _stratum,
                                _transition_group,
                                ('relative_amount', 'RelativeAmount'))

TRANSITION_SIZE_PRIORITIZATION = (*_time_common,
                                  _stratum,
                                  _transition_group,
                                  ('priority', 'Priority'))

TRANSITION_SPATIAL_MULTIPLIER = (*_time_common,
                                 _transition_group,
                                 _transition_multiplier_type,
                                 ('transition_multiplier_file_name', 'MultiplierFileName'))

STATE_ATTRIBUTE_VALUE = (*_time_common,
                         _stratum,
                         _secondary_stratum,
                         _stateclass,
                         _state_attribute_type,
                         ('value', 'Value'))

TRANSITION_ATTRIBUTE_VALUE = (*_time_common,
                              _stratum,
                              _secondary_stratum,
                              _transition_group,
                              _stateclass,
                              _transition_attribute_type,
                              ('value', 'Value'))

TRANSITION_ATTRIBUTE_TARGET = (*_time_common,
                               _stratum,
                               _secondary_stratum,
                               _transition_attribute_type,
                               ('target', 'Amount'),
                               *_distribution_common)
