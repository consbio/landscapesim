"""
    This creates all of the maps from Django to SyncroSim.
    This is intended to be imported wherever the map is required.

    U_<variable>'s (e.g. U_TRANSITION) represent values we currently don't
    account for in the Django models/
"""

# TODO - generate mappings for all values

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

RUN_CONTROL = ()

DETERMINISTIC_TRANSITION = ()

TRANSITION = (('stratum_src', 'StratumIDSource'),
              ('stateclass_src', 'StateClassIDSource'),
              ('stratum_dest', 'StratumIDDest'),
              ('stateclass_dest', 'StateClassIDDest'),
              ('transition_type', 'TransitionTypeID'),
              ('probability', 'Probability'),
              ('age_reset', 'AgeReset'))

U_TRANSITION = ('Proportion', 'AgeMin', 'AgeMax', 'AgeRelative',
               'TSTMin', 'TSTMax', 'TSTRelative')

INITIAL_CONDITIONS_NON_SPATIAL = ()

INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION = ()

TRANSITION_TARGET = ()

TRANSITION_MULTIPLIER_VALUE = ()

TRANSITION_SIZE_DISTRIBUTION = ()

TRANSITION_SIZE_PRIORITIZATION = ()

STATE_ATTRIBUTE_VALUE = ()

TRANSITION_ATTRIBUTE_VALUE = ()

TRANSITION_ATTRIBUTE_TARGET = ()
