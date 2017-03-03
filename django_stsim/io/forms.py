"""
    This file contains all the necessary validators for importing a sheet into SyncroSim.
"""

from rest_framework import serializers

from django_stsim.models import Stratum, SecondaryStratum, StateClass, TransitionType, Transition


def gen_name_field():
    return serializers.SlugRelatedField(
        many=False,
        slug_field='name',
        read_only=True
    )


class ImportSerializerBase(serializers.ModelSerializer):
    """
        Base serializer for validating sheets.

        Usage:
            Data to be validated against this sheet should match against the data available
            rom the model specified in the Meta class.

            name_pairs is a 1-to-1 matching of the Django-ORM names to STSim names.
            extra_names is used as convenience for importing blank values for values not yet handled.

            None values are returned as empty strings

            Otherwise, data is returned according to the Django-ORM type specified in models.py
    """
    name_pairs = ()
    extra_names = ()

    def transform(self):
        """
        Transforms the names in the model to the names used in STSim.
        :return:
        """
        transformed_data = dict()
        # Fill fields from validated data
        for attr in self.data.items():
            for pair in self.name_pairs:
                if attr[0] == pair[0]:
                    transformed_data[pair[1]] = attr[1] if attr[1] is not None else ''
                    break

        # Now handle names which we don't handle yet.
        for unhandled in self.extra_names:
            transformed_data[unhandled] = ''

        return transformed_data


def validate_sheet(rows, sheet_serializer):
    """
    Utility for validating multiple rows of data with a given import utility
    :param rows:
    :param sheet_serializer:
    :return:
    """
    validated_rows = []
    if not issubclass(sheet_serializer, ImportSerializerBase):
        raise serializers.ValidationError('Must use serializer derived from ImportSerializerBase')

    for row in rows:
        try:
            validated_row = sheet_serializer(row).transform()
            validated_rows.append(validated_row)
        except:
            raise serializers.ValidationError("Malformed data when importing sheet.")

    return validated_rows

# TODO - Add DeterministicTransitionImport


class TransitionImport(ImportSerializerBase):

    name_pairs = (('stratum_src', 'StratumIDSource'),
                  ('stateclass_src', 'StateClassIDSource'),
                  ('stratum_dest', 'StratumIDDest'),
                  ('stateclass_dest', 'StateClassIDDest'),
                  ('transition_type', 'TransitionTypeID'),
                  ('probability', 'Probability'),
                  ('age_reset', 'AgeReset'))

    extra_names = ('Proportion', 'AgeMin', 'AgeMax', 'AgeRelative',
                   'TSTMin', 'TSTMax', 'TSTRelative')

    stratum_src = gen_name_field()
    stateclass_src = gen_name_field()
    stratum_dest = gen_name_field()
    stateclass_dest = gen_name_field()
    transition_type = gen_name_field()

    class Meta:
        model = Transition
        fields = ('stratum_src', 'stateclass_src', 'stratum_dest', 'stateclass_dest',
                  'transition_type', 'probability', 'age_reset')

# TODO - Add DeterministicTransitionImport
