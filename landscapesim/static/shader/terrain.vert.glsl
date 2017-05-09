// terrain.vert

// heightmap to get vertical amounts from
uniform sampler2D heightmap;
uniform float disp;

// texel varyings
varying float vAmount;
varying vec2 vUV;

// light uniforms
uniform vec3 lightPosition;

// light varyings
varying vec3 fN;
varying vec3 fE;
varying vec3 fL;

float decodeElevation(vec4 texture) {
    return (texture.r + texture.g * 255.0) * disp;
}

void main() 
{ 
    vUV = uv;
    vAmount = decodeElevation(texture2D(heightmap, uv));
    
    // use this for lighting based on sun location
    fN = normalize( vec4(normal, 0.0) ).xyz;
    fE = -(modelViewMatrix*vec4(position, 1.0)).xyz;
    fL = lightPosition;

        // set the position since we don't need to alter it
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);

}