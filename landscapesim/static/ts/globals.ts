// globals.ts

// debugging constants

export const USE_RANDOM = true
//export const USE_RANDOM = false

// global constants configuration
export const MAX_INSTANCES = 5000		// max number of vertex instances we allow per vegtype
export const MAX_CLUSTERS_PER_VEG = 20	// maximum number of clusters to generate for each vegtype
export const RESOLUTION = 800.0			// resolution of terrain (in meters)
export const TERRAIN_DISP = 5.0 / RESOLUTION // the amount of displacement we impose to actually 'see' the terrain
export const MAX_CLUSTER_RADIUS = 30.0	// max radius to grow around a cluster

// global colors
export const WHITE = 'rgb(255,255,255)'

export function getVegetationLightPosition(vegname: string) : number[] {
	if (vegname.includes("Sagebrush")) {
		return [0.0, -5.0, 5.0]
	}
	return [0.0, 5.0, 0.0]
}
