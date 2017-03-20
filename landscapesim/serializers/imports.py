import inspect
from collections import OrderedDict
from django.db import models
from rest_framework.serializers import ValidationError
from landscapesim.io.utils import default_int_to_empty_or_int, bool_to_empty_or_yes
from landscapesim.io import config
from landscapesim.serializers import scenarios as serializers


class BaseImportSerializer(object):
    """
        Base serializer for transforming serialized data into csv sheets.
        We take inspiration from rest_framework's BaseSerializer and use our own mapping routine,
        defined in landscapesim.io.config
    """

    drf_serializer = None
    sheet_map = ()

    def __init__(self, initial_data):
        self._initial_data = initial_data
        self._many = type(initial_data) is list

    def _ignore(self, val):
        if val == 'id':
            return True
        elif val == 'scenario':
            return True
        return False

    def _transform(self, data):
        """
        Transforms the names in the model to the names used in STSim.
        :return: An OrderedDict of initial_data with fieldnames ordered how they should be imported.
        """
        transformed_data = OrderedDict()
        # Fill fields from validated data
        for pair in self.sheet_map:
            for attr in data.items():
                if self._ignore(attr[0]):
                    continue

                if attr[0] == pair[0]:
                    ssim_name = pair[1]
                    transformed_data[ssim_name] = attr[1] if attr[1] is not None else ''

                    # Convert pk-related fields to the value of it's name field
                    is_django_model = inspect.isclass(type(transformed_data[ssim_name])) and \
                                      issubclass(type(transformed_data[ssim_name]), models.Model)

                    # Handle type tranforms
                    if is_django_model:
                        transformed_data[ssim_name] = transformed_data[ssim_name].name

                    # Convert bools to Yes or empty string
                    if type(transformed_data[ssim_name]) is bool:
                        transformed_data[ssim_name] = bool_to_empty_or_yes(transformed_data[ssim_name])

                    # Filter default integers (-1) to empty string
                    elif type(transformed_data[ssim_name]) is int:
                        transformed_data[ssim_name] = default_int_to_empty_or_int(transformed_data[ssim_name])
                    break

        if len(list(transformed_data.keys())) != len(self.sheet_map):
            # Determine missing keys
            missing = [x[0] for x in self.sheet_map if x[0] not in transformed_data.keys()]
            raise ValidationError("Invalid conversion occured. Didn't satisfy all values stored in this serializer's "
                                  "sheet_map configuration. Missing: {}".format(', '.join(missing)))

        return transformed_data

    @property
    def validated_data(self):
        """
        Validates and transforms (lists of) data to match importable csv data.
        :return:
        """
        deserialized_data = self.drf_serializer(data=self._initial_data, many=self._many)
        if deserialized_data.is_valid(True):
            deserialized_data = deserialized_data.validated_data
            if self._many:
                return [self._transform(x) for x in deserialized_data]
            else:
                return self._transform(deserialized_data)
        else:
            raise ValidationError("Error deserializing drf_serializer.")


class DistributionValueImport(BaseImportSerializer):
    drf_serializer = serializers.DistributionValueSerializer
    sheet_map = config.DISTRIBUTION_VALUE


class OutputOptionImport(BaseImportSerializer):
    drf_serializer = serializers.OutputOptionSerializer
    sheet_map = config.OUTPUT_OPTION


class RunControlImport(BaseImportSerializer):
    drf_serializer = serializers.RunControlSerializer
    sheet_map = config.RUN_CONTROL


class DeterministicTransitionImport(BaseImportSerializer):
    drf_serializer = serializers.DeterministicTransitionSerializer
    sheet_map = config.DETERMINISTIC_TRANSITION


class TransitionImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionSerializer
    sheet_map = config.TRANSITION


class InitialConditionsNonSpatialImport(BaseImportSerializer):
    drf_serializer = serializers.InitialConditionsNonSpatial
    sheet_map = config.INITIAL_CONDITIONS_NON_SPATIAL


class InitialConditionsNonSpatialDistributionImport(BaseImportSerializer):
    drf_serializer = serializers.InitialConditionsNonSpatialDistributionSerializer
    sheet_map = config.INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION


class InitialConditionsSpatialImport(BaseImportSerializer):
    drf_serializer = serializers.InitialConditionsSpatialSerializer
    sheet_map = config.INITIAL_CONDITIONS_SPATIAL


class TransitionTargetImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionTargetSerializer
    sheet_map = config.TRANSITION_TARGET


class TransitionMultiplierValueImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionMultiplierValueSerializer
    sheet_map = config.TRANSITION_MULTIPLIER_VALUE


class TransitionSizeDistributionImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionSizeDistributionSerializer
    sheet_map = config.TRANSITION_SIZE_DISTRIBUTION


class TransitionSizePrioritizationImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionSizePrioritizationSerializer
    sheet_map = config.TRANSITION_SIZE_PRIORITIZATION


class StateAttributeValueImport(BaseImportSerializer):
    drf_serializer = serializers.StateAttributeValueSerializer
    sheet_map = config.STATE_ATTRIBUTE_VALUE


class TransitionAttributeValueImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionAttributeValueSerializer
    sheet_map = config.TRANSITION_ATTRIBUTE_VALUE


class TransitionAttributeTargetImport(BaseImportSerializer):
    drf_serializer = serializers.TransitionAttributeTargetSerializer
    sheet_map = config.TRANSITION_ATTRIBUTE_TARGET
