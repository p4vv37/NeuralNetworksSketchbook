[Differentiable]
float4 brightness(float4 ammount, float4 pixel)
{
    pixel.rgb += ammount.rgb;
    pixel.a = 1.0;
    return pixel;
}

float4 brightness_inplace(float4 ammount, inout float4 pixel)
{
    pixel.rgb += ammount.rgb;
    pixel.a = 1.0;
    return pixel;
}
