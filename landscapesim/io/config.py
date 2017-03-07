"""
    This creates all of the maps from Django to SyncroSim.
    This is intended to be imported wherever the map is required.

    NOTE: Order is intended to match the order in which the config is imported/exported.
"""

# Commonly used mapping components
stratum = ('stratum', 'StratumID')
stratum_src = ('stratum_src', 'StratumIDSource')
stratum_dest = ('stratum_dest', 'StratumIDDest')
secondary_stratum = ('secondary_stratum', 'SecondaryStratumID')
stateclass = ('stateclass', 'StateClassID')
stateclass_src = ('stateclass_src', 'StateClassIDSource')
stateclass_dest = ('stateclass_dest', 'StateClassIDDest')
transition_group = ('transition_group', 'TransitionGroupID')
transition_type = ('transition_type', 'TransitionTypeID')
state_attribute_type = ('state_attribute_type', 'StateAttributeTypeID')
transition_attribute_type = ('transition_attribute_type', 'TransitionAttributeTypeID'),
iteration = ('iteration', 'Iteration')
timestep = ('timestep', 'Timestep')
age_min = ('age_min', 'AgeMin')
age_max = ('age_max', 'AgeMax')
distribution_type = ('distribution_type', 'DistributionTypeID')
distribution_sd = ('distribution_sd', 'DistributionSD')
distribution_min = ('distribution_min', 'DistributionMin')
distribution_max = ('distribution_max', 'DistributionMax')

# Common combinations
time_common = (timestep, iteration)
age_common = (age_min, age_max)
distribution_common = (distribution_type, distribution_sd, distribution_min, distribution_max)


DISTRIBUTION_VALUE = (distribution_type,
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
                  ('raster_sc_t','RasterOutputSCTimesteps'),
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

DETERMINISTIC_TRANSITION = (stratum_src,
                            stateclass_src,
                            stratum_dest,
                            stateclass_dest,
                            *age_common)

TRANSITION = (stratum_src,
              stateclass_src,
              stratum_dest,
              stateclass_dest,
              transition_type,
              ('probability', 'Probability'),
              ('proportion', 'Proportion'),
              ('age_relative', 'AgeRelative'),
              ('age_reset', 'AgeReset'),
              *age_common,
              ('tst_min', 'TSTMin'),
              ('tst_max', 'TSTMax'),
              ('tst_relative', 'TSTRelative'))

INITIAL_CONDITIONS_NON_SPATIAL = (('total_amount', 'TotalAmount'),
                                  ('num_cells', 'NumCells'),
                                  ('calc_from_dist', 'CaldFromDist'))

INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION = (stratum,
                                               secondary_stratum,
                                               stateclass,
                                               ('relative_amount', 'RelativeAmount'),
                                               *age_common)

TRANSITION_TARGET = (*time_common,
                     stratum,
                     secondary_stratum,
                     transition_group,
                     ('target_area', 'Amount'),
                     *distribution_common)

TRANSITION_MULTIPLIER_VALUE = (*time_common,
                               stratum,
                               secondary_stratum,
                               stateclass,
                               transition_group,
                               ('transition_multiplier_type', 'TransitionMultiplierTypeID'),
                               ('multiplier', 'Amount'),
                               *distribution_common)

TRANSITION_SIZE_DISTRIBUTION = (*time_common,
                                stratum,
                                transition_group,
                                ('relative_amount', 'RelativeAmount'))

TRANSITION_SIZE_PRIORITIZATION = (*time_common,
                                  stratum,
                                  transition_group,
                                  ('priority', 'Priority'))

STATE_ATTRIBUTE_VALUE = (*time_common,
                         stratum,
                         secondary_stratum,
                         stateclass,
                         state_attribute_type,
                         ('value', 'Value'))

TRANSITION_ATTRIBUTE_VALUE = (*time_common,
                              stratum,
                              secondary_stratum,
                              transition_group,
                              stateclass,
                              ('transition_attribute_type', 'TransitionAttributeTypeID'),
                              ('value', 'Value'))

TRANSITION_ATTRIBUTE_TARGET = (*time_common,
                               stratum,
                               secondary_stratum,
                               transition_attribute_type,
                               ('target', 'Amount'),
                               *distribution_common)
