import bpy
import mathutils
import math
import random
import pathlib
import requests
import mathutils
import shutil

FRAME_CODE = "{0:0>4}".format(bpy.context.scene.frame_current)
ROOT_DIR = r"/home/pawel/git/NeuralNetworksSketchbook/sd_texturing/tmp"
ROOT_PATH = pathlib.Path(ROOT_DIR)
PROMPT = "An oil painting of a pirate treasure chest, gold, coins, highly detailed, trending on artstation, concept art, Professional, gold coins on ground, wooden box with wooden cover"
N_PROMPT = "blue topping, dark, shadows, bright spots, glossy, only gold"
OUTPUT_TEXTURE_PATH = pathlib.Path(ROOT_DIR) / "txt.png"
OUTPUT_UV_PATH = pathlib.Path(ROOT_DIR) / F"uv{FRAME_CODE}.exr"
OUTPUT_DEPTH_PATH = pathlib.Path(ROOT_DIR) / F"depth{FRAME_CODE}.bmp"
OUTPUT_DIFFUSE_PATH = pathlib.Path(ROOT_DIR) / F"diffuse{FRAME_CODE}.bmp"
OUTPUT_RENDER_PATH = pathlib.Path(ROOT_DIR) / F"Image{FRAME_CODE}.png"
OUTPUT_ALPHA_PATH = pathlib.Path(ROOT_DIR) / F"alpha{FRAME_CODE}.png"
API_URL = "http://127.0.0.1:7000"
SEED = 2048


def setup():
    if not pathlib.Path(ROOT_DIR).exists():
        pathlib.Path(ROOT_DIR).mkdir()
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    for node in tree.nodes:
        if node.label == "Output":
            node.base_path = str(pathlib.Path(ROOT_DIR))

    output_image = bpy.data.images.new(str(OUTPUT_TEXTURE_PATH), width=768, height=768)

    output_image.file_format = 'PNG'
    output_image.filepath = str(OUTPUT_TEXTURE_PATH)
    output_image.save()

    material = bpy.data.materials["TargetMaterial"]
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            node.image = output_image


def copy_files_for_preview(idx):
    directory = ROOT_PATH / str(idx)
    directory.mkdir(parents=True, exist_ok=True)
    files = [f for f in ROOT_PATH.iterdir() if f.is_file()]
    for f in files:
        shutil.copyfile(ROOT_PATH / f.name, ROOT_PATH / str(idx) / f.name)


def render_view(angle, z_offset=2, radius=7):
    print(F"Rendering: {angle}")
    # Reload textures:
    for img in bpy.data.images:
        img.reload()

    # Basic parameters
    scene = bpy.data.scenes['Scene']
    render = scene.render

    # Resolution change 
    render.resolution_x = 768
    render.resolution_y = 512

    # Set camera position
    target_object = bpy.data.objects['Target']  # NAMING: Target == main object

    z = target_object.location[2] + z_offset
    angle_radians = 2 * math.pi * angle / 360

    # Randomly place the camera on a circle around the object at the same height as the main camera
    new_camera_pos = mathutils.Vector((radius * math.cos(angle_radians), radius * math.sin(angle_radians), z))

    bpy.ops.object.camera_add(enter_editmode=False, location=new_camera_pos)
    camera = bpy.context.object

    # Add a new track to constraint and set it to track your object
    track_to = bpy.context.object.constraints.new('TRACK_TO')
    track_to.target = target_object
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'

    # Render UVs and Depth
    bpy.context.scene.camera = camera
    bpy.ops.render.render()
    bpy.data.objects.remove(camera, do_unlink=True)


def generate_data():
    return {
        "prompt": PROMPT,
        "n_prompt": N_PROMPT,
        "depth": str(OUTPUT_DEPTH_PATH),
        "uv": str(OUTPUT_UV_PATH),
        "out_txt": str(OUTPUT_TEXTURE_PATH),
        "render": str(OUTPUT_RENDER_PATH),
        "alpha": str(OUTPUT_ALPHA_PATH),
        "diffuse": str(OUTPUT_DIFFUSE_PATH),
        "depth_based_mixing": 1,
        # "strength": 0.9,
        "seed": SEED
    }


def depth2img(**kwargs):
    data = generate_data()
    data.update(kwargs)
    response = requests.get(API_URL + "/depth2img_step", json=data)
    print(response.status_code, response.text)


def finish_texture():
    data = generate_data()
    response = requests.get(API_URL + "/finish_texture", json=data)
    print(response.status_code, response.text)


if __name__ == "__main__":
    setup()
    copy_files_for_preview(0)

    number_of_renders = 4
    for num in range(number_of_renders):
        angle = 360 * num / (number_of_renders) - 90
        render_view(angle)
        depth2img()
        copy_files_for_preview(num + 1)

    # top part problem
    render_view(-90, z_offset=3, radius=3)
    depth2img(strength=0.5)
    
    #number_of_renders = 4
    #for num in range(number_of_renders):
    #    angle = 360 * num / (number_of_renders ) + 45
    #    render_view(angle)
    #    depth2img(strength=0.5)
    #    copy_files_for_preview(num + 1 + 4)

    render_view(-90)
    depth2img(strength=0.5)
    
    #render_view(0, 6, 2)
    #depth2img(strength=0.5)
    finish_texture()
    render_view(0)
    copy_files_for_preview(number_of_renders + 2 + 4)
    print("end")
