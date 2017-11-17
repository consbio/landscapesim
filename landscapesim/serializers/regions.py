import json

from rest_framework import serializers

from landscapesim.models import ReportingUnit, Region


class ReportingUnitSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()

    class Meta:
        model = ReportingUnit
        fields = ('type', 'geometry', 'properties',)

    def get_type(self, obj):
        return 'Feature'

    def get_geometry(self, obj):
        return json.loads(obj.polygons.json)

    def get_properties(self, obj):
        return {
            'id': obj.id,
            'unit_id': obj.unit_id,
            'name': obj.name
        }


class RegionSerializer(serializers.ModelSerializer):
    polygons = ReportingUnitSerializer(many=True, read_only=True)

    class Meta:
        model = Region
        exclude = ('path',)
