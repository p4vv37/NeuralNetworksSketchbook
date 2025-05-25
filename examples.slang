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