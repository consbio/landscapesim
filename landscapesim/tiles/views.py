import json

import mercantile
from clover.geometry.bbox import BBox
from clover.utilities.color import Color
from ncdjango.config import RenderConfiguration, ImageConfiguration, LegendConfiguration
from ncdjango.views import GetImageViewBase, LegendViewBase
from pyproj import Proj

TILE_SIZE = (256, 256)
TRANSPARENT_BACKGROUND_COLOR = Color(255, 255, 255, 0)


class GetImageView(GetImageViewBase):
    def get_service_name(self, request, *args, **kwargs):
        return kwargs['service_name']

    def get_render_configurations(self, request, **kwargs):
        tile_bounds = list(mercantile.bounds(int(self.kwargs['x']), int(self.kwargs['y']), int(self.kwargs['z'])))
        extent = BBox(tile_bounds, projection=Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')).project(
            Proj(
                '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
            )
        )

        base_config = ImageConfiguration(
            extent=extent,
            size=TILE_SIZE,
            image_format='png',
            background_color=TRANSPARENT_BACKGROUND_COLOR
        )

        return base_config, [
            RenderConfiguration(
                variable=x,
                extent=extent,
                size=TILE_SIZE,
                image_format='png'
            ) for x in self.service.variable_set.all()
        ]


class GetTimeSeriesImageView(GetImageViewBase):
    def get_service_name(self, request, *args, **kwargs):
        return kwargs['service_name']

    def get_render_configurations(self, request, **kwargs):
        tile_bounds = list(mercantile.bounds(int(self.kwargs['x']), int(self.kwargs['y']), int(self.kwargs['z'])))
        extent = BBox(tile_bounds, projection=Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')).project(
            Proj(
                '+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
            )
        )

        base_config = ImageConfiguration(
            extent=extent,
            size=TILE_SIZE,
            image_format='png',
            background_color=TRANSPARENT_BACKGROUND_COLOR
        )

        variable = self.service.variable_set.filter(name__exact=self.kwargs['layer_name']).first()
        t = int(self.kwargs['t'])

        return base_config, [RenderConfiguration(
            variable=variable,
            extent=extent,
            size=TILE_SIZE,
            image_format='png',
            time_index=t
        )]


class GetLegendView(LegendViewBase):

    def get_service_name(self, request, *args, **kwargs):
        return kwargs['service_name']

    def serialize_data(self, data):
        variable = list(data.keys())[0]
        elements = data[variable]
        output = {
            'name': variable.name,
            'legend': [
                {
                    'label': element.labels[0],
                    'image_data': element.image_base64,
                    'content_type': 'image/png',
                    'height': element.image.size[1] if element.image else None,
                    'width': element.image.size[0] if element.image else None
                } for element in elements
            ]
        }
        return json.dumps(output), 'application/json'

    def get_legend_configurations(self, request, **kwargs):
        return [LegendConfiguration(
            variable=self.service.variable_set.filter(name__exact=self.kwargs['layer_name']).first()
        )]
