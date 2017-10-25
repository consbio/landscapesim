import asyncio
import mercantile
import aiohttp
from PIL import Image, ImageMath, ImageDraw
from pyproj import Proj
from django.conf import settings
from clover.geometry.bbox import BBox


ALLOWED_HOSTS = getattr(settings, 'ALLOWED_HOSTS')
PORT = getattr(settings, 'PORT', 80)

TILE_SIZE = (256, 256)
IMAGE_SIZE = (645, 430)


class MapImage(object):
    def __init__(self, size, point, zoom, tile_layers, region, zone_id, opacity):
        self._configure_event_loop()

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
        self.tile_layers = tile_layers
        self.region = region
        self.zone_id = zone_id
        self.opacity = opacity

    def _configure_event_loop(self):
        if sys.platform == 'win32':
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        else:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())

    def get_layer_images(self):
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

        layer_images = [Image.new('RGBA', self.image_size) for _ in self.tile_layers]

        with aiohttp.ClientSession() as client:
            requests = []

            for i in range(self.num_tiles[0] * self.num_tiles[1]):
                tile = mercantile.Tile(
                    x=self.ul_tile.x + i % self.num_tiles[0],
                    y=self.ul_tile.y + i // self.num_tiles[0],
                    z=self.zoom
                )

                for j, layer_url in enumerate(self.tile_layers):
                    requests.append(fetch_tile(client, layer_url, tile, layer_images[j]))

            asyncio.get_event_loop().run_until_complete(asyncio.gather(*requests))

        return layer_images

    def draw_geometry(self, im, geometry, color, width):
        canvas = ImageDraw.Draw(im)

        canvas.line(
            [tuple(round(x) for x in self.to_image(*mercantile.xy(*p))) for p in geometry], fill=color, width=width
        )

    def draw_zone_geometry(self, im):
        if self.zone_id is not None:
            polygon = SeedZone.objects.get(pk=self.zone_id).polygon

            if polygon.geom_type == 'MultiPolygon':
                geometries = polygon.coords
            else:
                geometries = [polygon.coords]

            for geometry in geometries:
                self.draw_geometry(im, geometry[0], (0, 255, 0), 3)

    def draw_region_geometry(self, im):
        try:
            region = Region.objects.filter(name=self.region).get()
        except Region.DoesNotExist:
            return

        for geometry in region.polygons.coords:
            self.draw_geometry(im, geometry[0], (0, 0, 102), 1)

    '''
    def get_marker_image(self):
        leaflet_images_dir = os.path.join(BASE_DIR, 'seedsource', 'static', 'leaflet', 'images')
        marker = Image.open(os.path.join(leaflet_images_dir, 'marker-icon.png'))
        shadow = Image.open(os.path.join(leaflet_images_dir, 'marker-shadow.png'))

        # Raise the shadow opacity
        shadow.putalpha(ImageMath.eval('a * 2', a=shadow.convert('RGBA').split()[3]).convert('L'))

        im = Image.new('RGBA', self.image_size)
        im.paste(shadow, (self.point_px[0] - 12, self.point_px[1] - shadow.size[1]))

        marker_im = Image.new('RGBA', im.size)
        marker_im.paste(marker, (self.point_px[0] - marker.size[0] // 2, self.point_px[1] - marker.size[1]))
        im.paste(marker_im, (0, 0), marker_im)

        return im
    '''

    def crop_image(self, im):
        im_ul = (self.point_px[0] - self.target_size[0] // 2, self.point_px[1] - self.target_size[1] // 2)
        box = (*im_ul, im_ul[0] + self.target_size[0], im_ul[1] + self.target_size[1])

        return im.crop(box), BBox(
            (self.to_world(box[0], box[3])) + self.to_world(box[2], box[1]), projection=Proj(init='epsg:3857')
        )

    def get_image(self) -> (Image, BBox):
        im = Image.new('RGBA', self.image_size)

        for i, layer_im in enumerate(self.get_layer_images()):
            im.paste(Image.blend(im, layer_im, 1 if i == 0 else self.opacity), (0, 0), layer_im)

        #self.draw_zone_geometry(im)
        #self.draw_region_geometry(im)

        #marker_im = self.get_marker_image()
        im.paste(marker_im, (0, 0), marker_im)

        return self.crop_image(im)