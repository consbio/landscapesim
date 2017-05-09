// spatial_veg.frag

precision highp float;

uniform sampler2D tex;
uniform sampler2D sc_tex;

varying vec2 vUV;
varying vec2 scUV;

// light color uniforms
uniform vec3 ambientProduct;
uniform vec3 diffuseProduct;
uniform float diffuseScale;
uniform vec3 specularProduct;
uniform float shininess;

// light varyings
varying vec3 fN;
varying vec3 fE;
varying vec3 fL;
varying vec3 negfN;


void main() {

    vec4 myColor = texture2D(tex, vUV);
    vec4 sc_color = texture2D(sc_tex, scUV);

    if (myColor.a <= 0.3 || sc_color.rgb == vec3(0.)) {  // if alpha is 0, discard
    	discard;
    }
    else {
    	
        // compute lighting
        vec3 N = gl_FrontFacing ? normalize(fN) : normalize(negfN);
        //vec3 N = gl_Front
        vec3 E = normalize(fE);
        vec3 L = normalize(fL);
    
        vec3 H = normalize( L + E );
    
        vec4 ambient = vec4(ambientProduct, 1.0)*myColor;
    
        float diffDot = max(dot(L, N), diffuseScale);
        vec4 diffuse = diffDot*vec4(diffuseProduct, 1.0)*myColor;
    
        float specDot = pow(max(dot(N, H), 0.0), shininess);
        vec4 specular = specDot*vec4(specularProduct, 1.0)*myColor;
    
        // discard the specular highlight if the light's behind the vertex
        if( dot(L, N) < 0.0 ) {
           specular = vec4(0.0, 0.0, 0.0, 1.0);
        }
    
        vec4 finalColor = ambient + diffuse + specular;
        finalColor.a = 1.0;
        gl_FragColor = finalColor;
    }
}