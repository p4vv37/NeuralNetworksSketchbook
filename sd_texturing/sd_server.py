import pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import torch
from diffusers import StableDiffusionDepth2ImgPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image
import numpy as np
import cv2
import os


class Handler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.depth2img_pipe = StableDiffusionDepth2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-depth",
            torch_dtype=torch.float16,
        ).to("cuda")
        self.img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2",
            torch_dtype=torch.float16,
        ).to("cuda")

        super(Handler, self).__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):

        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length)
        data = json.loads(str(field_data, "UTF-8"))

        prompt = data.get("prompt")
        n_propmt = data.get("n_propmt", "")

        depth_path = data.get("depth")
        src_path = data.get("render")
        uv_path = data.get("uv")
        alpha_path = data.get("alpha")
        out_txt_path = data.get("out_txt")

        seed = data.get("seed", 1024)
        generator = torch.Generator(device="cuda").manual_seed(seed)

        if prompt is None or out_txt_path is None:
            self.send_response(400)
            self.send_header('Incorrect payload', 'text/html')
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('python 3 ', 'text/html')
        self.end_headers()
        if self.path == "/depth2img_step":
            init_img = Image.open(src_path)
            depth_img = Image.open(depth_path)
            img = self.depth2img_pipe(prompt=prompt, image=init_img, depth_map=depth_img, negative_prompt=n_propmt,
                                      guidance_scale=9, strength=1.0, generator=generator, num_inference_steps=50,
                                      num_images_per_prompt=1).images[0]
            img.save(pathlib.Path(src_path).parent / "prev.png")

            os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

            uv_img = cv2.imread(uv_path,
                                cv2.IMREAD_UNCHANGED)
            uv_img = cv2.cvtColor(uv_img, cv2.COLOR_BGR2RGB)
            out_img = Image.open(out_txt_path)
            alpha_img = Image.open(alpha_path)

            uv_img_arr = np.asarray(uv_img)
            img_arr = np.asarray(img)
            out_img_arr = np.array(out_img)
            src_alpha_arr = np.array(alpha_img)

            for x in range(uv_img_arr.shape[0]):
                for y in range(uv_img_arr.shape[1]):
                    u, v, w = uv_img_arr[x][y]
                    a = src_alpha_arr[x][y]
                    if a > 244 and sum([u, v, w]) > 0.00000001:
                        txt_u = int(out_img_arr.shape[1] * v) - 1
                        txt_v = int(out_img_arr.shape[0] - 1) - int(out_img_arr.shape[0] * u)
                        if sum(out_img_arr[txt_u, txt_v]) < 0.00001:
                            out_img_arr[txt_u, txt_v] = img_arr[x][y]

            print(out_img_arr.shape)
            out = Image.fromarray(out_img_arr.astype('uint8'), 'RGB')
            out.save(out_txt_path)

        if self.path == "/img2img_step":
            pass

        message = "Python 3 html server"
        print(message)
        self.wfile.write(bytes(message, "utf8"))


with HTTPServer(('', 7000), Handler) as server:
    server.serve_forever()
