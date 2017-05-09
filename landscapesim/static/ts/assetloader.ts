// Loader that provides a dictionary of named assets
// LICENSE: MIT
// Copyright (c) 2016 by Mike Linkovich;
// Adapted for use by Taylor Mutch, CBI

export interface TextureAssets {
	[id: string]: THREE.Texture
}

export interface GeometryAssets {
	[id: string]: THREE.Geometry
}

export interface Assets {
	images: {[id: string]: HTMLImageElement}
	text: {[id: string]: string}
	textures: TextureAssets
	geometries: GeometryAssets
	statistics: {[id: string]: any}
}

export interface AssetDescription {
	name: string
	url: string
}

export interface AssetList {
	images?: AssetDescription[]
	text?: AssetDescription[]
	textures?: AssetDescription[]
	geometries?: AssetDescription[]
	statistics?: AssetDescription[]
}

export interface AssetRepo {
	[name : string] : Assets
}

/**
 * Create a Loader instance
 */
export function Loader() {

	let isLoading = false
	let totalToLoad = 0
	let numLoaded = 0
	let numFailed = 0
	let success_cb : (a: Assets) => any
	let progress_cb : (p: number) => any
	let error_cb : (e: string) => any
	let done_cb : (ok: boolean) => any
	let assets: Assets = {images: {}, text: {}, textures: {}, geometries: {}, statistics: {}}

	/**
	 * Start loading a list of assets
	 */
	function load(
		assetList: AssetList,
		success?: (a: Assets) => any,
		progress?: (p: number) => any,
		error?: (e: string) => any,
		done?: (ok: boolean) => any
	) {
		success_cb = success
		progress_cb = progress
		error_cb = error
		done_cb = done
		totalToLoad = 0
		numLoaded = 0
		numFailed = 0
		isLoading = true

		if (assetList.text) {
			totalToLoad += assetList.text.length
			for (let i = 0; i < assetList.text.length; ++i)
				loadText(assetList.text[i])
		}
		if (assetList.images) {
			totalToLoad += assetList.images.length
			for (let i = 0; i < assetList.images.length; ++i)
				loadImage(assetList.images[i])
		}
		if (assetList.textures) {
			totalToLoad += assetList.textures.length
			for (let i = 0; i < assetList.textures.length; ++i)
				loadTexture(assetList.textures[i])
		}
		if (assetList.geometries) {
			totalToLoad += assetList.geometries.length
			for (let i = 0; i < assetList.geometries.length; ++i)
				loadGeometry(assetList.geometries[i])
		}
		if (assetList.statistics) {
			totalToLoad += assetList.statistics.length
			for (let i = 0; i < assetList.statistics.length; ++i)
				loadStatistics(assetList.statistics[i])

		}
	}

	function loadText (ad: AssetDescription) {
		console.log('loading '+ad.url)
		const req = new XMLHttpRequest()
		req.overrideMimeType('*/*')
		req.onreadystatechange = function() {
			if (req.readyState === 4) {
				if (req.status === 200) {
					assets.text[ad.name] = req.responseText
					doProgress()
				} else {
					doError("Error "+req.status+" loading "+ad.url)
				}
			}
		}
		req.open('GET', ad.url)
		req.send()
	}

	function loadImage (ad: AssetDescription) {
		const img = new Image()
		assets.images[ad.name] = img
		img.onload = doProgress
		img.onerror = doError
		img.src = ad.url
	}

	function loadTexture (ad: AssetDescription) {

		let parts = ad.url.split('.')
		let ext = parts[parts.length - 1]
		if (ext === 'tga') {
			assets.textures[ad.name] = new THREE.TGALoader().load(ad.url, doProgress)
		}
		else {
			assets.textures[ad.name] = new THREE.TextureLoader().load(ad.url, doProgress)
		}
	}

	function loadGeometry (ad: AssetDescription) {
		const jsonLoader = new THREE.JSONLoader()
		jsonLoader.load(ad.url, function(geometry, materials) {
				assets.geometries[ad.name] = geometry
				doProgress()
			},
			function(e) {},	// progress
			function(error) {
				doError("Error " + error + "loading " + ad.url)
			})	// failure
	}

	function loadStatistics (ad: AssetDescription) {
		if ($) {
			$.getJSON(ad.url)
				.done(function(response) {
				assets.statistics[ad.name] = response['data']
				doProgress()
			})
				.fail(function(jqhxr, textStatus, error) {
					doError('Error ' + error + "loading " + ad.url)
				})
		}
	}


	function doProgress() {
		numLoaded += 1
		if (progress_cb)
			progress_cb(numLoaded / totalToLoad)
		tryDone()
	}

	function doError (e: any) {
		if( error_cb )
			error_cb(e)
		numFailed += 1
		tryDone()
	}

	function tryDone() {
		if (!isLoading)
			return true
		if (numLoaded + numFailed >= totalToLoad) {
			const ok = !numFailed
			if (ok && success_cb)
				success_cb(assets)
			if (done_cb)
				done_cb(ok)
			isLoading = false
		}
		return !isLoading
	}

	/**
	 *  Public interface
	 */
	return {
		load: load,
		getAssets: () => assets
	}

} // end Loader
