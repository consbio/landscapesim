"""
    An import utility class for creating reports in SyncroSim and exporting them to be used in
    the LandscapeSim API.

    Each report configuration corresponds to:
    - Report name,
    - Report model class,
    - Report row model call,
    - SyncroSim sheet mapping, and
    - Type conversion mapping
"""

import csv
import os
from inspect import isfunction

from django.conf import settings

from landscapesim import models
from landscapesim.common import config
from landscapesim.common.types import default_int
from landscapesim.common.utils import get_random_csv
from .filters import *

DEBUG = getattr(settings, 'DEBUG')


""" Report summary configurations """
STATECLASS_REPORT = (
    'stateclass-summary',
    models.StateClassSummaryReport,
    models.StateClassSummaryReportRow,
    config.STATECLASS_SUMMARY_ROW,
    (int, int, StratumFilter, StateClassFilter, float, default_int, default_int, float, float, SecondaryStratumFilter)
)
TRANSITION_REPORT = (
    'transition-summary',
    models.TransitionSummaryReport,
    models.TransitionSummaryReportRow,
    config.TRANSITION_SUMMARY_ROW,
    (int, int, StratumFilter, TransitionGroupFilter, default_int, default_int, float, SecondaryStratumFilter)
)
TRANSITION_STATECLASS_REPORT = (
    'transition-stateclass-summary',
    models.TransitionByStateClassSummaryReport,
    models.TransitionByStateClassSummaryReportRow,
    config.TRANSITION_STATECLASS_SUMMARY_ROW,
    (int, int, StratumFilter, TransitionTypeFilter, StateClassFilter, StateClassFilter, float, SecondaryStratumFilter)
)
STATE_ATTRIBUTE_REPORT = (
    'state-attributes',
    models.StateAttributeSummaryReport,
    models.StateAttributeSummaryReportRow,
    config.STATE_ATTRIBUTE_SUMMARY_ROW,
    (int, int, StratumFilter, StateAttributeTypeFilter, default_int, default_int, float, SecondaryStratumFilter)
)
TRANSITION_ATTRIBUTE_REPORT = (
    'transition-attributes',
    models.TransitionAttributeSummaryReport,
    models.TransitionAttributeSummaryReportRow,
    config.TRANSITION_ATTRIBUTE_SUMMARY_ROW,
    (int, int, StratumFilter, TransitionAttributeTypeFilter, default_int, default_int, float, SecondaryStratumFilter)
)


class ReportImporter:
    """
    A base report creation interface for exporting reports and creating API-exposed reports.

    This class functions very similarly to ProjectImporter (or ImporterBase), but it requires additional
    information about what models are connected to the scenario the report is created for. For that reason,
    this class is orphaned away from ImporterBase.
    """

    def __init__(self, console, scenario):
        """
        Constructor
        :param console: Instance of STSimConsole
        :param scenario: Instance of Scenario
        """
        self.console = console
        self.scenario = scenario
        self.temp_file = get_random_csv(scenario.library.tmp_file)

    def generate_report(self, report_name):
        """
        Create a CSV report corresponding to the appropriate name.
        :param report_name: The name of the ST-Sim report to export.
        """
        self.console.generate_report(report_name, self.temp_file, self.scenario.sid)

    def map_row(self, row_data, sheet_map, type_map):
        result = {}
        for pair, type_or_filter in zip(sheet_map, type_map):
            model_field, sheet_field = pair
            data = row_data[sheet_field]
            is_filter = not (isinstance(type_or_filter, type) or isfunction(type_or_filter))
            result[model_field] = type_or_filter.get(data, self.scenario.project) if is_filter else type_or_filter(data)
        return result

    def _create_report_summary(self, report_config):
        name, model, row_model, sheet_map, type_map = report_config

        self.generate_report(name)
        report, created = model.objects.get_or_create(scenario=self.scenario)
        with open(self.temp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                row_model.objects.create(report=report, **self.map_row(row, sheet_map, type_map))
        if not DEBUG and os.path.exists(self.temp_file):
            os.remove(self.temp_file)

        return report

    def create_stateclass_summary(self):
        self._create_report_summary(STATECLASS_REPORT)

    def create_transition_summary(self):
        self._create_report_summary(TRANSITION_REPORT)

    def create_transition_sc_summary(self):
        self._create_report_summary(TRANSITION_STATECLASS_REPORT)

    def create_state_attribute_summary(self):
        self._create_report_summary(STATE_ATTRIBUTE_REPORT)

    def create_transition_attribute_summary(self):
        self._create_report_summary(TRANSITION_ATTRIBUTE_REPORT)

    def create_all_summaries(self):
        self.create_stateclass_summary()
        self.create_transition_summary()
        self.create_transition_sc_summary()
        self.create_state_attribute_summary()
        self.create_transition_attribute_summary()
