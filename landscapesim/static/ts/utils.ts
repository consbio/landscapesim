// utils.ts

export function detectWebGL() {
	try {
		const canvas = document.createElement('canvas')
		return !!window['WebGLRenderingContext'] &&
			(!!canvas.getContext('webgl') || !!canvas.getContext('experimental-webgl'))
	}
	catch (e) {
		return null
	}
}