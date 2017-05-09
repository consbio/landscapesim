// data_terrain.vert

uniform sampler2D heightmap;

// light uniforms
uniform vec3 lightPosition;

// light varyings
varying vec3 fN;
varying vec3 fE;
varying vec3 fL;

varying vec2 vUV;
varying float vAmount;

float decodeElevation(vec4 texture) {
    return (texture.r * 256.0 + texture.g * 256.0 * 256.0) / (5000.0);
}

void main() 
{ 
    vUV = uv;
    vAmount = decodeElevation(texture2D(heightmap, uv));
    
        // use this for lighting based on sun location
    fN = normalize( vec4(normal, 0.0) ).xyz;
    fE = -(modelViewMatrix*vec4(position, 1.0)).xyz;
    fL = lightPosition;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
