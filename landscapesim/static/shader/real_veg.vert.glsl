// spatial_veg.vert

//precision highp float;
// include PI and other nice things
#include <common>   


uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 normalMatrix;
uniform sampler2D heightmap;
uniform float disp;

attribute vec3 position;
attribute vec2 offset;
attribute vec2 hCoord;
attribute vec2 uv;
attribute float rotation;
attribute vec3 normal;

varying vec2 vUV;
varying vec2 scUV;    

// light uniforms
uniform vec3 lightPosition;

// light varyings
varying vec3 fN;
varying vec3 negfN;
varying vec3 fE;
varying vec3 fL;

float decodeElevation(vec4 texture) {
    return (texture.r + texture.g * 256.0) * disp * 255.0;
}

// Rotate by angle
vec2 rotate (float x, float y, float r) {
    float c = cos(r);
    float s = sin(r);
    return vec2(x * c - y * s, x * s + y * c);
}

void main() {
    vUV = uv;
    scUV = hCoord;
    float vAmount = decodeElevation(texture2D(heightmap, hCoord));
    vec3 newPosition = position;
    vec3 newNormal = normal;

    // rotate around the y axis
    newPosition.xz = rotate(newPosition.x, newPosition.z, PI * rotation);
    newNormal.xz = rotate(newNormal.x, newNormal.z, PI * rotation);
    
    // now translate to the offset position
    newPosition += vec3(offset.x, vAmount, offset.y);

    // implement phong lighting
    vec4 pos = vec4(newPosition,1.0);

    // use for light in eye position. This makes things stand out more when the user is looking directly at it.
    fN = normalize( modelViewMatrix*vec4(newNormal, 0.0) ).xyz;
    negfN = fN * -1.0;
    fE = -(modelViewMatrix*pos).xyz;
    fL = lightPosition - (modelViewMatrix*pos).xyz;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
}