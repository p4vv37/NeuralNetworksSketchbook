import bpy
import mathutils
import math
import random
import pathlib
import requests
import mathutils


# image = bpy.data.images.load( imgFile ) 
# np_array = np.asarray(image.pixels)

ROOT_DIR = r"/home/pawel/git/NeuralNetworksSketchbook/sd_texturing/tmp"
# PROMPT = "A wooden box, shadowless product lighting, flat white background"
PROMPT = "A wooden box"
N_PROMPT = "dark, shadows, bright spots"
OUTPUT_TEXTURE_PATH = pathlib.Path(ROOT_DIR) / "txt.png"
OUTPUT_UV_PATH = pathlib.Path(ROOT_DIR) / "uv0001.exr"
OUTPUT_DEPTH_PATH = pathlib.Path(ROOT_DIR) / "depth0001.bmp"
OUTPUT_DIFFUSE_PATH = pathlib.Path(ROOT_DIR) / "diffuse0001.bmp"
OUTPUT_RENDER_PATH = pathlib.Path(ROOT_DIR) / "Image0001.bmp"
OUTPUT_ALPHA_PATH = pathlib.Path(ROOT_DIR) / "alpha0001.png"
API_URL = "http://127.0.0.1:7000"
SEED = 1024


def setup():    
    if not pathlib.Path(ROOT_DIR).exists():
        pathlib.Path(ROOT_DIR).mkdir()
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    for node in tree.nodes:
        if node.label == "Output":
            node.base_path = str(pathlib.Path(ROOT_DIR))
     
    #output_image = None
    #for img in bpy.data.images:
    #    if img.filepath == str(OUTPUT_TEXTURE_PATH):
    #        output_image = img
    #        break
    #if output_image is None or not OUTPUT_TEXTURE_PATH.exists():
    #    output_image = bpy.data.images.new(str(OUTPUT_TEXTURE_PATH), width=512, height=512)
    output_image = bpy.data.images.new(str(OUTPUT_TEXTURE_PATH), width=512, height=512)
    
    output_image.file_format = 'PNG'
    output_image.filepath = str(OUTPUT_TEXTURE_PATH)
    output_image.save()
    
    material = bpy.data.materials["TargetMaterial"]
    for node in material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            node.image = output_image


def render_view(angle, z_offset=2, radius=10):
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
    #camera = bpy.data.objects['Camera']  # Make sure your first camera is named 'MainCamera'
    target_object = bpy.data.objects['Target']  # The camera will face this object. /!\ Naming

    z = target_object.location[2] + z_offset
    angle = 2 * math.pi * angle/360

    # Randomly place the camera on a circle around the object at the same height as the main camera
    new_camera_pos = mathutils.Vector((radius * math.cos(angle), radius * math.sin(angle), z))

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
    

def depth2img():
    data = {
        "prompt": PROMPT,
        "n_propmt": N_PROMPT,
        "depth": str(OUTPUT_DEPTH_PATH),
        "uv": str(OUTPUT_UV_PATH),
        "out_txt": str(OUTPUT_TEXTURE_PATH),
        "render": str(OUTPUT_RENDER_PATH),
        "alpha": str(OUTPUT_ALPHA_PATH),
        "diffuse": str(OUTPUT_DIFFUSE_PATH),
        "seed": SEED
    }
    response = requests.get(API_URL + "/depth2img_step", json=data)


def img2img(label):
    data = {
        "prompt": PROMPT,
        "n_propmt": N_PROMPT,
        "depth": str(OUTPUT_DEPTH_PATH),
        "uv": str(OUTPUT_UV_PATH),
        "out_txt": str(OUTPUT_TEXTURE_PATH),
        "render": str(OUTPUT_RENDER_PATH),
        "alpha": str(OUTPUT_ALPHA_PATH),
        "diffuse": str(OUTPUT_DIFFUSE_PATH),
        "seed": SEED
    }
    response = requests.get(API_URL + "/depth2img_step", json=data)

setup()

number_of_renders = 6
for num in range(number_of_renders):
    angle = 360*num/(number_of_renders + 1)
    render_view(angle)
    depth2img()
render_view(0, 6, 2)
depth2img()
print("end")
#render_view(90)mg2img(LABEL)
#render_view(180)
#img2img(LABEL)
#render_view(240)
#img2img(LABEL)