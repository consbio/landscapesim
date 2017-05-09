// data_veg.frag

precision highp float;

uniform sampler2D sc_tex;

varying vec2 scUV;

void main() {
    vec4 sc_color = texture2D(sc_tex, scUV);
    if (sc_color.rgb == vec3(0.)) discard;
    gl_FragColor = sc_color;
}