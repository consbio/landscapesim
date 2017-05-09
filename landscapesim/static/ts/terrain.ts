// terrain.ts

import {WHITE} from './globals'

/***** lighting uniforms for terrain - calculate only once for the whole app *****/
const AMBIENT = new THREE.Color(WHITE)
const DIFFUSE = new THREE.Color(WHITE)
const SPEC = new THREE.Color(WHITE)
const INTENSITY = 1.0
const KA = 0.2
const KD = 1.0
const KS = 0.15
const SHINY = 20.0
AMBIENT.multiplyScalar(KA * INTENSITY)
DIFFUSE.multiplyScalar(KD * INTENSITY)
SPEC.multiplyScalar(KS * INTENSITY)

const SUN = [1.0, 3.0, -1.0]	// light position for the terrain, i.e. the ball in the sky
								// shines from the top and slightly behind and west


interface TerrainParams {

	// heightmap
	heightmap: THREE.Texture
	heights: Float32Array
	disp: number

	// textures
	dirt: THREE.Texture
	snow: THREE.Texture
	grass: THREE.Texture
	sand: THREE.Texture
	water: THREE.Texture

	// shaders
	vertShader: string
	fragShader: string
	data: any

}

export function createTerrain(params: TerrainParams) {

	// data for landscape width/height
	const maxHeight = params.data.dem_max
	const width = params.data.dem_width
	const height = params.data.dem_height


	// make sure the textures repeat wrap
	params.heightmap.wrapS = params.heightmap.wrapT = THREE.RepeatWrapping
	params.dirt.wrapS = params.dirt.wrapT = THREE.RepeatWrapping
	params.grass.wrapS = params.grass.wrapT = THREE.RepeatWrapping
	params.snow.wrapS = params.snow.wrapT = THREE.RepeatWrapping
	params.sand.wrapS = params.sand.wrapT = THREE.RepeatWrapping
	params.water.wrapS = params.water.wrapT = THREE.RepeatWrapping

	const geo = new THREE.PlaneBufferGeometry(width, height, width-1, height-1)
	geo.rotateX(-Math.PI / 2)

	let vertices = geo.getAttribute('position')

	for (var i = 0; i < vertices.count; i++) {
		vertices.setY(i, params.heights[i] * params.disp)
	}

	geo.computeVertexNormals()

	const mat = new THREE.ShaderMaterial({
		uniforms: {
			// textures for color blending
			heightmap: {type: "t", value: params.heightmap},
			dirt: {type: "t", value: params.dirt},
			snow: {type: "t", value: params.snow},
			grass: {type: "t", value: params.grass},
			sand: {type: "t", value: params.sand},
			// lighting
			lightPosition: {type: "3f", value: SUN},
			ambientProduct: {type: "c", value: AMBIENT},
			diffuseProduct: {type: "c", value: DIFFUSE},
			specularProduct: {type: "c", value: SPEC},
			shininess: {type: "f", value: SHINY},
			// height exageration
			disp: {type: "f", value: params.disp}
			},
		vertexShader: params.vertShader,
		fragmentShader: params.fragShader
	})

	const mesh = new THREE.Mesh(geo, mat)
	mesh.name = 'terrain'

	// never reuse
	geo.dispose()
	mat.dispose()

	return mesh
}

interface DataTerrainParams {
	heightmap: THREE.Texture,
	heights: Float32Array,
	stateclassTexture: THREE.Texture,
	vertShader: string,
	fragShader: string,
	disp: number,
	data: any
}

export function createDataTerrain(params: DataTerrainParams) {

	const width = params.data.dem_width
	const height = params.data.dem_height

	const geo = new THREE.PlaneBufferGeometry(width, height, width-1, height-1)
	geo.rotateX(-Math.PI / 2)

	let vertices = geo.getAttribute('position')

	for (var i = 0; i < vertices.count; i++) {
		vertices.setY(i, params.heights[i] * params.disp)
	}

	geo.computeVertexNormals()

	const mat = new THREE.ShaderMaterial({
		uniforms: {
			// textures for color blending
			heightmap: {type: "t", value: params.heightmap},
			//tex: {type: "t", value: params.stateclassTexture},
			lightPosition: {type: "3f", value: SUN},
			ambientProduct: {type: "c", value: AMBIENT},
			diffuseProduct: {type: "c", value: DIFFUSE},
			specularProduct: {type: "c", value: SPEC},
			shininess: {type: "f", value: SHINY},
			},
		vertexShader: params.vertShader,
		fragmentShader: params.fragShader,
		side: THREE.DoubleSide
	})

	const mesh = new THREE.Mesh(geo, mat)
	mesh.name = 'terrain'

	// never reuse
	geo.dispose()
	mat.dispose()

	return mesh
}
