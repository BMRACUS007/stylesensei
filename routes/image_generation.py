from flask import Blueprint, request, url_for, jsonify
import os
import random

image_generation_bp = Blueprint("image_generation", __name__)

# ==========================
# CONFIG
# ==========================

dress_folder = os.path.join("static", "dresses")

colors = ["red", "blue", "black", "white", "green", "yellow", "pink"]

pattern_map = {
    "flowers": "flowers",
    "floral": "flowers",
    "glitter": "glitter",
    "sparkle": "glitter",
    "embroidery": "embroidery",
    "lace": "lace"
}

# ==========================
# TEXT → IMAGE (FOLDER PICKER)
# ==========================

@image_generation_bp.route("/generate_text_to_image", methods=["POST"])
def generate_text_to_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").lower().strip()

        if not prompt:
            return jsonify({"error": "Prompt required"}), 400

        detected_color = None
        for color in colors:
            if color in prompt:
                detected_color = color
                break

        if not detected_color:
            return jsonify({"error": "Network Error"}), 400

        folder_path = os.path.join(dress_folder, detected_color)

        if not os.path.exists(folder_path):
            return jsonify({"error": "Network Error"}), 404

        images = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not images:
            return jsonify({"error": "Network Error"}), 404

        selected = random.choice(images)

        return jsonify({
            "image_url": url_for(
                "static",
                filename=f"dresses/{detected_color}/{selected}",
                _external=True
            ),
            "mode": "local_color_random"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# IMAGE → IMAGE (PATTERN PICKER)
# ==========================

@image_generation_bp.route("/generate_image_to_image", methods=["POST"])
def generate_image_to_image():
    try:
        uploaded_image = request.files.get("image")
        prompt = request.form.get("prompt", "").lower().strip()

        if not uploaded_image or not prompt:
            return jsonify({"error": "Image and prompt required"}), 400

        detected_pattern = None

        for key, folder in pattern_map.items():
            if key in prompt:
                detected_pattern = folder
                break

        if not detected_pattern:
            return jsonify({"error": "Network Error"}), 400

        folder_path = os.path.join("static", "dresses", detected_pattern)

        if not os.path.exists(folder_path):
            return jsonify({"error": "Network Error"}), 404

        images = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not images:
            return jsonify({"error": "Network Error"}), 404

        selected = random.choice(images)

        return jsonify({
            "image_url": url_for(
                "static",
                filename=f"dresses/{detected_pattern}/{selected}",
                _external=True
            ),
            "pattern_detected": detected_pattern
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# SKETCH → IMAGE (DISABLED)
# ==========================

@image_generation_bp.route("/generate_sketch_to_image", methods=["POST"])
def generate_sketch_to_image():
    try:
        uploaded_sketch = request.files.get("sketch")
        prompt = request.form.get("prompt", "").lower().strip()

        if not uploaded_sketch or not prompt:
            return jsonify({
                "error": "Sketch and prompt required"
            }), 400

        # -------------------------
        # 1. Detect color from prompt
        # -------------------------
        colors = [
            "red",
            "blue",
            "black",
            "white",
            "green",
            "grey",
            "pink",
            "purple"
        ]

        detected_color = None

        for color in colors:
            if color in prompt:
                detected_color = color
                break

        if not detected_color:
            return jsonify({
                "error": "Please specify a color in the prompt"
            }), 400

        # -------------------------
        # 2. Find corresponding image
        # -------------------------
        image_filename = f"{detected_color}.png"

        image_path = os.path.join(
            "static",
            "dresses",
            "sketches",
            image_filename
        )

        print("Checking:", image_path)

        if not os.path.exists(image_path):
            return jsonify({
                "error": f"Image not found for color: {detected_color}"
            }), 404

        # -------------------------
        # 3. Build image URL
        # -------------------------
        image_url = url_for(
            "static",
            filename=f"dresses/sketches/{image_filename}",
            _external=True
        )

        print("Detected Color:", detected_color)
        print("Image URL:", image_url)

        # -------------------------
        # 4. Return response
        # -------------------------
        return jsonify({
            "image_url": image_url,
            "mode": "local_sketch_template",
            "color_detected": detected_color,
            "sketch_used": image_filename
        })

    except Exception as e:
        print("Sketch-to-Image Error:", e)
        return jsonify({
            "error": str(e)
        }), 500
