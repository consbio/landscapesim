// Sets up a simple 3D viewer behind the map
var container = document.getElementById('scene');

var topographicBasemapUrl = L.esri.BasemapLayer.TILES.Imagery.urlTemplate.replace('{s}', 'services');
var heightDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
var normalDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/normal/{z}/{x}/{y}.png';

// Determine tiles from selected library configuration
var _e = library_config[1].extent;
var _bounds = [[_e[0][1], _e[0][0]],[_e[1][1], _e[1][0]]];
var _zoom = 11;
var tiles = xyz(_bounds, _zoom);

// tile constants
var tile_size = 256;

var _config = {
    'z': _zoom,
    'xmin': tiles[0].x - 1,
    'xmax': tiles[tiles.length-1].x + 1,
    'eymin': tiles[0].y - 1,
    'eymax': tiles[tiles.length-1].y + 1
};

var getTileUrl = function(template, z, x, y) {
    return template.replace('{z}', z).replace('{x}', x).replace('{y}', y)
};

var metersPerPixel = function(z) {
    return 6378137.0 * 2.0 * Math.PI / (tile_size * Math.pow(2, z));
};

// num tiles, width and height <--> x and y
// Increase the number of tiles to see more of the area
var x_tiles = _config['xmax'] - _config['xmin'] + 1;
var y_tiles = _config['eymax'] - _config['eymin'] + 1;

// world size
var w_width = tile_size * x_tiles;
var w_height = tile_size * y_tiles;

// scene graph, camera and builtin WebGL renderer
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1500 );

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
container.appendChild(renderer.domElement);

var controls = new THREE.OrbitControls(camera, container);
controls.maxDistance = 1000;
controls.minDistance = 10;
controls.maxPolarAngle = Math.PI / 2.1;

var loader = new THREE.TextureLoader();

// light uniform
var dynamicLightPosition = [1.0,0.0,1.0];

var vertexShader = ["attribute vec3 position;",
        "attribute vec2 uv;",
        "",
        "precision mediump float;",
        "precision mediump int;",
        "uniform mat4 modelViewMatrix; // optional",
        "uniform mat4 projectionMatrix; // optional",
        "uniform float zoom;",
        "",
        "uniform sampler2D heightMap;",
        "uniform sampler2D normalMap;",
        "uniform vec3 light;",
        //"uniform float disp;// displacement",
        "",
        "varying vec2 vUV;",
        "varying vec3 fN;",
        "varying vec3 fE;",
        "varying vec3 fL;",
        "",
        "float mpp()",
            "{return 6378137.0 * 2.0 * 3.141592653589793 / (256.0 * exp2(zoom));}",
        "",
        "float decodeHeight(vec4 texture)",
        "{",
        "   return (texture.r * 256.0 * 256.0 + texture.g * 256.0 + texture.b - 32768.0);",
        "}",
        "",
        "void main()",
        "{",
        "   vUV = uv;",
        "   float h = decodeHeight(texture2D(heightMap, uv)) / mpp();",
        "   fN = normalize(texture2D(normalMap, uv).xyz * 256.);",
        "   fE = -(modelViewMatrix * vec4(position, 1.0)).xyz;",
        "   fL = normalize(light);",
        "   gl_Position = projectionMatrix * modelViewMatrix * vec4(position.x, h, position.z, 1.0);",
        "}"].join('\n');
