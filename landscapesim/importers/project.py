import csv

from landscapesim import models
from landscapesim.io.types import default_int, empty_or_yes_to_bool
from landscapesim.io.utils import get_random_csv


class ProjectImporter:

    def __init__(self, project, console):
        self.project = project
        self.console = console

    def _import_table(self, config):
        pass

    def process_project_definitions(self):
        tmp_file = get_random_csv(self.project.library.tmp_file)
        kwgs = {'pid': self.project.pid, 'overwrite': True, 'orig': True}

        # Import terminology
        self.console.export_sheet('STSim_Terminology', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            terms = [r for r in reader][0]
            models.Terminology.objects.create(
                project=self.project,
                amount_label=terms['AmountLabel'],
                amount_units=terms['AmountUnits'],
                state_label_x=terms['StateLabelX'],
                state_label_y=terms['StateLabelY'],
                primary_stratum_label=terms['PrimaryStratumLabel'],
                secondary_stratum_label=terms['SecondaryStratumLabel'],
                timestep_units=terms['TimestepUnits']
            )
        print('Imported terminology for project {}.'.format(self.project.name))

        self.console.export_sheet('Stats_DistributionType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.DistributionType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description'],
                    is_internal=empty_or_yes_to_bool(row['IsInternal'])
                )
        print('Imported distribution types for project {}.'.format(self.project.name))

        # Import strata
        self.console.export_sheet('STSim_Stratum', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.Stratum.objects.create(
                    stratum_id=default_int(row['ID']),
                    project=self.project,
                    name=row['Name'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported strata for project {}.'.format(self.project.name))

        # import secondary strata
        self.console.export_sheet('STSim_SecondaryStratum', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.SecondaryStratum.objects.create(
                    project=self.project,
                    secondary_stratum_id=default_int(row['ID']),
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported secondary strata for project {}.'.format(self.project.name))

        # import stateclasses
        self.console.export_sheet('STSim_StateClass', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.StateClass.objects.create(
                    stateclass_id=default_int(row['ID']),
                    project=self.project,
                    name=row['Name'],
                    state_label_x=row['StateLabelXID'],
                    state_label_y=row['StateLabelYID'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported state classes for project {}.'.format(self.project.name))

        # import transition types
        self.console.export_sheet('STSim_TransitionType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionType.objects.create(
                    project=self.project,
                    transition_type_id=default_int(row['ID']),
                    name=row['Name'],
                    color=row['Color'],
                    description=row['Description']
                )
        print('Imported transition types for project {}.'.format(self.project.name))

        # import transition groups
        self.console.export_sheet('STSim_TransitionGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionGroup.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported transition groups for project {}.'.format(self.project.name))

        # map transition groups to transition types
        self.console.export_sheet('STSim_TransitionTypeGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionTypeGroup.objects.create(
                    project=self.project,
                    transition_type=models.TransitionType.objects.filter(
                        name__exact=row['TransitionTypeID'], project=self.project
                    ).first(),
                    transition_group=models.TransitionGroup.objects.filter(
                        name__exact=row['TransitionGroupID'], project=self.project
                    ).first(),
                    is_primary=row['IsPrimary']
                )
        print('Imported transition type groups for project {}.'.format(self.project.name))

        # import transition multiplier types
        self.console.export_sheet('STSim_TransitionMultiplierType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionMultiplierType.objects.create(
                    project=self.project,
                    name=row['Name']
                )
        print('Imported transition multiplier types for project {}.'.format(self.project.name))

        # Import attribute groups
        self.console.export_sheet('STSim_AttributeGroup', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.AttributeGroup.objects.create(
                    project=self.project,
                    name=row['Name'],
                    description=row['Description']
                )
        print('Imported attribute groups for project {}.'.format(self.project.name))

        # Import state attribute types
        self.console.export_sheet('STSim_StateAttributeType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.StateAttributeType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    attribute_group=models.AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                                         project=self.project).first(),
                    units=row['Units'],
                    description=row['Description']
                )
        print('Imported state attribute types for project {}.'.format(self.project.name))

        # Import transition attribute types
        self.console.export_sheet('STSim_TransitionAttributeType', tmp_file, **kwgs)
        with open(tmp_file, 'r') as sheet:
            reader = csv.DictReader(sheet)
            for row in reader:
                models.TransitionAttributeType.objects.create(
                    project=self.project,
                    name=row['Name'],
                    attribute_group=models.AttributeGroup.objects.filter(name__exact=row['AttributeGroupID'],
                                                                         project=self.project).first(),
                    units=row['Units'],
                    description=row['Description']
                )
        print('Imported transition attribute types for project {}.'.format(self.project.name))

