import asyncio
import math
import sys
from io import BytesIO
from json import loads

import aiohttp
import mercantile
from PIL import Image, ImageDraw
from clover.geometry.bbox import BBox
from clover.utilities.color import Color
from django.conf import settings
from django.contrib.gis.geometry.backend import Geometry
from ncdjango.geoimage import world_to_image, image_to_world
from pyproj import Proj, transform

ALLOWED_HOSTS = getattr(settings, 'ALLOWED_HOSTS')
PORT = getattr(settings, 'PORT', 80)

TILE_SIZE = (256, 256)
IMAGE_SIZE = (750, 500)


class MapImage(object):
    def __init__(self, center, bbox, zoom, basemap, opacity, size=None):

        self._configure_event_loop()
        point = center['geometry']['coordinates']
        if size is None:
            size = IMAGE_SIZE

        self.num_tiles = [math.ceil(size[x] / TILE_SIZE[x]) + 1 for x in (0, 1)]
        center_tile = mercantile.tile(point[0], point[1], zoom)

        mercator = Proj(init='epsg:3857')
        wgs84 = Proj(init='epsg:4326')

        center_tile_bbox = BBox(mercantile.bounds(*center_tile), projection=wgs84).project(mercator, edge_points=0)
        center_to_image = world_to_image(center_tile_bbox, TILE_SIZE)
        center_to_world = image_to_world(center_tile_bbox, TILE_SIZE)
        center_point_px = center_to_image(*mercantile.xy(*point))

        self.ul_tile = mercantile.tile(
            *transform(mercator, wgs84, *center_to_world(
                center_point_px[0] - math.ceil(IMAGE_SIZE[0] / 2),
                center_point_px[1] - math.ceil(IMAGE_SIZE[1] / 2)
            ), zoom))

        lr_tile = mercantile.Tile(
            x=min(2 ** zoom, self.ul_tile.x + self.num_tiles[0]),
            y=min(2 ** zoom, self.ul_tile.y + self.num_tiles[1]),
            z=zoom
        )

        ul = mercantile.xy(*mercantile.ul(*self.ul_tile))
        lr = mercantile.xy(*mercantile.ul(*lr_tile))

        self.image_bbox = BBox((ul[0], lr[1], lr[0], ul[1]))
        self.image_size = (TILE_SIZE[0] * self.num_tiles[0], TILE_SIZE[1] * self.num_tiles[1])

        self.to_image = world_to_image(self.image_bbox, self.image_size)
        self.to_world = image_to_world(self.image_bbox, self.image_size)

        self.point_px = [round(x) for x in self.to_image(*mercantile.xy(*point))]

        self.target_size = size
        self.point = point
        self.zoom = zoom
        self.basemap = basemap
        self._basemap_image = None
        self.opacity = opacity

    def _configure_event_loop(self):
        if sys.platform == 'win32':
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        else:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())

    def get_layer_images(self, service_url):
        async def fetch_tile(client, layer_url, tile, im):
            headers = {}
            layer_url = layer_url.format(x=tile.x, y=tile.y, z=tile.z, s='server')
            if layer_url.startswith('//'):
                layer_url = 'https:{}'.format(layer_url)
            elif layer_url.startswith('/'):
                layer_url = 'http://127.0.0.1:{}{}'.format(PORT, layer_url)
                if ALLOWED_HOSTS:
                    headers['Host'] = ALLOWED_HOSTS[0]

            async with client.get(layer_url, headers=headers) as r:
                tile_im = Image.open(BytesIO(await r.read()))
                im.paste(tile_im, ((tile.x - self.ul_tile.x) * 256, (tile.y - self.ul_tile.y) * 256))

        # Basemap caching to reduce requests
        basemap_cached = self._basemap_image is not None
        if basemap_cached:
            tile_layers = [service_url]
        else:
            tile_layers = [self.basemap, service_url]

        layer_images = [Image.new('RGBA', self.image_size) for _ in tile_layers]
        with aiohttp.ClientSession() as client:
            requests = []
            for i in range(int(self.num_tiles[0] * self.num_tiles[1])):
                tile = mercantile.Tile(
                    x=self.ul_tile.x + i % self.num_tiles[0],
                    y=self.ul_tile.y + i // self.num_tiles[0],
                    z=self.zoom
                )
                for j, layer_url in enumerate(tile_layers):
                    requests.append(fetch_tile(client, layer_url, tile, layer_images[j]))
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*requests))

        # If basemap is not cached, capture it
        if basemap_cached:
            layer_images.insert(0, self._basemap_image)
        else:
            self._basemap_image = layer_images[0]

        return layer_images

    def draw_geometry(self, im, geometry, color, width):
        canvas = ImageDraw.Draw(im)
        canvas.line(
            [tuple(round(x) for x in self.to_image(*mercantile.xy(*p))) for p in geometry], fill=color, width=width
        )

    def crop_image(self, im):
        im_ul = (self.point_px[0] - self.target_size[0] // 2, self.point_px[1] - self.target_size[1] // 2)
        box = (*im_ul, im_ul[0] + self.target_size[0], im_ul[1] + self.target_size[1])

        return im.crop(box), BBox(
            (self.to_world(box[0], box[3])) + self.to_world(box[2], box[1]), projection=Proj(init='epsg:3857')
        )

    def get_image(self, service_url) -> (Image, BBox):
        im = Image.new('RGBA', self.image_size)

        for i, layer_im in enumerate(self.get_layer_images(service_url)):
            im.paste(Image.blend(im, layer_im, 1 if i == 0 else self.opacity), (0, 0), layer_im)

        return self.crop_image(im)

    def get_polygon_image(self, polygons):
        im = Image.new('RGBA', self.image_size)

        if self._basemap_image is not None:
            im.paste(Image.blend(im, self._basemap_image, 1), (0, 0), self._basemap_image)

        for p in polygons:
            color = Color.from_hex(p['properties']['color']).to_tuple() if hasattr(p['properties'], 'color') else (0, 0, 255)
            self.draw_geometry(im, Geometry(str(p['geometry']))[0], color, 3)

        return self.crop_image(im)

    def get_legend(self, legend_url):
        async def fetch_legend(client, url):
            headers = {}
            if url.startswith('//'):
                url = 'https:{}'.format(url)
            elif url.startswith('/'):
                url = 'http://127.0.0.1:{}{}'.format(PORT, url)
                if ALLOWED_HOSTS:
                    headers['Host'] = ALLOWED_HOSTS[0]

            async with client.get(url, headers=headers) as r:
                return await r.read()

        with aiohttp.ClientSession() as client:
            task = asyncio.ensure_future(fetch_legend(client, legend_url))
            response = asyncio.gather(task)
            asyncio.get_event_loop().run_until_complete(task)

        return loads(response.result()[0].decode())
