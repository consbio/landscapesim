// app.ts

import * as globals from './globals'
import {createTerrain, createDataTerrain} from './terrain'
import {createSpatialVegetation, VegetationGroups} from './veg'
import {detectWebGL} from './utils'
import {Loader, Assets, AssetList, AssetDescription, AssetRepo} from './assetloader'
import * as STSIM from './stsim'


export default function run(container_id: string) {

	if (!detectWebGL) {
		alert("Your browser does not support WebGL. Please use a different browser (I.e. Chrome, Firefox).")
		return null
	}

	let initialized = false
	let masterAssets = {} as AssetRepo

	// setup the THREE scene
	const container = document.getElementById(container_id)
	const scene = new THREE.Scene()
	const renderer = new THREE.WebGLRenderer({antialias: false})
	container.appendChild(renderer.domElement)
	const camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 2.0, 3000.0)
	
	// Camera controls
	const controls = new THREE.OrbitControls(camera, renderer.domElement)
	controls.enableKeys = false
	camera.position.y = 350
	camera.position.z = 600

	//const camera_start_position = camera.position.copy(new THREE.Vector3())
	const camera_start = new THREE.Vector3(camera.position.x, camera.position.y, camera.position.z)

	controls.maxPolarAngle = Math.PI / 2

	// Custom event handlers since we only want to render when something happens.
	renderer.domElement.addEventListener('mousedown', animate, false)
	renderer.domElement.addEventListener('mouseup', stopAnimate, false)
	renderer.domElement.addEventListener('mousewheel', render, false)
	renderer.domElement.addEventListener( 'MozMousePixelScroll', render, false ); // firefox

	initialize()

	// Load initial assets
	function initialize() {

		let terrainInitialized = false
		let vegetationInitialized = false
		function tryDone() {
			return terrainInitialized && vegetationInitialized
		}

		const terrainLoader = Loader()
		terrainLoader.load({
				text: [
					/* realism shaders */
					{name: 'terrain_vert', url: 'static/shader/terrain.vert.glsl'},
					{name: 'terrain_frag', url: 'static/shader/terrain.frag.glsl'},
					/* data shaders */
					{name: 'data_terrain_vert', url: 'static/shader/data_terrain.vert.glsl'},
					{name: 'data_terrain_frag', url: 'static/shader/data_terrain.frag.glsl'},
				],
				textures: [
					// terrain materials
					{name: 'terrain_dirt', url: 'static/img/terrain/dirt-512.jpg'},
					{name: 'terrain_grass', url: 'static/img/terrain/grass-512.jpg'},
					{name: 'terrain_snow', url: 'static/img/terrain/snow-512.jpg'},
					{name: 'terrain_sand', url: 'static/img/terrain/sand-512.jpg'},
					{name: 'terrain_water', url: 'static/img/terrain/water-512.jpg'},
		
				],
			},
			function(loadedAssets: Assets) {
				console.log('Terrain loaded')
				masterAssets['terrain'] = loadedAssets
				terrainInitialized = true
				initialized = tryDone()
			},
			reportProgress, reportError)

		const vegetationLoader = Loader()
		vegetationLoader.load(
			{
				text: [
					{name: 'real_veg_vert', url: 'static/shader/real_veg.vert.glsl'},
					{name: 'real_veg_frag', url: 'static/shader/real_veg.frag.glsl'},
					{name: 'data_veg_vert', url: 'static/shader/data_veg.vert.glsl'},
					{name: 'data_veg_frag', url: 'static/shader/data_veg.frag.glsl'},
				]
			},
			function(loadedAssets: Assets) {
				console.log('Vegetation shaders loaded')
				masterAssets['vegetation'] = loadedAssets
				vegetationInitialized = true
				initialized = tryDone()
			},
			reportProgress, reportError)
	}

	let currentDefinitions : STSIM.LibraryDefinitions
	let currentLibraryName = ""
	function setLibraryDefinitions(name:string, definitions: STSIM.LibraryDefinitions) {
		if (name != currentLibraryName) {
			currentLibraryName = name
			currentDefinitions = definitions
		}
	}

	let currentUUID : string
	let currentConditions : STSIM.LibraryInitConditions
	function setStudyArea(uuid : string, initialConditions: STSIM.LibraryInitConditions) {
		if (uuid != currentUUID) {
			currentUUID = uuid
			currentConditions = initialConditions
			camera.position.set(camera_start.x, camera_start.y, camera_start.z)

			// remove current terrain and vegetation cover
			if (scene.getObjectByName('terrain') != undefined) {
				scene.remove(scene.getObjectByName('data'))
				scene.remove(scene.getObjectByName('realism'))
				scene.remove(scene.getObjectByName('vegetation'))
				render()
			}

			const baseSourceURL = [currentLibraryName, 'select', currentUUID].join('/')
			const studyAreaLoader = Loader()
			let studyAreaAssets = {} as AssetList

			// Construct urls for vegetation geometry, textures based on asset names
			const assetNamesList = currentDefinitions.veg_model_config.visualization_asset_names
			let textures = [] as AssetDescription[]
			let geometries = [] as AssetDescription[]
			let assetName : string
			let assetPath : string
			textures.push({name: 'elevation', url: baseSourceURL + '/elev/'})
			textures.push({name: 'veg_tex', url: baseSourceURL + '/veg/'})
			textures.push({name: 'sc_tex', url: baseSourceURL + '/sc/'})

			for (var idx in assetNamesList) {
				assetName = assetNamesList[idx].asset_name
				assetPath = [currentLibraryName, assetName].join('/')
				geometries.push({
					name: assetName,
					url: 'static/json/geometry/' + assetPath + '.json'					
				})
				textures.push({
					name: assetName,
					url: 'static/img/' + assetPath + '.png'
				})
			}

			studyAreaAssets.textures = textures
			studyAreaAssets.geometries = geometries
			studyAreaLoader.load(studyAreaAssets, createScene, reportProgress, reportError)
		}
	}

	function createScene(loadedAssets: Assets) {
		masterAssets[currentLibraryName] = loadedAssets

		const heightmapTexture = loadedAssets.textures['elevation']
		const heights = computeHeights(heightmapTexture)
		const disp = 2.0 / 30.0

		const terrainAssets = masterAssets['terrain']
		const vegetationAssets = masterAssets['vegetation']

		// define the realism group
		let realismGroup = new THREE.Group()
		realismGroup.name = 'realism'
		const realismTerrain = createTerrain({
			dirt: terrainAssets.textures['terrain_dirt'],
			snow: terrainAssets.textures['terrain_snow'],
			grass: terrainAssets.textures['terrain_grass'],
			sand: terrainAssets.textures['terrain_sand'],
			water: terrainAssets.textures['terrain_water'],
			vertShader: terrainAssets.text['terrain_vert'],
			fragShader: terrainAssets.text['terrain_frag'],
			data: currentConditions.elev,
			heightmap: heightmapTexture,
			heights: heights,
			disp: disp
		})
		realismGroup.add(realismTerrain)
		
		// define the data group
		let dataGroup = new THREE.Group()
		dataGroup.name = 'data'
		dataGroup.visible = false	// initially set to false
		const dataTerrain = createDataTerrain({
			heightmap: heightmapTexture,
			heights: heights,
			stateclassTexture: loadedAssets.textures['sc_tex'],
			data: currentConditions.elev,
			vertShader: terrainAssets.text['data_terrain_vert'],
			fragShader: terrainAssets.text['data_terrain_frag'],
			disp: disp
		})
		dataGroup.add(dataTerrain)
		
		let vegAssetGroups = {} as STSIM.VizMapping
		let assetGroup : STSIM.VizAsset
		let i : number, j : number, breakout : boolean, name : string
			for (name in currentConditions.veg_sc_pct) {
				for (i = 0; i < currentDefinitions.veg_model_config.visualization_asset_names.length; i++) {
					assetGroup = currentDefinitions.veg_model_config.visualization_asset_names[i]
					breakout = false
					for (j = 0; j < assetGroup.valid_names.length; j++) {
						// is there a lookup in our definitions
						if (currentDefinitions.veg_model_config.lookup_field) {
							const lookupNames = currentDefinitions.veg_model_config.asset_map
							if (lookupNames[name] == assetGroup.valid_names[j]) {
								vegAssetGroups[name] = assetGroup
								breakout = true
								break;
							}
						// use the library names as is
						} else {
							if (name == assetGroup.valid_names[j]) {
								vegAssetGroups[name] = assetGroup
								breakout = true
								break;
							}	
						}
					}
					if (breakout) break;
				}
			}

			// create the vegetation
		const vegGroups = createSpatialVegetation({
			libraryName: currentLibraryName,
			zonalVegtypes: currentConditions.veg_sc_pct,
			veg_names: currentConditions.veg_names,
			vegAssetGroups : vegAssetGroups,
			vegtypes: currentDefinitions.vegtype_definitions,
			config: currentDefinitions.veg_model_config,
			strataTexture: loadedAssets.textures['veg_tex'],
			stateclassTexture: loadedAssets.textures['sc_tex'],
			heightmap: heightmapTexture,
			geometries: loadedAssets.geometries,
			textures: loadedAssets.textures,
			realismVertexShader: vegetationAssets.text['real_veg_vert'],
			realismFragmentShader: vegetationAssets.text['real_veg_frag'],
			dataVertexShader: vegetationAssets.text['data_veg_vert'],
			dataFragmentShader: vegetationAssets.text['data_veg_frag'],
			heightStats: currentConditions.elev,
			disp: disp
		}) as VegetationGroups
		//realismGroup.add(vegGroups.data)		
		//dataGroup.add(vegGroups.data)
		scene.add(vegGroups.data)
		scene.add(realismGroup)
		scene.add(dataGroup)
	
	
		// show the animation controls for the outputs
    	$('#animation_container').show();
	
		// activate the checkbox
		$('#viz_type').on('change', function() {
			if (dataGroup.visible) {
				dataGroup.visible = false
				realismGroup.visible = true
			} else {
				dataGroup.visible = true
				realismGroup.visible = false
			}
			render()
		})
				
		// render the scene once everything is finished being processed
		console.log('Vegetation Rendered!')
		render()
	}

	function collectSpatialOutputs(runControl: STSIM.RunControl) {

		if (!runControl.spatial) return
		console.log('Updating vegetation covers')
		
		const sid = runControl.result_scenario_id
		const srcSpatialTexturePath = runControl.library + '/outputs/' + sid

		let model_outputs : AssetDescription[] = new Array()
		for (var step = runControl.min_step; step <= runControl.max_step; step += runControl.step_size) {
			for (var it = 1; it <= runControl.iterations; it += 1) {
				
				model_outputs.push({name: String(it) + '_' + String(step), url: srcSpatialTexturePath + '/sc/' + it + '/' + step + '/'})
				if (step == runControl.min_step) break;	// Only need to get the initial timestep 1 time for all iterations			
			}
		}
		const outputsLoader = Loader()
		outputsLoader.load({
				textures: model_outputs,
			},
			function(loadedAssets: Assets) {
				console.log('Animation assets loaded!')
				
				masterAssets[String(sid)] = loadedAssets

				const dataGroup = scene.getObjectByName('data') as THREE.Group
				const realismGroup = scene.getObjectByName('realism') as THREE.Group
				dataGroup.visible = true
				realismGroup.visible = false
				render()

				// create an animation slider and update the stateclass texture to the last one in the timeseries, poc
				$('#viz_type').prop('checked', true)
				const animationSlider = $('#animation_slider')
				const currentIteration = 1								// TODO - show other iterations
				animationSlider.attr('max', runControl.max_step)
				animationSlider.attr('step', runControl.step_size)
				animationSlider.on('input', function() {
					const timestep = animationSlider.val()
					let timeTexture: THREE.Texture

					
					if (timestep == 0 || timestep == '0') {
						timeTexture = masterAssets[String(sid)].textures['1_0']
					}
					else {
						timeTexture = masterAssets[String(sid)].textures[String(currentIteration) + '_' + String(timestep)]
					}

					// update the dataGroup terrain and vegtypes
					//const dataGroup = scene.getObjectByName('data') as THREE.Group

					// TODO - do this change for each level of detail in the LOD

					let vegetation = scene.getObjectByName('vegetation')
					let childMaterial: THREE.RawShaderMaterial
					for (var i = 0; i < vegetation.children.length; i++) {
						const child = vegetation.children[i] as THREE.Mesh
						childMaterial = child.material as THREE.RawShaderMaterial
						childMaterial.uniforms.sc_tex.value = timeTexture
						childMaterial.needsUpdate = true
					}

					render()
					
				})
				
			},
			reportProgress,
			reportError
		)
		
	}

	function computeHeights(hmTexture: THREE.Texture ) { //, stats: STSIM.ElevationStatistics) {
		const image = hmTexture.image
		let w = image.naturalWidth
		let h = image.naturalHeight
		let canvas = document.createElement('canvas')
		canvas.width = w
		canvas.height = h
		let ctx = canvas.getContext('2d')
		ctx.drawImage(image, 0, 0, w, h)
		let data = ctx.getImageData(0, 0, w, h).data
		const heights = new Float32Array(w * h)
		let idx: number
		for (let y = 0; y < h; ++y) {
			for (let x = 0; x < w; ++x) {
				idx = (x + y * w) * 4
				heights[x + y * w] = (data[idx] | (data[idx+1] << 8) | (data[idx+2] << 16)) + data[idx+3] - 255  
			}
		}
		// Free the resources and return
		data = ctx = canvas = null
		return heights
	}

	function render() {
		renderer.render(scene, camera)
		controls.update()
	}

	let renderID: any

	function animate() {
		render()
		renderID = requestAnimationFrame(animate)
	}

	function stopAnimate() {
		cancelAnimationFrame(renderID)
	}

	function resize() {
		const newContainer = document.getElementById(container_id)
		renderer.setSize(newContainer.offsetWidth, newContainer.offsetHeight)
		camera.aspect = newContainer.offsetWidth / newContainer.offsetHeight
		camera.updateProjectionMatrix()
		render()
	}

	function isInitialized() {
		return initialized
	}

	return {
		isInitialized: isInitialized,
		resize: resize,
		scene: scene,
		camera: camera,
		setLibraryDefinitions: setLibraryDefinitions,
		setStudyArea: setStudyArea,
		libraryDefinitions: masterAssets[currentLibraryName],
		collectSpatialOutputs: collectSpatialOutputs,
	}
}

function reportProgress(progress: number) {
	console.log("Loading assets... " + progress * 100 + "%")
}

function reportError(error: string) {
	console.log(error)
	return
}

