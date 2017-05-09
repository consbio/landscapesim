# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ncdjango', '0004_auto_20170508_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DeterministicTransition',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('location', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DistributionType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('is_internal', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='DistributionValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('dmin', models.FloatField(null=True, blank=True)),
                ('dmax', models.FloatField()),
                ('relative_frequency', models.FloatField(null=True, blank=True)),
                ('distribution_type', models.ForeignKey(to='landscapesim.DistributionType')),
            ],
        ),
        migrations.CreateModel(
            name='InitialConditionsNonSpatial',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('total_amount', models.FloatField()),
                ('num_cells', models.IntegerField()),
                ('calc_from_dist', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='InitialConditionsNonSpatialDistribution',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('relative_amount', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InitialConditionsSpatial',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('num_rows', models.IntegerField()),
                ('num_cols', models.IntegerField()),
                ('num_cells', models.IntegerField()),
                ('cell_size', models.IntegerField()),
                ('cell_size_units', models.CharField(max_length=100)),
                ('cell_area', models.FloatField()),
                ('cell_area_override', models.BooleanField(default=False)),
                ('xll_corner', models.FloatField()),
                ('yll_corner', models.FloatField()),
                ('srs', models.CharField(max_length=500)),
                ('stratum_file_name', models.CharField(max_length=100)),
                ('secondary_stratum_file_name', models.CharField(max_length=100)),
                ('stateclass_file_name', models.CharField(max_length=100)),
                ('age_file_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=50)),
                ('file', models.FilePathField(match='*.ssim')),
                ('orig_file', models.FilePathField(match='*.ssim')),
                ('tmp_file', models.FilePathField()),
            ],
        ),
        migrations.CreateModel(
            name='OutputOption',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sum_sc', models.BooleanField(default=False)),
                ('sum_sc_t', models.IntegerField(null=True)),
                ('sum_sc_zeros', models.BooleanField(default=False)),
                ('raster_sc', models.BooleanField(default=False)),
                ('raster_sc_t', models.IntegerField(null=True)),
                ('sum_tr', models.BooleanField(default=False)),
                ('sum_tr_t', models.IntegerField(null=True)),
                ('sum_tr_interval', models.BooleanField(default=False)),
                ('raster_tr', models.BooleanField(default=False)),
                ('raster_tr_t', models.IntegerField(null=True)),
                ('sum_trsc', models.BooleanField(default=False)),
                ('sum_trsc_t', models.IntegerField(null=True)),
                ('sum_sa', models.BooleanField(default=False)),
                ('sum_sa_t', models.IntegerField(null=True)),
                ('raster_sa', models.BooleanField(default=False)),
                ('raster_sa_t', models.IntegerField(null=True)),
                ('sum_ta', models.BooleanField(default=False)),
                ('sum_ta_t', models.IntegerField(null=True)),
                ('raster_ta', models.BooleanField(default=False)),
                ('raster_ta_t', models.IntegerField(null=True)),
                ('raster_strata', models.BooleanField(default=False)),
                ('raster_strata_t', models.IntegerField(null=True)),
                ('raster_age', models.BooleanField(default=False)),
                ('raster_age_t', models.IntegerField(null=True)),
                ('raster_tst', models.BooleanField(default=True)),
                ('raster_tst_t', models.IntegerField(null=True)),
                ('raster_aatp', models.BooleanField(default=False)),
                ('raster_aatp_t', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('pid', models.PositiveSmallIntegerField()),
                ('library', models.ForeignKey(related_name='projects', to='landscapesim.Library')),
            ],
        ),
        migrations.CreateModel(
            name='RunControl',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('min_iteration', models.IntegerField()),
                ('max_iteration', models.IntegerField()),
                ('min_timestep', models.IntegerField()),
                ('max_timestep', models.IntegerField()),
                ('is_spatial', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RunScenarioModel',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('uuid', models.CharField(db_index=True, max_length=36, default=uuid.uuid4)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('celery_id', models.CharField(max_length=100)),
                ('inputs', models.TextField(default='{}')),
                ('outputs', models.TextField(default='{}')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('is_result', models.BooleanField(default=False)),
                ('sid', models.PositiveSmallIntegerField()),
                ('is_dependency_of', models.ForeignKey(blank=True, null=True, to='landscapesim.Scenario')),
                ('project', models.ForeignKey(related_name='scenarios', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ScenarioInputServices',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age', models.ForeignKey(null=True, related_name='age_input_service', to='ncdjango.Service')),
                ('scenario', models.OneToOneField(related_name='scenario_input_services', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(null=True, related_name='secondary_stratum_input_service', to='ncdjango.Service')),
                ('stateclass', models.ForeignKey(null=True, related_name='stateclass_input_service', to='ncdjango.Service')),
                ('stratum', models.ForeignKey(null=True, related_name='stratum_input_service', to='ncdjango.Service')),
            ],
        ),
        migrations.CreateModel(
            name='ScenarioOutputServices',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age', models.ForeignKey(null=True, related_name='age_output_service', to='ncdjango.Service')),
                ('avg_annual_transition_group_probability', models.ForeignKey(null=True, related_name='avg_annual_transition_probability_output_service', to='ncdjango.Service')),
                ('scenario', models.OneToOneField(related_name='scenario_output_services', to='landscapesim.Scenario')),
                ('state_attribute', models.ForeignKey(null=True, related_name='state_attribute_output_service', to='ncdjango.Service')),
                ('stateclass', models.ForeignKey(null=True, related_name='stateclass_output_service', to='ncdjango.Service')),
                ('stratum', models.ForeignKey(null=True, related_name='stratum_output_service', to='ncdjango.Service')),
                ('transition_attribute', models.ForeignKey(null=True, related_name='transition_attribute_output_service', to='ncdjango.Service')),
                ('transition_group', models.ForeignKey(null=True, related_name='transition_group_output_service', to='ncdjango.Service')),
                ('tst', models.ForeignKey(null=True, related_name='tst_output_service', to='ncdjango.Service')),
            ],
        ),
        migrations.CreateModel(
            name='SecondaryStratum',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('secondary_stratum_id', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='secondary_strata', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='StateAttributeSummaryReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('scenario', models.OneToOneField(related_name='state_attribute_summary_report', to='landscapesim.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='StateAttributeSummaryReportRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('iteration', models.IntegerField()),
                ('timestep', models.IntegerField()),
                ('amount', models.FloatField()),
                ('report', models.ForeignKey(related_name='results', to='landscapesim.StateAttributeSummaryReport')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StateAttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('units', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('attribute_group', models.ForeignKey(blank=True, null=True, to='landscapesim.AttributeGroup')),
                ('project', models.ForeignKey(related_name='state_attributes', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='StateAttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('value', models.FloatField()),
                ('scenario', models.ForeignKey(related_name='state_attribute_values', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('state_attribute_type', models.ForeignKey(to='landscapesim.StateAttributeType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StateClass',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('stateclass_id', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=100)),
                ('state_label_x', models.CharField(max_length=100)),
                ('state_label_y', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='stateclasses', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='StateClassSummaryReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('scenario', models.OneToOneField(related_name='stateclass_summary_report', to='landscapesim.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='StateClassSummaryReportRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('iteration', models.IntegerField()),
                ('timestep', models.IntegerField()),
                ('amount', models.FloatField()),
                ('proportion_of_landscape', models.FloatField()),
                ('proportion_of_stratum', models.FloatField()),
                ('report', models.ForeignKey(related_name='results', to='landscapesim.StateClassSummaryReport')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stateclass', models.ForeignKey(to='landscapesim.StateClass')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stratum',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('stratum_id', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='strata', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Terminology',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('amount_label', models.CharField(max_length=100)),
                ('amount_units', models.CharField(max_length=100)),
                ('state_label_x', models.CharField(max_length=100)),
                ('state_label_y', models.CharField(max_length=100)),
                ('primary_stratum_label', models.CharField(max_length=100)),
                ('secondary_stratum_label', models.CharField(max_length=100)),
                ('timestep_units', models.CharField(max_length=100)),
                ('project', models.OneToOneField(related_name='terminology', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('probability', models.FloatField()),
                ('proportion', models.FloatField(null=True, blank=True)),
                ('age_relative', models.FloatField(null=True, blank=True)),
                ('age_reset', models.BooleanField(default=False)),
                ('tst_min', models.FloatField(null=True, blank=True)),
                ('tst_max', models.FloatField(null=True, blank=True)),
                ('tst_relative', models.FloatField(null=True, blank=True)),
                ('scenario', models.ForeignKey(related_name='transitions', to='landscapesim.Scenario')),
                ('stateclass_dest', models.ForeignKey(related_name='stateclass_dest', to='landscapesim.StateClass')),
                ('stateclass_src', models.ForeignKey(related_name='stateclass_src', to='landscapesim.StateClass')),
                ('stratum_dest', models.ForeignKey(blank=True, null=True, related_name='stratum_dest', to='landscapesim.Stratum')),
                ('stratum_src', models.ForeignKey(related_name='stratum_src', to='landscapesim.Stratum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionAttributeSummaryReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('scenario', models.OneToOneField(related_name='transition_attribute_summary_report', to='landscapesim.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionAttributeSummaryReportRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('iteration', models.IntegerField()),
                ('timestep', models.IntegerField()),
                ('amount', models.FloatField()),
                ('report', models.ForeignKey(related_name='results', to='landscapesim.TransitionAttributeSummaryReport')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stratum', models.ForeignKey(to='landscapesim.Stratum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionAttributeTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('distribution_sd', models.FloatField(null=True, blank=True)),
                ('distribution_min', models.FloatField(null=True, blank=True)),
                ('distribution_max', models.FloatField(null=True, blank=True)),
                ('target', models.FloatField()),
                ('distribution_type', models.ForeignKey(blank=True, null=True, to='landscapesim.DistributionType')),
                ('scenario', models.ForeignKey(related_name='transition_attribute_targets', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionAttributeType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('units', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('attribute_group', models.ForeignKey(blank=True, null=True, to='landscapesim.AttributeGroup')),
                ('project', models.ForeignKey(related_name='transition_attributes', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionAttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('value', models.FloatField()),
                ('scenario', models.ForeignKey(related_name='transition_attribute_values', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stateclass', models.ForeignKey(blank=True, null=True, to='landscapesim.StateClass')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
                ('transition_attribute_type', models.ForeignKey(to='landscapesim.TransitionAttributeType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionByStateClassSummaryReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('scenario', models.OneToOneField(related_name='transition_by_sc_summary_report', to='landscapesim.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionByStateClassSummaryReportRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('iteration', models.IntegerField()),
                ('timestep', models.IntegerField()),
                ('amount', models.FloatField()),
                ('report', models.ForeignKey(related_name='results', to='landscapesim.TransitionByStateClassSummaryReport')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stateclass_dest', models.ForeignKey(related_name='stateclass_dest_tscr', to='landscapesim.StateClass')),
                ('stateclass_src', models.ForeignKey(related_name='stateclass_src_tscr', to='landscapesim.StateClass')),
                ('stratum', models.ForeignKey(to='landscapesim.Stratum')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='transition_groups', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionMultiplierType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='transition_multiplier_types', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionMultiplierValue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('distribution_sd', models.FloatField(null=True, blank=True)),
                ('distribution_min', models.FloatField(null=True, blank=True)),
                ('distribution_max', models.FloatField(null=True, blank=True)),
                ('multiplier', models.FloatField()),
                ('distribution_type', models.ForeignKey(blank=True, null=True, to='landscapesim.DistributionType')),
                ('scenario', models.ForeignKey(related_name='transition_multiplier_values', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stateclass', models.ForeignKey(blank=True, null=True, to='landscapesim.StateClass')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
                ('transition_multiplier_type', models.ForeignKey(blank=True, null=True, to='landscapesim.TransitionMultiplierType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionSizeDistribution',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('maximum_area', models.FloatField()),
                ('relative_amount', models.FloatField()),
                ('scenario', models.ForeignKey(related_name='transition_size_distributions', to='landscapesim.Scenario')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionSizePrioritization',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('priority', models.CharField(max_length=25)),
                ('scenario', models.ForeignKey(related_name='transition_size_prioritizations', to='landscapesim.Scenario')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
                ('transition_group', models.ForeignKey(blank=True, null=True, to='landscapesim.TransitionGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionSpatialMultiplier',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('transition_multiplier_file_name', models.CharField(max_length=100)),
                ('scenario', models.ForeignKey(related_name='transition_spatial_multipliers', to='landscapesim.Scenario')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
                ('transition_multiplier_type', models.ForeignKey(blank=True, null=True, to='landscapesim.TransitionMultiplierType')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionSummaryReport',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('scenario', models.OneToOneField(related_name='transition_summary_report', to='landscapesim.Scenario')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionSummaryReportRow',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('age_min', models.IntegerField(default=-1)),
                ('age_max', models.IntegerField(default=-1)),
                ('iteration', models.IntegerField()),
                ('timestep', models.IntegerField()),
                ('amount', models.FloatField()),
                ('report', models.ForeignKey(related_name='results', to='landscapesim.TransitionSummaryReport')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stratum', models.ForeignKey(to='landscapesim.Stratum')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('timestep', models.IntegerField(null=True, blank=True)),
                ('iteration', models.IntegerField(null=True, blank=True)),
                ('distribution_sd', models.FloatField(null=True, blank=True)),
                ('distribution_min', models.FloatField(null=True, blank=True)),
                ('distribution_max', models.FloatField(null=True, blank=True)),
                ('target_area', models.FloatField()),
                ('distribution_type', models.ForeignKey(blank=True, null=True, to='landscapesim.DistributionType')),
                ('scenario', models.ForeignKey(related_name='transition_targets', to='landscapesim.Scenario')),
                ('secondary_stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum')),
                ('stratum', models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransitionType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('transition_type_id', models.IntegerField(default=-1)),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=100)),
                ('project', models.ForeignKey(related_name='transition_types', to='landscapesim.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TransitionTypeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('is_primary', models.CharField(max_length=3, default='')),
                ('project', models.ForeignKey(related_name='transition_type_groups', to='landscapesim.Project')),
                ('transition_group', models.ForeignKey(to='landscapesim.TransitionGroup')),
                ('transition_type', models.ForeignKey(to='landscapesim.TransitionType')),
            ],
        ),
        migrations.AddField(
            model_name='transitionbystateclasssummaryreportrow',
            name='transition_type',
            field=models.ForeignKey(to='landscapesim.TransitionType'),
        ),
        migrations.AddField(
            model_name='transitionattributevalue',
            name='transition_group',
            field=models.ForeignKey(to='landscapesim.TransitionGroup'),
        ),
        migrations.AddField(
            model_name='transitionattributetarget',
            name='transition_attribute_type',
            field=models.ForeignKey(to='landscapesim.TransitionAttributeType'),
        ),
        migrations.AddField(
            model_name='transitionattributesummaryreportrow',
            name='transition_attribute_type',
            field=models.ForeignKey(to='landscapesim.TransitionAttributeType'),
        ),
        migrations.AddField(
            model_name='transition',
            name='transition_type',
            field=models.ForeignKey(to='landscapesim.TransitionType'),
        ),
        migrations.AddField(
            model_name='stateclasssummaryreportrow',
            name='stratum',
            field=models.ForeignKey(to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='stateattributevalue',
            name='stateclass',
            field=models.ForeignKey(blank=True, null=True, to='landscapesim.StateClass'),
        ),
        migrations.AddField(
            model_name='stateattributevalue',
            name='stratum',
            field=models.ForeignKey(blank=True, null=True, to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='stateattributesummaryreportrow',
            name='state_attribute_type',
            field=models.ForeignKey(to='landscapesim.StateAttributeType'),
        ),
        migrations.AddField(
            model_name='stateattributesummaryreportrow',
            name='stratum',
            field=models.ForeignKey(to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='runscenariomodel',
            name='parent_scenario',
            field=models.ForeignKey(related_name='parent_scenario', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='runscenariomodel',
            name='result_scenario',
            field=models.ForeignKey(null=True, related_name='result_scenario', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='runcontrol',
            name='scenario',
            field=models.OneToOneField(related_name='run_control', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='outputoption',
            name='scenario',
            field=models.OneToOneField(related_name='output_options', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='initialconditionsspatial',
            name='scenario',
            field=models.OneToOneField(related_name='initial_conditions_spatial_settings', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='initialconditionsnonspatialdistribution',
            name='scenario',
            field=models.ForeignKey(related_name='initial_conditions_nonspatial_distributions', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='initialconditionsnonspatialdistribution',
            name='secondary_stratum',
            field=models.ForeignKey(blank=True, null=True, to='landscapesim.SecondaryStratum'),
        ),
        migrations.AddField(
            model_name='initialconditionsnonspatialdistribution',
            name='stateclass',
            field=models.ForeignKey(to='landscapesim.StateClass'),
        ),
        migrations.AddField(
            model_name='initialconditionsnonspatialdistribution',
            name='stratum',
            field=models.ForeignKey(related_name='stratum_ic', to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='initialconditionsnonspatial',
            name='scenario',
            field=models.OneToOneField(related_name='initial_conditions_nonspatial_settings', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='distributionvalue',
            name='scenario',
            field=models.ForeignKey(related_name='distribution_values', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='distributiontype',
            name='project',
            field=models.ForeignKey(related_name='distribution_types', to='landscapesim.Project'),
        ),
        migrations.AddField(
            model_name='deterministictransition',
            name='scenario',
            field=models.ForeignKey(related_name='deterministic_transitions', to='landscapesim.Scenario'),
        ),
        migrations.AddField(
            model_name='deterministictransition',
            name='stateclass_dest',
            field=models.ForeignKey(related_name='stateclass_dest_det', to='landscapesim.StateClass'),
        ),
        migrations.AddField(
            model_name='deterministictransition',
            name='stateclass_src',
            field=models.ForeignKey(related_name='stateclass_src_det', to='landscapesim.StateClass'),
        ),
        migrations.AddField(
            model_name='deterministictransition',
            name='stratum_dest',
            field=models.ForeignKey(blank=True, null=True, related_name='stratum_dest_det', to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='deterministictransition',
            name='stratum_src',
            field=models.ForeignKey(related_name='stratum_src_det', to='landscapesim.Stratum'),
        ),
        migrations.AddField(
            model_name='attributegroup',
            name='project',
            field=models.ForeignKey(related_name='attribute_groups', to='landscapesim.Project'),
        ),
    ]
