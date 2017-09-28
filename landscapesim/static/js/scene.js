/* Sets up a simple 3D viewer behind the map */

var container = document.getElementById('scene');
var topographicBasemapUrl = L.esri.BasemapLayer.TILES.Imagery.urlTemplate.replace('{s}', 'services');
var heightDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
var normalDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/normal/{z}/{x}/{y}.png';
var blankDataUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEX///+nxBvIAAAAH0lEQVQYGe3BAQ0AAADCIPunfg43YAAAAAAAAAAA5wIhAAAB9aK9BAAAAABJRU5ErkJggg==";
var tileSize = 256;
var num_requests = 0;

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
var fragmentShader = ["precision mediump float;",
    "precision mediump int;",
    "",
    "uniform sampler2D baseMap;",
    "uniform sampler2D layerMap;",
    "uniform int hasLayerMap;",
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
    "vec4 baseColor = texture2D(baseMap, vUV);",
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

// scene graph, camera and builtin WebGL renderer
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1500);

var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

var controls = new THREE.OrbitControls(camera, container);
controls.maxDistance = 1000;
controls.minDistance = 10;
controls.maxPolarAngle = Math.PI / 2.1;

var loader = new THREE.TextureLoader();

var getTileUrl = function (template, z, x, y) {
    return template.replace('{z}', z).replace('{x}', x).replace('{y}', y)
};

// Calculate height to pixels. Here for reference, implemented internally in shader program
var metersPerPixel = function (z) {
    return 6378137.0 * 2.0 * Math.PI / (tileSize * Math.pow(2, z));
};

// light uniform
var dynamicLightPosition = [1.0, 0.0, 1.0];

// Retrieve a THREE.Mesh from the scene based on it's tile coordinates
function getChildByCoords(z, x, y) {
    for (var i = 0; i < scene.children.length; i++) {
        var child = scene.children[i];
        var data = child.userData;
        if (z === data.z && x === data.x && y === data.y) {
            return child;
        }
    }
    return null;
}

function addOneTile(z, x_offset, y_offset, base_texture, height_texture, normal_texture, layer_texture) {
    var geometry = new THREE.PlaneBufferGeometry(tileSize, tileSize, tileSize - 1, tileSize - 1);
    var material = new THREE.RawShaderMaterial(
        {
            uniforms: {
                'heightMap': {value: height_texture},
                'normalMap': {value: normal_texture},
                'baseMap': {value: base_texture},
                'layerMap': {value: layer_texture},
                'hasLayerMap': {value: false},
                'zoom': {value: z},
                'light': {value: dynamicLightPosition}
            },
            vertexShader: vertexShader,
            fragmentShader: fragmentShader
        });

    geometry.rotateX(-Math.PI / 2);
    var tile = new THREE.Mesh(geometry, material);

    tile.translateOnAxis(new THREE.Vector3(1, 0, 0), x_offset);
    tile.translateOnAxis(new THREE.Vector3(0, 0, 1), y_offset);
    return tile;
}

// create one tile mesh
function createOneTile(z, x, y, x_offset, y_offset) {
    var heightTileUrl = getTileUrl(heightDataUrl, z, x, y);
    var normalTileUrl = getTileUrl(normalDataUrl, z, x, y);
    var baseTileUrl = getTileUrl(topographicBasemapUrl, z, x, y);
    //var baseTileUrl = getTileUrl(currentLayerUrl, z, x, y);
    loader.load(blankDataUrl, function (layerMap) {
        loader.load(baseTileUrl, function (baseMap) {
            loader.load(heightTileUrl, function (heightMap) {
                loader.load(normalTileUrl, function (normalsMap) {
                    console.log(layerMap);
                    var tile = addOneTile(z, x_offset, y_offset, baseMap, heightMap, normalsMap, layerMap);
                    tile.userData = {z: z, x: x, y: y};
                    scene.add(tile);
                    num_requests--;
                    if (num_requests === 0) {
                        console.log('All terrains loaded');
                        canRenderLayer = true;
                        if (currentLayerUrl) {
                            //update3DLayer();
                        }
                    }
                })
            })
        })
    })
}

function updateOneTile(mesh, tile) {
    (function(thisMesh, t) {
        loader.load(getTileUrl(currentLayerUrl, t.z, t.x, t.z), function (layerMap) {
            thisMesh.material.uniforms.layerMap.value = layerMap;
            thisMesh.material.uniforms.layerMap.needsUpdate = true;
            thisMesh.material.needsUpdate = true;
        })
    }
    )(mesh, tile);
}

function update3DLayer() {
    var _e = library_config[1].extent;
    var _bounds = [[_e[0][1], _e[0][0]], [_e[1][1], _e[1][0]]];
    var _zoom = 12;
    var tiles = xyz(_bounds, _zoom);

    for (var i = 0; i < tiles.length; i++) {
        var t = tiles[i];
        var child = getChildByCoords(t.z, t.x, t.y);
        if (child) {
            updateOneTile(child, t);
        }
    }

}

var canRenderLayer = false;
var currentLayerUrl = "/maps/tiles/d64c21c6-31c1-43fb-8c6c-5ddfb3c49818/{z}/{x}/{y}.png";

function init3DScenario() {
    //scene.position.set(new THREE.Vector3(0, 0, 0));   // Reset scene position? New 'Scene'?

    // Determine tiles from selected library configuration
    var _e = library_config[1].extent;
    var _bounds = [[_e[0][1], _e[0][0]], [_e[1][1], _e[1][0]]];
    var _zoom = 12;
    var tiles = xyz(_bounds, _zoom);

    var z = _zoom;
    var xmin = tiles[0].x;
    var xmax =  tiles[tiles.length - 1].x;
    var ymin = tiles[0].y;
    var ymax = tiles[tiles.length - 1].y;

    // num tiles, width and height <--> x and y
    // Increase the number of tiles to see more of the area
    var numTilesX = xmax - xmin + 1;
    var numTilesY = ymax - ymin + 1;

    // world size
    var worldWidth = tileSize * numTilesX;
    var worldHeight = tileSize * numTilesY;

    var local_x_offset = 0;
    var local_y_offset = 0;

    // add tiles in succession
    for (var x = 0; x < numTilesX; x++) {
        local_y_offset = 0;
        for (var y = 0; y < numTilesY; y++) {
            num_requests++;
            createOneTile(z, xmin + x, ymin + y, local_x_offset, local_y_offset);
            local_y_offset += tileSize;
        }
        local_x_offset += tileSize;
    }

    // move the whole world to center the map
    scene.translateOnAxis(new THREE.Vector3(1, 0, 0), - worldWidth / 2 + tileSize / 2);
    scene.translateOnAxis(new THREE.Vector3(0, 0, 1), - worldHeight / 3 * 2 + tileSize / 2);

    // move the camera
    camera.position.y = 800;
}

var resize = function () {
    renderer.setSize( container.offsetWidth, container.offsetHeight );
    camera.aspect = container.offsetWidth / container.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
};

window.addEventListener('resize', resize, false);

var renderID;

var render = function() {
    controls.update();
	renderer.render(scene, camera);
};

var animate = function () {
    render();
    renderID = requestAnimationFrame( animate );
};

var cancelAnimate = function() {
    cancelAnimationFrame(renderID);
};
