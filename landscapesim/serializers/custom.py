from rest_framework import serializers
from django.core.urlresolvers import reverse
from landscapesim.models import ScenarioInputServices, ScenarioOutputServices


class ScenarioInputServicesSerializer(serializers.ModelSerializer):

    stratum = serializers.SerializerMethodField(allow_null=True)
    secondary_stratum = serializers.SerializerMethodField(allow_null=True)
    stateclass = serializers.SerializerMethodField(allow_null=True)
    age = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = ScenarioInputServices
        fields = ('stratum', 'secondary_stratum', 'stateclass', 'age')

    def _get_url(self, service):
        return '/'.join(reverse('tiles_get_image', args=[service.name, 0, 0, 0])
                        .split('/')[:-3] + ['{z}', '{x}', '{y}.png'])

    def get_stratum(self, obj):
        if obj.stratum:
            return self._get_url(obj.stratum)
        else:
            return None

    def get_stateclass(self, obj):
        if obj.stateclass:
            return self._get_url(obj.stateclass)
        else:
            return None

    def get_secondary_stratum(self, obj):
        if obj.secondary_stratum:
            return self._get_url(obj.secondary_stratum)
        else:
            return None

    def get_age(self, obj):
        if obj.age:
            return self._get_url(obj.age)
        else:
            return None


class ScenarioOutputServicesSerializer(serializers.ModelSerializer):

    stateclass = serializers.SerializerMethodField(allow_null=True)
    transition_group = serializers.SerializerMethodField(allow_null=True)
    age = serializers.SerializerMethodField(allow_null=True)
    tst = serializers.SerializerMethodField(allow_null=True)
    stratum = serializers.SerializerMethodField(allow_null=True)
    state_attribute = serializers.SerializerMethodField(allow_null=True)
    transition_attribute = serializers.SerializerMethodField(allow_null=True)
    avg_annual_transition_group_probability = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = ScenarioOutputServices
        fields = ('stateclass', 'transition_group', 'age', 'tst',
                  'stratum', 'state_attribute', 'transition_attribute',
                  'avg_annual_transition_group_probability')

    def _get_url(self, service):
        variable_name = service.variable_set.first().name
        path_parts = reverse('timeseries_tiles_get_image', args=[
            service.name, variable_name, 0, 0, 0, 0]).split('/')[:-5]
        iteration_pattern = variable_name[:-len(variable_name.split('-')[-1])] + '{it}'
        return '/'.join(path_parts + [iteration_pattern, '{z}', '{x}', '{y}', '{t}.png'])

    def get_stateclass(self, obj):
        if obj.stateclass:
            return self._get_url(obj.stateclass)
        else:
            return None

    def get_transition_group(self, obj):
        if obj.transition_group:
            return self._get_url(obj.transition_group)
        else:
            return None

    def get_age(self, obj):
        if obj.age:
            return self._get_url(obj.age)
        else:
            return None

    def get_tst(self, obj):
        if obj.tst:
            return self._get_url(obj.tst)
        else:
            return None

    def get_stratum(self, obj):
        if obj.stratum:
            return self._get_url(obj.stratum)
        else:
            return None

    def get_state_attribute(self, obj):
        if obj.state_attribute:
            return self._get_url(obj.state_attribute)
        else:
            return None

    def get_transition_attribute(self, obj):
        if obj.transition_attribute:
            return self._get_url(obj.transition_attribute)
        else:
            return None

    def get_avg_annual_transition_group_probability(self, obj):
        if obj.avg_annual_transition_group_probability:
            return self._get_url(obj.avg_annual_transition_group_probability)
        else:
            return None
