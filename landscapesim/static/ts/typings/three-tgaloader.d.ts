// TGALoader.d.ts
// Project: http://mrdoob.github.com/three.js/
// Definitions by: Taylor <https://github.com/TaylorMutch>
// Definitions: https://github.com/borisyankov/DefinitelyTyped

declare namespace THREE {
	class TGALoader {
		constructor(manager?: LoadingManager);

		manager: LoadingManager;
		crossOrigin: string;
		path: string;


		load(url: string, onload?: (texture: DataTexture) => void, onProgress?: (event: any) => void, onError?: (event: any) => void): DataTexture;
		setCrossOrigin(crossOrigin: string): void;
		setPath(path: string): void;
	}
}