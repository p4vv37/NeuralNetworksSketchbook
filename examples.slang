[Differentiable]
float3 brightness(float3 ammount, float3 pixel)
{
    pixel += ammount;
    return pixel;
}

float3 brightness_inplace(float3 ammount, inout float3 pixel)
{
    pixel += ammount;
    return pixel;
}

[Differentiable]
float4 rainbow(float2 p, float y)
{
    if (y < 0.1) return float4(1,1,1,1);
    float intensity = saturate((y - 0.1) / 0.9);

    float rnd = frac(sin(dot(p, float2(12.9898,78.233))) * 43758.5453);
    float2 w = p + (rnd - 0.5) * 0.03 * intensity;

    float swirl = sin(w.y * 10.0 + w.x * 5.0) * 0.4 * intensity;
    float angle = atan2(w.y - 0.5, w.x - 0.5) + swirl;
    float dist  = length(w - 0.5) * 2.0;

    float hue = angle/6.28318 + 0.5
              + dist * 0.6
              + p.x * 1.5
              + p.y * 0.5
              + (rnd - 0.5) * 0.1;

    float3 color;
    color.r = abs(frac(hue + 1.0) * 6.0 - 3.0) - 1.0;
    color.g = abs(frac(hue + 2.0/3.0) * 6.0 - 3.0) - 1.0;
    color.b = abs(frac(hue + 1.0/3.0) * 6.0 - 3.0) - 1.0;
    color = saturate(color);

    float glow = pow(intensity, 2.0) * 0.7;
    color = lerp(float3(1.0), color + glow, intensity);

    color += smoothstep(0.8, 0.5, dist) * intensity * 0.4;
    color += sin(p.x * 50.0 + p.y * 30.0) * 0.1 * intensity;
    color += cos((p.y - p.x) * 40.0)    * 0.05 * sqrt(intensity);

    float dark = lerp(1.0, 0.6, intensity);
    color *= dark;

    return float4(color, 1.0);
}
