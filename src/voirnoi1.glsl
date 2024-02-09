vec3 randColor(int number){
    return fract(sin(vec3(number+1)*vec3(12.8787, 1.97, 20.73739)));
}

float perlinNoise(vec2 P) {
    return fract(sin(dot(P ,vec2(12.9898,78.233))) * 43758.5453);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    vec3 col = vec3(0); 
    
    const int points_length = 100; 
    
    // Define the vectors for points_array
    vec2 points_array[points_length];
    
    // Introduce a factor to slow down the overall animation
    float animationFactor = 0.01;

    // Initialize points using Perlin noise
    for(int i = 0; i < points_length; i++){
        float x_freq = perlinNoise(vec2(float(i) * 0.1, 0.0)) * 10.0 * animationFactor + 1.0; // Frequency for x-axis
        float y_freq = perlinNoise(vec2(0.0, float(i) * 0.1)) * 10.0 * animationFactor + 1.0; // Frequency for y-axis
        float x = perlinNoise(vec2(float(i) * 0.1, 0.0)) * 0.9 + 0.05; // X position
        float y = perlinNoise(vec2(0.0, float(i) * 0.1)) * 0.9 + 0.05; // Y position
        x += sin(iTime * x_freq*0.01) * 0.1; // Add sine function to x
        y += sin(iTime * y_freq*0.5) * 0.1; // Add sine function to y
        points_array[i] = vec2(x, y);
    }
    
    float dmin = 1000.0; 
    int point = 0;
    
    // Pre-calculate rounded UV coordinates
    vec2 uv_rounded = floor(uv * 100.0) / 100.0;

    for(int i = 0; i < points_length; i++){
        vec2 point_rounded = floor(points_array[i] * 100.0) / 100.0;
        
        /*if(uv_rounded == point_rounded){
            col = vec3(1); 
        }*/
        if(length(points_array[i] - uv) < dmin){
            point = i; 
            dmin = length(points_array[i] - uv); 
        }
    }

    // Output to screen
    fragColor = vec4(randColor(point)-dmin+col, 1.0);
}
