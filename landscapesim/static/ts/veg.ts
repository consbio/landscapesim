// veg.ts
import * as globals from './globals'
import * as STSIM from './stsim'
import {GeometryAssets, TextureAssets} from './assetloader'

const RESOLUTION = 30	// 30 meter resolution

const AMBIENT = new THREE.Color(globals.WHITE)
const DIFFUSE = new THREE.Color(globals.WHITE)
const SPEC = new THREE.Color(globals.WHITE)
const INTENSITY = 1.0
const KA = 0.63
//const KA = 0.2
const KD = 1.0
const KS = 0.2
const SHINY = 20.0
AMBIENT.multiplyScalar(KA * INTENSITY)
DIFFUSE.multiplyScalar(KD * INTENSITY)
SPEC.multiplyScalar(KS * INTENSITY)

/*
	We should create two types of vegetation
	1) uses the standard 'realism' shaders that the non-spatial version uses, and
	2) one that uses the data-based shaders, to highlight the state class textures that are
	actually being shown, which dictate the change over time.
*/

export interface VegetationGroups {
	realism: THREE.Group
	data: THREE.Group
}

interface SpatialVegetationParams {
	libraryName: string
	zonalVegtypes: {[vegtype: string] : {[stateclass: string] : number}}
	veg_names: {[veg_name: string] : string}
	vegAssetGroups: STSIM.VizMapping
	vegtypes: STSIM.DefinitionMapping
	config: STSIM.VisualizationConfig
	strataTexture: THREE.Texture
	stateclassTexture: THREE.Texture
	heightmap: THREE.Texture
	geometries: GeometryAssets
	textures: TextureAssets
	realismVertexShader: string
	realismFragmentShader: string
	dataVertexShader: string
	dataFragmentShader: string
	heightStats: STSIM.ElevationStatistics
	disp: number,	// possibly unnecessary?
}

interface Vegtype3D {
	name: string
	heightmap: THREE.Texture
	sc_tex: THREE.Texture
	map: boolean[]
	numValid: number
	heightStats: STSIM.ElevationStatistics
	geo: THREE.InstancedBufferGeometry
	tex: THREE.Texture
	width: number
	height: number
	vertexShader: string
	fragmentShader: string
	disp: number
}


function decodeStrataImage(raw_data :Uint8ClampedArray) : Uint32Array {
	let decoded_data = new Uint32Array(raw_data.length / 4)
	let idx: number
	for (var i = 0; i < decoded_data.length; i++) {
		idx = i * 4
		decoded_data[i] = raw_data[idx] | (raw_data[idx+1] << 8) | (raw_data[idx+2] << 16) 
	}
	return decoded_data
}

// returns a THREE.Group of vegetation
export function createSpatialVegetation(params: SpatialVegetationParams) : VegetationGroups {
	console.log('Generating realistic vegetation...')

	let realismGroup = new THREE.Group()
	let dataGroup = new THREE.Group()
	dataGroup.name = realismGroup.name = 'vegetation'

	const strata_map = params.strataTexture
	const image = strata_map.image
	let w = image.naturalWidth
	let h = image.naturalHeight
	let canvas = document.createElement('canvas')
	canvas.width = w
	canvas.height = h
	let ctx = canvas.getContext('2d')
	ctx.drawImage(image, 0, 0, w, h)
	
	// get the image data and convert to IDs
	let raw_image_data = ctx.getImageData(0,0,w,h).data
	let strata_data = decodeStrataImage(raw_image_data)
	raw_image_data = null
	const strata_positions = computeStrataPositions(params.vegtypes, strata_data, w, h)

	for (var name in params.zonalVegtypes) {	

		const assetGroup = params.vegAssetGroups[name]
		const veg_geo = params.geometries[assetGroup.asset_name]
		const veg_tex = params.textures[assetGroup.asset_name]	
		const vegtypePositions = computeVegtypePositions(params.vegtypes[name], strata_positions, strata_data, w, h)
		const geometry = createVegtypeGeometry(veg_geo, vegtypePositions, w, h, assetGroup.symmetric, assetGroup.scale)
	
		realismGroup.add(createRealismVegtype({
			name: name,
			heightmap: params.heightmap,
			map: vegtypePositions.map, 
			numValid: vegtypePositions.numValid,
			heightStats: params.heightStats,
			geo: geometry,
			tex: veg_tex,
			sc_tex: params.stateclassTexture,
			width: w,
			height: h,
			vertexShader: params.realismVertexShader,
			fragmentShader: params.realismFragmentShader,
			disp: params.disp
		}))
		dataGroup.add(createDataVegtype({
			name: name,
			heightmap: params.heightmap,
			map: vegtypePositions.map,
			numValid: vegtypePositions.numValid,
			heightStats: params.heightStats,
			geo: geometry,
			tex: veg_tex,
			sc_tex: params.stateclassTexture,
			width: w,
			height: h,
			vertexShader: params.dataVertexShader,
			fragmentShader: params.dataFragmentShader,
			disp: params.disp
		}))
	}
	
	strata_data = ctx = canvas = null
	
	console.log('Vegetation generated!')
	return {realism: realismGroup, data: dataGroup}
}


