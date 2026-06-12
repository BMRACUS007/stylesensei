from flask import Blueprint, request, url_for, jsonify
import os
import random
from PIL import Image
import os
import uuid
image_generation_bp = Blueprint("image_generation", __name__)

# ==========================
# LOCAL IMAGE CONFIG
# ==========================

generated_images_folder = "static/generated_images"
dress_folder = os.path.join("static", "dresses")

os.makedirs(generated_images_folder, exist_ok=True)

# Supported colors
colors = ["red", "blue", "black", "white", "green", "yellow", "pink"]


# ==========================
# TEXT → IMAGE (LOCAL FALLBACK SYSTEM)
# ==========================

@image_generation_bp.route("/generate_text_to_image", methods=["POST"])
def generate_text_to_image():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request"}), 400

        prompt = data.get("prompt", "").lower().strip()

        if not prompt:
            return jsonify({"error": "Prompt required"}), 400

        # -------------------------
        # 1. Detect color
        # -------------------------
        detected_color = None
        for color in colors:
            if color in prompt:
                detected_color = color
                break

        if not detected_color:
            return jsonify({
                "error": "No color detected. Try: red dress, blue dress, etc."
            }), 400

        # -------------------------
        # 2. Get folder
        # -------------------------
        folder_path = os.path.join(dress_folder, detected_color)

        if not os.path.exists(folder_path):
            return jsonify({"error": f"No folder for {detected_color}"}), 404

        images = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not images:
            return jsonify({"error": f"No images in {detected_color} folder"}), 404

        # -------------------------
        # 3. Random selection
        # -------------------------
        selected_image = random.choice(images)

        image_url = url_for(
            "static",
            filename=f"dresses/{detected_color}/{selected_image}",
            _external=True
        )

        return jsonify({
            "image_url": image_url,
            "mode": "local_template",
            "color_detected": detected_color
        })

    except Exception as e:
        print("Text-to-Image Error:", e)
        return jsonify({"error": str(e)}), 500


# ==========================
# IMAGE → IMAGE (OPTIONAL PLACEHOLDER)
# ==========================
@image_generation_bp.route("/generate_image_to_image", methods=["POST"])
def generate_image_to_image():
    try:
        uploaded_image = request.files.get("image")
        prompt = request.form.get("prompt", "").lower()

        if not uploaded_image or not prompt:
            return jsonify({"error": "Image and prompt required"}), 400

        # -----------------------------
        # Load base image
        # -----------------------------
        base_image = Image.open(uploaded_image).convert("RGBA")

        # -----------------------------
        # Keyword → overlay mapping
        # -----------------------------
        overlay_map = {
            "red flowers": "red_flowers.png",
            "flowers": "red_flowers.png",
            "lace": "lace.png",
            "glitter": "glitter.png",
            "sparkle": "glitter.png",
            "embroidery": "embroidery.png"
        }

        overlays_to_apply = []

        # -----------------------------
        # 1. Detect all matching keywords
        # -----------------------------
        for keyword, file in overlay_map.items():
            if keyword in prompt:
                overlays_to_apply.append(file)

        if not overlays_to_apply:
            return jsonify({
                "error": "No valid design elements found in prompt"
            }), 400

        # -----------------------------
        # 2. Apply overlays sequentially
        # -----------------------------
        result = base_image

        for overlay_file in overlays_to_apply:
            overlay_path = os.path.join("static", "overlays", overlay_file)

            overlay = Image.open(overlay_path).convert("RGBA")
            overlay = overlay.resize(result.size)

            result = Image.alpha_composite(result, overlay)

        # -----------------------------
        # 3. Save final image
        # -----------------------------
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join("static", "result", filename)

        os.makedirs("static/result", exist_ok=True)
        result.save(save_path)

        return jsonify({
            "image_url": url_for("static", filename=f"result/{filename}", _external=True),
            "applied_effects": overlays_to_apply
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# SKETCH → IMAGE (OPTIONAL PLACEHOLDER)
# ==========================

@image_generation_bp.route("/generate_sketch_to_image", methods=["POST"])
def generate_sketch_to_image():
    try:
        uploaded_sketch = request.files.get("sketch")
        prompt = request.form.get("prompt", "").strip()

        if not uploaded_sketch or not prompt:
            return jsonify({"error": "Sketch and prompt required"}), 400

        return jsonify({
            "error": "Sketch mode disabled in local template system."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
