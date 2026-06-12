from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from routes import register_blueprints

from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import requests
import os
import time

# ==========================
# APP INIT
# ==========================

app = Flask(__name__)
CORS(app)

# Register all blueprints
register_blueprints(app)

# ==========================
# PAGES (FRONTEND ROUTES)
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/text_to_image")
def text_to_image():
    return render_template("text_to_image.html")


@app.route("/image_to_image")
def image_to_image():
    return render_template("image_to_image.html")


@app.route("/sketch_to_image")
def sketch_to_image():
    return render_template("sketch_to_image.html")


@app.route("/view_designs")
def view_designs():
    return render_template("view_designs.html")

# ==========================
# TEXT → IMAGE API (BLUEPRINT HANDLES GENERATION)
# ==========================

@app.route("/generate_text_to_image", methods=["POST"])
def handle_text_to_image():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        from routes.image_generation import generate_image_from_prompt

        start_time = time.time()
        image_path, image_url = generate_image_from_prompt(prompt)
        generation_time = round(time.time() - start_time, 2)

        return jsonify({
            "image_url": image_url,
            "image_path": image_path,
            "generation_time_seconds": generation_time
        })

    except Exception as e:
        return jsonify({"error": f"Generation error: {str(e)}"}), 500

@app.route("/generate_sketch_to_image", methods=["POST"])
def generate_sketch_to_image():
    try:
        uploaded_sketch = request.files.get("sketch")
        prompt = request.form.get("prompt", "").lower().strip()

        if not uploaded_sketch or not prompt:
            return jsonify({
                "error": "Sketch and prompt required"
            }), 400

        # Detect color from prompt
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
                "error": "Please specify a supported color"
            }), 400

        # Image file path
        image_filename = f"{detected_color}.png"

        image_path = os.path.join(
            app.root_path,
            "static",
            "dresses",
            "sketches",
            image_filename
        )

        print("Image Path:", image_path)
        print("Exists:", os.path.exists(image_path))

        if not os.path.exists(image_path):
            return jsonify({
                "error": f"Image not found: {image_filename}"
            }), 404

        # Build URL
        image_url = url_for(
            "static",
            filename=f"dresses/sketches/{image_filename}",
            _external=True
        )

        print("Generated URL:", image_url)

        return jsonify({
            "success": True,
            "image_url": image_url,
            "color_detected": detected_color,
            "sketch_used": image_filename
        })

    except Exception as e:
        print("Sketch Generation Error:", str(e))
        return jsonify({
            "error": str(e)
        }), 500

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
