"""
    This file contains all the necessary validators for importing a sheet into SyncroSim.
"""

from rest_framework import serializers

from landscapesim.io.config import DISTRIBUTION_VALUE, RUN_CONTROL, OUTPUT_OPTION, DETERMINISTIC_TRANSITION, TRANSITION, \
    INITIAL_CONDITIONS_NON_SPATIAL, INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION, TRANSITION_TARGET, \
    TRANSITION_MULTIPLIER_VALUE, TRANSITION_SIZE_DISTRIBUTION, TRANSITION_SIZE_PRIORITIZATION, STATE_ATTRIBUTE_VALUE, \
    TRANSITION_ATTRIBUTE_VALUE, TRANSITION_ATTRIBUTE_TARGET

from landscapesim.models import DistributionValue, OutputOption, RunControl, DeterministicTransition, Transition, \
    InitialConditionsNonSpatial, InitialConditionsNonSpatialDistribution, TransitionTarget, \
    TransitionMultiplierValue, TransitionSizeDistribution, TransitionSizePrioritization, \
    StateAttributeValue, TransitionAttributeValue, TransitionAttributeTarget
from landscapesim.io.utils import default_int_to_empty_or_int, bool_to_empty_or_yes


def name_field():
    return serializers.SlugRelatedField(
        many=False,
        slug_field='name',
        read_only=True
    )


class ImportSerializerBase(serializers.ModelSerializer):
    """
        Base serializer for validating sheets into SyncroSim.

        Data to be serialized should match the data available
        from the model specified in the Meta class.

        sheet_map is a 1-to-1 matching of the Django-ORM names to STSim names.
        # extra_names is used as convenience for importing blank values for values not yet handled.

        Otherwise, data is returned according to the Django-ORM Field specified in models.py.
        This is done for solidifying the native python type we handle and syncronizing with the type
        that SyncroSim expects.
    """
    sheet_map = ()

    def transform(self):
        """
        Transforms the names in the model to the names used in STSim.
        :return:
        """
        transformed_data = dict()
        # Fill fields from validated data
        for attr in self.data.items():
            for pair in self.sheet_map:
                if attr[0] == pair[0]:
                    transformed_data[pair[1]] = attr[1] if attr[1] is not None else ''

                    # Handle type tranforms
                    if type(transformed_data[pair[1]]) is bool:
                        transformed_data[pair[1]] = bool_to_empty_or_yes(transformed_data[pair[1]])
                    elif type(transformed_data[pair[1]]) is int:
                        transformed_data[pair[1]] = default_int_to_empty_or_int(transformed_data[pair[1]])
                    break

        return transformed_data


def validate_sheet(rows, sheet_serializer):
    """
    Utility for validating multiple rows of data with a given import utility
    :param rows:
    :param sheet_serializer:
    :return:
    """
    validated_rows = []
    if type(rows) is not list:
        raise TypeError('rows argument must be list object')

    if not issubclass(sheet_serializer, ImportSerializerBase):
        raise serializers.ValidationError('Must use serializer derived from ImportSerializerBase')

    for row in rows:
        try:
            validated_row = sheet_serializer(row).transform()
            validated_rows.append(validated_row)
        except:
            raise serializers.ValidationError("Malformed data when importing sheet.")

    return validated_rows


class DistributionValueImport(ImportSerializerBase):

    sheet_map = DISTRIBUTION_VALUE

    class Meta:
        model = DistributionValue
        fields = '__all__'


class OutputOptionImport(ImportSerializerBase):

    sheet_map = OUTPUT_OPTION

    class Meta:
        model = OutputOption
        fields = '__all__'


class RunControlImport(ImportSerializerBase):

    sheet_map = RUN_CONTROL

    class Meta:
        model = RunControl
        fields = '__all__'


class DeterministicTransitionImport(ImportSerializerBase):

    sheet_map = DETERMINISTIC_TRANSITION

    class Meta:
        model = DeterministicTransition
        fields = '__all__'


class TransitionImport(ImportSerializerBase):

    sheet_map = TRANSITION

    stratum_src = name_field()
    stateclass_src = name_field()
    stratum_dest = name_field()
    stateclass_dest = name_field()
    transition_type = name_field()

    class Meta:
        model = Transition
        fields = '__all__'


class InitialConditionsNonSpatialImport(ImportSerializerBase):

    sheet_map = INITIAL_CONDITIONS_NON_SPATIAL

    class Meta:
        model = InitialConditionsNonSpatial
        fields = '__all__'


class InitialConditionsNonSpatialDistributionImport(ImportSerializerBase):
    sheet_map = INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION

    stratum = name_field()
    secondary_stratum = name_field()
    stateclass = name_field()

    class Meta:
        model = InitialConditionsNonSpatialDistribution
        fields = '__all__'


class TransitionTargetImport(ImportSerializerBase):
    sheet_map = TRANSITION_TARGET

    stratum = name_field()
    secondary_stratum = name_field()
    transition_group = name_field()
    distribution_type = name_field()

    class Meta:
        model = TransitionTarget
        fields = '__all__'


class TransitionMultiplierValueImport(ImportSerializerBase):
    sheet_map = TRANSITION_MULTIPLIER_VALUE

    stratum = name_field()
    secondary_stratum = name_field()
    stateclass = name_field()
    transition_multiplier_type = name_field()
    transition_group = name_field()
    distribution_type = name_field()

    class Meta:
        model = TransitionMultiplierValue
        fields = '__all__'


class TransitionSizeDistributionImport(ImportSerializerBase):
    sheet_map = TRANSITION_SIZE_DISTRIBUTION

    stratum = name_field()
    transition_group = name_field()

    class Meta:
        model = TransitionSizeDistribution
        fields = '__all__'


class TransitionSizePrioritizationImport(ImportSerializerBase):
    sheet_map = TRANSITION_SIZE_PRIORITIZATION

    stratum = name_field()
    transition_group = name_field()

    class Meta:
        model = TransitionSizePrioritization
        fields = '__all__'


class StateAttributeValueImport(ImportSerializerBase):
    sheet_map = STATE_ATTRIBUTE_VALUE

    stratum = name_field()
    secondary_stratum = name_field()
    stateclass = name_field()
    state_attribute_type = name_field()

    class Meta:
        model = StateAttributeValue
        fields = '__all__'


class TransitionAttributeValueImport(ImportSerializerBase):
    sheet_map = TRANSITION_ATTRIBUTE_VALUE

    stratum = name_field()
    secondary_stratum = name_field()
    transition_group = name_field()
    stateclass = name_field()
    transition_attribute_type = name_field()

    class Meta:
        model = TransitionAttributeValue
        fields = '__all__'


class TransitionAttributeTargetImport(ImportSerializerBase):
    sheet_map = TRANSITION_ATTRIBUTE_TARGET

    stratum = name_field()
    secondary_stratum = name_field()
    transition_attribute_type = name_field()
    distribution_type = name_field()

    class Meta:
        model = TransitionAttributeTarget
        fields = '__all__'
