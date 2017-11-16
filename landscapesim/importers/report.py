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
from landscapesim.io import config
from landscapesim.io.types import default_int
from landscapesim.io.utils import get_random_csv
from .base import Filter

DEBUG = getattr(settings, 'DEBUG')

# Report filters
STRATUM_FILTER = Filter(models.Stratum)
STATECLASS_FILTER = Filter(models.StateClass)
TRANSITION_GROUP_FILTER = Filter(models.TransitionGroup)
TRANSITION_TYPE_FILTER = Filter(models.TransitionType)
STATE_ATTRIBUTE_FILTER = Filter(models.StateAttributeType)
TRANSITION_ATTRIBUTE_FILTER = Filter(models.TransitionAttributeType)
SECONDARY_STRATUM_FILTER = Filter(models.SecondaryStratum)

""" Report summary configurations """
STATECLASS_REPORT = (
    'stateclass-summary',
    models.StateClassSummaryReport,
    models.StateClassSummaryReportRow,
    config.STATECLASS_SUMMARY_ROW,
    (int, int, STRATUM_FILTER, STATECLASS_FILTER, float, default_int, default_int, float, float, SECONDARY_STRATUM_FILTER)
)
TRANSITION_REPORT = (
    'transition-summary',
    models.TransitionSummaryReport,
    models.TransitionSummaryReportRow,
    config.TRANSITION_SUMMARY_ROW,
    (int, int, STRATUM_FILTER, TRANSITION_GROUP_FILTER, default_int, default_int, float, SECONDARY_STRATUM_FILTER)
)
TRANSITION_STATECLASS_REPORT = (
    'transition-stateclass-summary',
    models.TransitionByStateClassSummaryReport,
    models.TransitionByStateClassSummaryReportRow,
    config.TRANSITION_STATECLASS_SUMMARY_ROW,
    (int, int, STRATUM_FILTER, TRANSITION_TYPE_FILTER, STATECLASS_FILTER, STATECLASS_FILTER, float, SECONDARY_STRATUM_FILTER)
)
STATE_ATTRIBUTE_REPORT = (
    'state-attributes',
    models.StateAttributeSummaryReport,
    models.StateAttributeSummaryReportRow,
    config.STATE_ATTRIBUTE_SUMMARY_ROW,
    (int, int, STRATUM_FILTER, STATE_ATTRIBUTE_FILTER, default_int, default_int, float, SECONDARY_STRATUM_FILTER)
)
TRANSITION_ATTRIBUTE_REPORT = (
    'transition-attributes',
    models.TransitionAttributeSummaryReport,
    models.TransitionAttributeSummaryReportRow,
    config.TRANSITION_ATTRIBUTE_SUMMARY_ROW,
    (int, int, STRATUM_FILTER, TRANSITION_ATTRIBUTE_FILTER, default_int, default_int, float, SECONDARY_STRATUM_FILTER)
)


class ReportImporter:
    """ A high-level interface for exporting reports and creating API-exposed reports. """

    def __init__(self, scenario, console):
        """
        Constructor
        :param scenario: Instance of Scenario
        :param console: Instance of STSimConsole
        """
        self.scenario = scenario
        self.console = console
        self.temp_file = get_random_csv(scenario.library.tmp_file)

    def generate_report(self, report_name):
        """
        Create a CSV report corresponding to the appropriate name.
        :param report_name: The name of the ST-Sim report to export.
        """
        self.console.generate_report(report_name, self.temp_file, self.scenario.sid)

    def _create_report_summary(self, report_config):
        name, model, row_model, sheet_map, type_map = report_config
        project = self.scenario.project

        def map_row(row_data):
            """ Map a row of data using the sheet_map and type_map. """
            objects = {}
            for pair, type_or_filter in zip(sheet_map, type_map):
                model_field, sheet_field = pair
                data = row_data[sheet_field]
                is_filter = not (isinstance(type_or_filter, type) or isfunction(type_or_filter))
                objects[model_field] = type_or_filter.get(data, project) if is_filter else type_or_filter(data)
            return objects

        self.generate_report(name)
        report, created = model.objects.get_or_create(scenario=self.scenario)
        with open(self.temp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                row_model.objects.create(report=report, **map_row(row))

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

    def create_all_reports(self):
        self.create_stateclass_summary()
        self.create_transition_summary()
        self.create_transition_sc_summary()
        self.create_state_attribute_summary()
        self.create_transition_attribute_summary()
