// terrain.frag

// our textures to blend
uniform sampler2D dirt;
uniform sampler2D snow;
uniform sampler2D grass;
uniform sampler2D sand;

// texel varyings
varying float vAmount;
varying vec2 vUV;

// light uniforms
uniform vec3 ambientProduct;
uniform vec3 diffuseProduct;
uniform vec3 specularProduct;
uniform float shininess;

// light varyings
varying vec3 fN;
varying vec3 fE;
varying vec3 fL;


void main() {

	vec4 sand = (smoothstep(-0.01, 0.02, vAmount) - smoothstep(0.03, 0.04, vAmount)) * texture2D(sand, vUV * 20.0);
	vec4 grassy = (smoothstep(-0.05, 0.14, vAmount) - smoothstep(0.15, 0.50, vAmount)) * texture2D( grass, vUV * 100.0 );
	vec4 dirty  = (smoothstep(0.20, 0.40, vAmount) - smoothstep(0.45, 0.95, vAmount)) * texture2D( dirt,  vUV * 80.0 );
	vec4 snowy  = (smoothstep(0.70, 0.85, vAmount))                                    * texture2D( snow,  vUV * 10.0 );
	vec4 myColor = vec4(0.0, 0.0, 0.0, 1.0) + sand + grassy + dirty + snowy;

	// compute lighting
	vec3 N = normalize(fN);
    vec3 E = normalize(fE);
    vec3 L = normalize(fL);

    vec3 H = normalize( L + E );

    vec4 ambient = vec4(ambientProduct,1.0)*myColor;

    float diffDot = max(dot(L, N), 0.0);
    vec4 diffuse = diffDot*vec4(diffuseProduct,1.0)*myColor;

    float specDot = pow(max(dot(N, H), 0.0), shininess);
    vec4 specular = specDot*vec4(specularProduct,1.0)*myColor;

    // discard the specular highlight if the light's behind the vertex
    if( dot(L, N) < 0.0 ) {
	   specular = vec4(0.0, 0.0, 0.0, 1.0);
    }

    vec4 finalColor = ambient + diffuse + specular;
    finalColor.a = 1.0;
	gl_FragColor = finalColor;
}