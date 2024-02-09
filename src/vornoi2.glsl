// Perlin noise function for displacement and frequency variation
float perlinNoise(vec2 P) {
    return fract(sin(dot(P, vec2(12.9898, 78.233))) * 43758.5453);
}

vec3 RGBToVec3Color(vec3 rgb) {
    return rgb / 255.0;
}

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

// Function to convert from HSV to RGB
vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

// Updated function to get the nth harmonious color given an original HSV color and the total number of colors
// Assumes hue in hsv_org.x is in the range [0, 1]
vec3 GetHarmoniousColor(vec3 hsv_org, int totalColors, int colorIndex) {
    float angleStep = 1.0 / float(totalColors); // Fraction of the full hue circle
    float newHue = mod(hsv_org.x + angleStep * float(colorIndex), 1.0); // Wrap hue within [0, 1]
    vec3 hsv_new = vec3(newHue, hsv_org.y, hsv_org.z);
    return hsv2rgb(hsv_new); // Convert the new HSV color back to RGB
}



// Function to determine cell color based on its grid position
vec3 getColor(int i, int j) {
    // Example starting with an RGB color and converting to HSV
    vec3 start_color_rgb = vec3(250, 170, 133); // Example RGB color
    vec3 start_color = rgb2hsv(RGBToVec3Color(start_color_rgb)); // Convert to HSV
    
    int n = 4; // Total number of colors
    int idx = (i * 2 + j * 3) % 4; // Use a more complex pattern to determine color
    if (idx == 0) return GetHarmoniousColor(start_color,n,0); // Red
    if (idx == 1) return GetHarmoniousColor(start_color,n,1);
    if (idx == 2) return GetHarmoniousColor(start_color,n,2);
    return GetHarmoniousColor(start_color,n,3);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;

    const int n = 10; // Grid width
    const int m = 10; // Grid height
    vec2 gridSize = vec2(1.0 / float(n), 1.0 / float(m));

    float closestDist = 10000.0;
    vec3 col = vec3(0);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            // Initial grid position
            vec2 gridPos = (vec2(float(i), float(j)) + 0.5) * gridSize;



            float dmin = 1000.0; 
            
            float movement_speed = 0.1;
            float sin_movement_ampl = 1.0;
            const float noiseStrength = 0.99; // If you want a fixed value inside the shader
            
            
            vec2 noiseOffset = perlinNoise(gridPos * 25.0) * noiseStrength * gridSize; // Adjusted displacement
            


            // Unique sine frequencies for each cell based on its index and perlin noise
            float sinFreqX = perlinNoise(vec2(float(i), float(j)) * 0.1) * movement_speed;
            float sinFreqY = perlinNoise(vec2(float(j), float(i)) * 0.1) * movement_speed;
            vec2 sinOffset = vec2(sin(iTime * sinFreqX + float(i)) * sin_movement_ampl, sin(iTime * sinFreqY + float(j)) * sin_movement_ampl); // Varied movement

            // Dynamic position considering both noise displacement and sine movement
            vec2 dynamicPos = gridPos + noiseOffset + sinOffset;

            // Calculate distance to this cell's dynamically adjusted center
            float dist = distance(uv, dynamicPos);
            


            if(length(dynamicPos - uv) < dmin){
               dmin = length(dynamicPos - uv); 
            }
            

            if (dist < closestDist) {
                closestDist = dist;
                col = getColor(i, j)-dmin; // Determine color based on adjusted grid position
            }
        }
    }

    fragColor = vec4(col, 1.0);
}