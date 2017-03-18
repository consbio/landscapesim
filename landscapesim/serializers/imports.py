from collections import OrderedDict
from rest_framework.serializers import ValidationError
from landscapesim import models as named_models
from landscapesim.io.utils import default_int_to_empty_or_int, bool_to_empty_or_yes
from landscapesim.io import config


class BaseImportSerializer(object):
    """
        Base serializer for transforming serialized data into csv sheets.
        We take inspiration from rest_framework's BaseSerializer and use our own mapping routine,
        defined in landscapesim.io.config
    """

    sheet_map = ()

    def __init__(self, initial_data, ignore_scenario_id=True):
        self._initial_data = initial_data
        self._ignore_scenario_id = ignore_scenario_id

    def _ignore(self, val):
        if val == 'id':
            return True
        elif val == 'scenario' and self._ignore_scenario_id:
            return True
        return False

    def _transform(self):
        """
        Transforms the names in the model to the names used in STSim.
        :return: An OrderedDict of initial_data with fieldnames ordered how they should be imported.
        """
        transformed_data = OrderedDict()
        # Fill fields from validated data
        for pair in self.sheet_map:
            for attr in self._initial_data.items():

                if self._ignore(attr[0]):
                    continue

                if attr[0] == pair[0]:
                    ssim_name = pair[1]
                    transformed_data[ssim_name] = attr[1] if attr[1] is not None else ''

                    # Handle type tranforms
                    # Convert pk-related fields to the value of it's name field
                    print(type(transformed_data[ssim_name]))
                    print(len(pair))
                    print(pair)
                    if len(pair) == 3 and type(transformed_data[ssim_name]) is int:
                        django_name = pair[2]
                        id = transformed_data[ssim_name]
                        if id > 0:
                            print('converted {}'.format(id))
                            transformed_data[ssim_name] = getattr(named_models, django_name).objects.get(id=id).name

                    # Convert bools to Yes or empty string
                    if type(transformed_data[ssim_name]) is bool:
                        transformed_data[ssim_name] = bool_to_empty_or_yes(transformed_data[ssim_name])

                    # Filter default integers (-1) to empty string
                    elif type(transformed_data[ssim_name]) is int:
                        transformed_data[ssim_name] = default_int_to_empty_or_int(transformed_data[ssim_name])
                    break

        if len(list(transformed_data.keys())) != len(self.sheet_map):
            raise ValidationError("Invalid conversion occured. Didn't satisfy all values stored in this serializer's"
                                  "sheet_map configuration")

        return transformed_data

    @property
    def validated_data(self):
        return self._transform()


class DistributionValueImport(BaseImportSerializer):

    sheet_map = config.DISTRIBUTION_VALUE


class OutputOptionImport(BaseImportSerializer):

    sheet_map = config.OUTPUT_OPTION


class RunControlImport(BaseImportSerializer):

    sheet_map = config.RUN_CONTROL


class DeterministicTransitionImport(BaseImportSerializer):

    sheet_map = config.DETERMINISTIC_TRANSITION


class TransitionImport(BaseImportSerializer):

    sheet_map = config.TRANSITION


class InitialConditionsNonSpatialImport(BaseImportSerializer):

    sheet_map = config.INITIAL_CONDITIONS_NON_SPATIAL


class InitialConditionsNonSpatialDistributionImport(BaseImportSerializer):

    sheet_map = config.INITIAL_CONDITIONS_NON_SPATIAL_DISTRIBUTION


class InitialConditionsSpatialImport(BaseImportSerializer):

    sheet_map = config.INITIAL_CONDITIONS_SPATIAL


class TransitionTargetImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_TARGET


class TransitionMultiplierValueImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_MULTIPLIER_VALUE


class TransitionSizeDistributionImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_SIZE_DISTRIBUTION


class TransitionSizePrioritizationImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_SIZE_PRIORITIZATION


class StateAttributeValueImport(BaseImportSerializer):

    sheet_map = config.STATE_ATTRIBUTE_VALUE


class TransitionAttributeValueImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_ATTRIBUTE_VALUE


class TransitionAttributeTargetImport(BaseImportSerializer):

    sheet_map = config.TRANSITION_ATTRIBUTE_TARGET
