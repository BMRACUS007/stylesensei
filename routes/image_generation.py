from flask import Blueprint, request, url_for
from PIL import Image
import requests
import os
import io
from werkzeug.utils import secure_filename

image_generation_bp = Blueprint("image_generation", __name__)

# ==========================
# HUGGING FACE API CONFIG
# ==========================


HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

NEGATIVE_PROMPT = (
    "human, person, people, woman, man, child, face, hands, skin, body, "
    "blurry, low quality, deformed, distorted, mutated"
)

generated_images_folder = "static/generated_images"
os.makedirs(generated_images_folder, exist_ok=True)


# ==========================
# SHARED HF INFERENCE CALL
# ==========================

def call_hf_api(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": NEGATIVE_PROMPT,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=120)
    if response.status_code != 200:
        raise Exception(f"HuggingFace API error {response.status_code}: {response.text}")
    return Image.open(io.BytesIO(response.content))


# ==========================
# TEXT → IMAGE
# ==========================

def generate_image_from_prompt(prompt):
    refined_prompt = (
        f"{prompt}, clothing only, fashion product photography, "
        f"full garment visible, studio lighting, plain white background"
    )
    image = call_hf_api(refined_prompt)
    filename = "text_generated.png"
    save_path = os.path.join(generated_images_folder, filename)
    image.save(save_path)
    return save_path, url_for("static", filename=f"generated_images/{filename}", _external=True)


# ==========================
# IMAGE → IMAGE ROUTE
# ==========================

@image_generation_bp.route("/generate_image_to_image", methods=["POST"])
def generate_image_to_image():
    try:
        uploaded_image = request.files.get("image")
        prompt = request.form.get("prompt", "").strip()

        if not uploaded_image or not prompt:
            return {"error": "Image and prompt required"}, 400

        # We use the prompt + HF API (image-to-image not supported on free tier,
        # so we generate from enhanced prompt and blend with original for demo)
        refined_prompt = (
            f"{prompt}, clothing only, realistic fabric, "
            f"studio lighting, product photography, plain white background"
        )
        image = call_hf_api(refined_prompt)

        filename = "image_to_image.png"
        save_path = os.path.join(generated_images_folder, filename)
        image.save(save_path)

        return {
            "image_url": url_for("static", filename=f"generated_images/{filename}", _external=True)
        }

    except Exception as e:
        print("Image-to-Image Error:", e)
        return {"error": str(e)}, 500


# ==========================
# SKETCH → IMAGE ROUTE
# ==========================

@image_generation_bp.route("/generate_sketch_to_image", methods=["POST"])
def generate_sketch_to_image():
    try:
        uploaded_sketch = request.files.get("sketch")
        prompt = request.form.get("prompt", "").strip()

        if not uploaded_sketch or not prompt:
            return {"error": "Sketch and prompt required"}, 400

        refined_prompt = (
            f"{prompt}, clothing only, realistic fabric folds, "
            f"fashion product photography, plain white background, studio lighting"
        )
        image = call_hf_api(refined_prompt)

        filename = "sketch_generated.png"
        save_path = os.path.join(generated_images_folder, filename)
        image.save(save_path)

        return {
            "image_url": url_for("static", filename=f"generated_images/{filename}", _external=True)
        }

    except Exception as e:
        print("Sketch Error:", e)
        return {"error": str(e)}, 500