var fragmentShader= ["precision mediump float;",
        "precision mediump int;",
        "",
        "uniform sampler2D basemap;",
        "",
        "varying vec2 vUV;",
        "varying vec3 fN;",
        "varying vec3 fE;",
        "varying vec3 fL;",
        "",
        "vec4 not(vec4 a) {",
        "  return 1.0 - a;",
        "}",
        "",
        "void main()",
        "{",
        "// constant ambient, diffuse and specular and shiny values",
        "float KA = 0.5;",
        "float KD = 1.0;",
        "float KS = 0.15;",
        "float SHINY = 20.0;",
        "",
        "// sample the layer data",
        "vec4 baseColor = texture2D(basemap, vUV);",
        "",
        "// compute lighting per vertex",
        "vec3 N = normalize(fN);",
        "    vec3 E = normalize(fE);",
        "    vec3 L = normalize(fL);",
        "    vec3 H = normalize( L + E );",
        "    vec4 ambient = vec4(vec3(KA),1.0)*baseColor;",
        "    float diffDot = max(dot(L, N), 0.0);",
        "    vec4 diffuse = diffDot*vec4(vec3(KD),1.0)*baseColor;",
        "    float specDot = pow(max(dot(N, H), 0.0), SHINY);",
        "    vec4 specular = specDot*vec4(vec3(KS),1.0)*baseColor;",
        "",
        "    // zero the specular highlight if the light is behind the vertex being drawn",
        "    if( dot(L, N) < 0.0 ) {",
        "       specular = vec4(0.0, 0.0, 0.0, 1.0);",
        "    }",
        "",
        "    vec4 finalColor = ambient + diffuse + specular;",
        "    finalColor.a = 1.0;",
        "gl_FragColor = finalColor;",
        "}"].join('\n');

function addOneTile(x_offset, y_offset, base_texture, height_texture, normal_texture) {
	var geometry = new THREE.PlaneBufferGeometry(tile_size, tile_size, tile_size-1, tile_size-1);
	var material = new THREE.RawShaderMaterial(
	{
		uniforms: {
			'heightMap': {value: height_texture},
			'normalMap': {value: normal_texture},
			'basemap': {value: base_texture},
            'zoom': {value: _zoom},
			'light': {value: dynamicLightPosition}
		},
        vertexShader: vertexShader,
        fragmentShader: fragmentShader
	});

	geometry.rotateX(-Math.PI / 2);
	var tile = new THREE.Mesh( geometry, material );

	tile.translateOnAxis(new THREE.Vector3(1,0,0), x_offset);
	tile.translateOnAxis(new THREE.Vector3(0,0,1), y_offset);
    return tile;
}

// create one tile mesh
function createOneTile(x_idx,y_idx, x_offset, y_offset) {

    var z = _zoom;
    var x = _config.xmin + x_idx;
    var y = _config.eymin + y_idx;
    var heightTileUrl = getTileUrl(heightDataUrl, z, x, y);
    var normalTileUrl = getTileUrl(normalDataUrl, z, x, y);
    var baseTileUrl = getTileUrl(topographicBasemapUrl, z, x, y);

	loader.load(baseTileUrl, function(basemap) {
		loader.load(heightTileUrl, function(height) {
			loader.load(normalTileUrl, function(normals) {
                var tile = addOneTile(x_offset, y_offset, basemap, height, normals);
                tile.userData = {z: z, x: x, y: y};
                scene.add(tile)
				num_requests--;
				if (num_requests === 0) {
				    console.log(new Date().getTime() - start);
                }
            })
        })
    })
}

var local_x_offset = 0;
var local_y_offset = 0;

var start = new Date().getTime();
var num_requests = 0;

// add tiles in succession
for (var x = 0; x < x_tiles; x++) {
	local_y_offset = 0;
	for (var y = 0; y < y_tiles; y++) {
		num_requests++;
		createOneTile(x, y, local_x_offset, local_y_offset);
        local_y_offset += tile_size;
	}
	local_x_offset += tile_size;
}

// move the whole world to center the map
scene.translateOnAxis(new THREE.Vector3(1,0,0), - w_width / 2 + tile_size/2);
scene.translateOnAxis(new THREE.Vector3(0,0,1), - w_height / 3 * 2 + tile_size/2);

// move the camera
camera.position.y = 800;

var resize = function () {
    renderer.setSize( container.offsetWidth, container.offsetHeight );
    camera.aspect = container.offsetWidth / container.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
};

window.addEventListener('resize', resize, false);

var animate = function () {
	requestAnimationFrame( animate );
    controls.update();
	renderer.render(scene, camera);
};

animate();