function computeStrataPositions(vegtypes: any, data: Uint32Array, w: number, h: number) {
	let strata_map: boolean[] = new Array()		// declare boolean array
	let strata_data = data.slice()

	// convert to boolean and return the map
	for (var i = 0; i < strata_data.length; i++) {
		strata_map.push(strata_data[i] != 0 && i % Math.floor((Math.random()*75)) == 0? true: false)
	}
	return strata_map
}

interface VegtypeLocations {
	map: boolean[],
	numValid: number
}

function computeVegtypePositions(id: number, position_map: boolean[], type_data: Uint32Array, w:number, h:number) : VegtypeLocations {
	let vegtype_map: boolean[] = new Array()		// declare boolean array
	let idx : number
	let valid: boolean
	let numValid = 0
	for (let y = 0; y < h; ++y) {
		for (let x = 0; x < w; x++) {

			// idx in the image
			idx = (x + y * w)
			
			// update vegtype map
			valid = type_data[idx] == id && position_map[idx]

			// how many are valid? This informs the number of instances to do
			if (valid) numValid++

			vegtype_map.push(valid)
		}
	}

	return {map: vegtype_map, numValid: numValid}
}


function createRealismVegtype(params: Vegtype3D) {

	const lightPosition = globals.getVegetationLightPosition(name)
	const diffuseScale = DIFFUSE

	const mat = new THREE.RawShaderMaterial({
		uniforms: {
			heightmap: {type: "t", value: params.heightmap},
			disp: {type: "f", value: params.disp},
			tex: {type: "t", value: params.tex},
			sc_tex: {type: "t", value: params.sc_tex},
			// lighting
			lightPosition: {type: "3f", value: lightPosition},
			ambientProduct: {type: "c", value: AMBIENT},
			diffuseProduct: {type: "c", value: DIFFUSE},
			diffuseScale: {type: "f", value: diffuseScale},
			specularProduct: {type: "c", value: SPEC},
			shininess: {type: "f", value: SHINY}
		},
		vertexShader: params.vertexShader,
		fragmentShader: params.fragmentShader,
		side: THREE.DoubleSide
	})

	const mesh = new THREE.Mesh(params.geo, mat)
	mesh.name = name
	//mesh.frustumCulled = false
	return mesh
}

function createVegtypeGeometry(geo: THREE.Geometry, positions: VegtypeLocations,
	width: number, height: number, symmetric: boolean, scale: number) : THREE.InstancedBufferGeometry {

	const baseGeo = new THREE.BoxGeometry(1,1,1)
	baseGeo.translate(0, 0.5, 0)

	const inst_geo = new THREE.InstancedBufferGeometry()
	inst_geo.fromGeometry(baseGeo)
	baseGeo.dispose()

	// always remove the color buffer since we are using textures
	if ( inst_geo.attributes['color'] ) {
		inst_geo.removeAttribute('color')
	}		

	inst_geo.maxInstancedCount = positions.numValid

	const offsets = new THREE.InstancedBufferAttribute(new Float32Array(positions.numValid * 2), 2)
	const hCoords = new THREE.InstancedBufferAttribute(new Float32Array(positions.numValid * 2), 2)
	const rotations = new THREE.InstancedBufferAttribute(new Float32Array(positions.numValid), 1)

	inst_geo.addAttribute('offset', offsets)
	inst_geo.addAttribute('hCoord', hCoords)
	inst_geo.addAttribute('rotation', rotations)

	// generate offsets
	let i = 0
	let x: number, y:number, idx:number, posx: number, posy: number, tx:number, ty: number
	for (y = 0; y < height; y += 1) {
		for (x = 0; x < width; x += 1) {

			idx = (x + y * width)

			if (positions.map[idx]) {
				posx = (x - width/2)
				posy = (y - height/2)
				
				tx = x / width
				ty = y / height

				offsets.setXY(i, posx, posy)
				hCoords.setXY(i, tx, 1 - ty)
				rotations.setX(i, Math.random() * 2.0)
				i++;
			}
		}
	}

	return inst_geo
}


function createDataVegtype(params: Vegtype3D) {

	const mat = new THREE.RawShaderMaterial({
		uniforms: {
			heightmap: {type: "t", value: params.heightmap},
			disp: {type: "f", value: params.disp},
			sc_tex: {type:"t", value: params.sc_tex},
		},
		vertexShader: params.vertexShader,
		fragmentShader: params.fragmentShader,
		side: THREE.DoubleSide
	})

	const mesh = new THREE.Mesh(params.geo, mat)
	mesh.name = name
	mesh.frustumCulled = false
	return mesh
}
