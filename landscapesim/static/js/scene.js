/* Sets up a simple 3D viewer behind the map */
var container = document.getElementById('scene');
var topographicBasemapUrl = L.esri.BasemapLayer.TILES.Imagery.urlTemplate.replace('{s}', 'services');
var heightDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
var normalDataUrl = 'https://s3.amazonaws.com/elevation-tiles-prod/normal/{z}/{x}/{y}.png';
var blankDataUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEX///+nxBvIAAAAH0lEQVQYGe3BAQ0AAADCIPunfg43YAAAAAAAAAAA5wIhAAAB9aK9BAAAAABJRU5ErkJggg==";
var tileSize = 128;
var numRequests = 0;
var vertexShader = [
    "attribute vec3 position;",
    "attribute vec2 uv;",
    "",
    "precision mediump float;",
    "precision mediump int;",
    "uniform mat4 modelViewMatrix; // optional",
    "uniform mat4 projectionMatrix; // optional",
    "",
    "uniform sampler2D heightMap;",
    "uniform sampler2D normalMap;",
    "uniform vec3 light;",
    "uniform float metersPerPx;",
    "",
    "varying vec2 vUV;",
    "varying vec3 fN;",
    "varying vec3 fE;",
    "varying vec3 fL;",
    "",
    "float decodeHeight(vec4 texture)",
    "{",
    "   return (texture.r * 256.0 * 256.0 + texture.g * 256.0 + texture.b - 32768.0) / metersPerPx;",
    "}",
    "",
    "void main()",
    "{",
    "   vUV = uv;",
    "   float h = decodeHeight(texture2D(heightMap, uv));",
    "   fN = normalize(texture2D(normalMap, uv).xyz * 256.);",
    "   fE = -(modelViewMatrix * vec4(position, 1.0)).xyz;",
    "   fL = normalize(light);",
    "   gl_Position = projectionMatrix * modelViewMatrix * vec4(position.x, h, position.z, 1.0);",
    "}"].join('\n');
var fragmentShader = [
    "precision mediump float;",
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
    //"// constant ambient, diffuse and specular and shiny values",
    "   float KA = 0.5;",
    "   float KD = 1.0;",
    "   float KS = 0.15;",
    "   float SHINY = 20.0;",
    "",
    //"// sample the layer data",
    "   vec4 baseColor = texture2D(baseMap, vUV);",
    "   vec4 layerColor = texture2D(layerMap, vUV);",
    "",
    //"// compute lighting per vertex",
    "    vec3 N = normalize(fN);",
    "    vec3 E = normalize(fE);",
    "    vec3 L = normalize(fL);",
    "    vec3 H = normalize( L + E );",
    "    vec4 ambient = vec4(vec3(KA),1.0)*baseColor;",
    "    float diffDot = max(dot(L, N), 0.0);",
    "    vec4 diffuse = diffDot*vec4(vec3(KD),1.0)*baseColor;",
    "    float specDot = pow(max(dot(N, H), 0.0), SHINY);",
    "    vec4 specular = specDot*vec4(vec3(KS),1.0)*baseColor;",
    "",
    //"    // zero the specular highlight if the light is behind the vertex being drawn",
    "    if( dot(L, N) < 0.0 ) {",
    "       specular = vec4(0.0, 0.0, 0.0, 1.0);",
    "    }",
    "",
    "    vec4 finalColor = ambient + diffuse + specular;",
    "    finalColor.a = 1.0;",
    "    if (hasLayerMap > 0 && layerColor.a > 0.5) {",
    "        finalColor.xyz = mix(layerColor.xyz, finalColor.xyz, 0.5);",
    "    }",
    "    gl_FragColor = finalColor;",
    "}"].join('\n');

// scene graph, camera and builtin WebGL renderer
var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(65, container.offsetWidth / container.offsetHeight, 0.1, 1500);

var renderer = new THREE.WebGLRenderer();
renderer.setSize(container.offsetWidth, container.offsetHeight);
container.appendChild(renderer.domElement);

var controls = new THREE.OrbitControls(camera, container);
controls.maxDistance = 1000;
controls.minDistance = 10;
controls.maxPolarAngle = Math.PI / 2.1;

var loader = new THREE.TextureLoader();

var getTileUrl = function (template, z, x, y) {
    return template.replace('{z}', z).replace('{x}', x).replace('{y}', y)
};

// Calculate height to pixels
var metersPerPixel = function (z, lat) {
    return Math.cos(lat) * 6378137.0 * 2.0 * Math.PI / (tileSize * Math.pow(2, z));
};

// light uniform
var dynamicLightPosition = [1.0, 0.0, 1.0];

/* One-time initialization of geometry, significantly reduces memory usage. */
var planeGeometry = new THREE.PlaneBufferGeometry(tileSize, tileSize, tileSize - 1, tileSize - 1);
planeGeometry.rotateX(-Math.PI / 2);

function addOneTile(z, latitude, x_offset, y_offset, base_texture, height_texture, normal_texture, layer_texture) {
    var material = new THREE.RawShaderMaterial(
        {
            uniforms: {
                'heightMap': {value: height_texture},
                'normalMap': {value: normal_texture},
                'baseMap': {value: base_texture},
                'layerMap': {value: layer_texture},
                'hasLayerMap': {value: false},
                'metersPerPx': {value: metersPerPixel(z, latitude)},
                'light': {value: dynamicLightPosition}
            },
            vertexShader: vertexShader,
            fragmentShader: fragmentShader
        });
    var tile = new THREE.Mesh(planeGeometry, material);
    tile.translateOnAxis(new THREE.Vector3(1, 0, 0), x_offset);
    tile.translateOnAxis(new THREE.Vector3(0, 0, 1), y_offset);
    return tile;
}

/* Create one tile mesh */
function createOneTile(z, x, y, latitude, x_offset, y_offset) {
    var heightTileUrl = getTileUrl(heightDataUrl, z, x, y);
    var normalTileUrl = getTileUrl(normalDataUrl, z, x, y);
    var baseTileUrl = getTileUrl(topographicBasemapUrl, z, x, y);
    loader.load(blankDataUrl, function (layerMap) {
        loader.load(baseTileUrl, function (baseMap) {
            loader.load(heightTileUrl, function (heightMap) {
                loader.load(normalTileUrl, function (normalsMap) {
                    var tile = addOneTile(z, latitude, x_offset, y_offset, baseMap, heightMap, normalsMap, layerMap);
                    tile.userData = {z: z, x: x, y: y};
                    scene.add(tile);
                    numRequests--;
                    if (numRequests === 0) {
                        console.log('All terrains loaded');
                        canRender3DLayer = true;
                        if (currentLayerUrl) {
                            update3DLayer(currentLayerUrl);
                        }
                    }
                })
            })
        })
    })
}

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

function updateOneTile(t) {
    loader.load(getTileUrl(currentLayerUrl, t.z, t.x, t.y), function (layerMap) {
        var mesh = getChildByCoords(t.z, t.x, t.y);
        mesh.material.uniforms.layerMap.value = layerMap;
        mesh.material.uniforms.hasLayerMap.value = true;
        mesh.material.needsUpdate = true;
    })
}

function updateSceneTiles() {
    var tiles = sceneConfig().tiles;
    for (var i = 0; i < tiles.length; i++) {
        var t = tiles[i];
        updateOneTile(t);
    }
    sceneNeedsUpdate = false;
}

function sceneConfig() {
    var libInfo = store[$(".model_selection").val()];
    var e = libInfo.extent;
    var bounds = [[e[0][1], e[0][0]], [e[1][1], e[1][0]]];
    var zoom = libInfo.zoom;
    return {tiles: xyz(bounds, zoom), zoom: zoom, lat: e[1][0]};
}

var sceneEnabled = function() { return $('#scene-switch')[0].checked; }

var sceneNeedsUpdate = false;
function update3DLayer(layerUrl) {
    currentLayerUrl = layerUrl;
    sceneNeedsUpdate = true;
}

var canRender3DLayer = false;
var currentLayerUrl = null;

function init3DScenario(initialLayerUrl) {
    resetScene();
    controls.reset();
    scene.position.set(0, 0, 0);

    if (initialLayerUrl) {
        currentLayerUrl = initialLayerUrl;
    }

    // Determine tiles from selected library configuration
    var config = sceneConfig();
    var tiles = config.tiles;
    var z = config.zoom;

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

    var localXOffset = 0;
    var localYOffset = 0;

    // add tiles in succession
    for (var x = 0; x < numTilesX; x++) {
        localYOffset = 0;
        for (var y = 0; y < numTilesY; y++) {
            numRequests++;
            createOneTile(z, xmin + x, ymin + y, config.lat, localXOffset, localYOffset);
            localYOffset += tileSize;
        }
        localXOffset += tileSize;
    }

    // move the whole world to center the map
    scene.translateOnAxis(new THREE.Vector3(1, 0, 0), - worldWidth / 2 + tileSize / 2);
    scene.translateOnAxis(new THREE.Vector3(0, 0, 1), - worldHeight / 2 + tileSize / 2);

    // Reset camera position
    camera.position.set(0, 800, 0);
    controls.saveState();
}

/* Clears the scene and disposes of memory allocated to WebGL */
var resetScene = function() {
    for (var i = scene.children.length - 1; i >= 0; i--) {
        var child = scene.children[i];
        scene.remove(child);

        // Dispose of the textures
        child.material.uniforms.layerMap.value.dispose();
        child.material.uniforms.baseMap.value.dispose();
        child.material.uniforms.heightMap.value.dispose();
        child.material.uniforms.normalMap.value.dispose();

        // Dispose of the uniforms
        child.material.dispose();
    }
    canRender3DLayer = false;
};

var resize = function () {
    renderer.setSize( container.offsetWidth, container.offsetHeight );
    camera.aspect = container.offsetWidth / container.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
};

var renderID;

var render = function() {
    controls.update();
	renderer.render(scene, camera);
};

var animate = function () {
    render();
    if (sceneNeedsUpdate) updateSceneTiles();
    renderID = requestAnimationFrame( animate );
};

var cancelAnimate = function() {
    cancelAnimationFrame(renderID);
};
