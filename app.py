from flask import Flask, render_template, request, jsonify, send_file, url_for
from flask_cors import CORS
from routes import register_blueprints
from routes.image_generation import generate_image_from_prompt
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

app = Flask(__name__)
CORS(app)
register_blueprints(app)

# ==========================
# BLOCKCHAIN (OPTIONAL)
# ==========================

BLOCKCHAIN_AVAILABLE = False
try:
    from web3 import Web3
    from blockchain_interaction import get_user_designs as _get_user_designs
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if w3.is_connected():
        BLOCKCHAIN_AVAILABLE = True
except Exception:
    pass

# ==========================
# PAGES
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
# TEXT TO IMAGE API
# ==========================

@app.route("/generate_text_to_image", methods=["POST"])
def handle_text_to_image():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    try:
        start_time = time.time()
        image_path, image_url = generate_image_from_prompt(prompt)
        generation_time = round(time.time() - start_time, 2)
        return jsonify({
            "image_url": image_url,
            "image_path": image_path,
            "generation_time_seconds": generation_time
        })
    except Exception as e:
        return jsonify({"error": f"Generation error: {str(e)}}"}), 500

# ==========================
# IPFS UPLOAD
# ==========================

@app.route("/upload_to_ipfs_from_url", methods=["POST"])
def upload_to_ipfs_from_url():
    data = request.get_json()
    image_url = data.get("image_url")
    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400
    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 500
        image_file = BytesIO(response.content)
        image_file.name = "design.png"
        ipfs_response = requests.post(
            "http://127.0.0.1:5001/api/v0/add",
            files={"file": image_file}
        )
        if ipfs_response.status_code != 200:
            return jsonify({"error": "IPFS not available in deployed mode"}), 503
        cid = ipfs_response.json()["Hash"]
        return jsonify({"cid": cid, "ipfs_url": f"https://ipfs.io/ipfs/{cid}"})
    except Exception as e:
        return jsonify({"error": "IPFS is only available when running locally with IPFS daemon"}), 503

# ==========================
# PDF GENERATION
# ==========================

@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json()
        cid = data.get("cid", "N/A")
        wallet = data.get("wallet", "N/A")

        # Try to fetch image from IPFS, fall back to placeholder
        image = None
        try:
            response = requests.get(f"http://127.0.0.1:8080/ipfs/{cid}", timeout=5)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
        except Exception:
            pass

        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        c.setFillColor(colors.whitesmoke)
        c.rect(0, 0, width, height, fill=True, stroke=0)
        c.setFillColor(colors.darkblue)
        c.rect(0, height - 80, width, 80, fill=True, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width / 2, height - 50, "StyleSensei Design Certificate")
        c.setStrokeColor(colors.grey)
        c.setLineWidth(2)
        c.rect(40, 40, width - 80, height - 120)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(60, height - 120, f"Wallet Address: {wallet}")
        c.drawString(60, height - 140, f"Design CID: {cid}")

        if image:
            c.drawImage(ImageReader(image), 60, height - 450, width=5.5 * inch, height=3.5 * inch, mask='auto')

        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, 30, "Generated and verified by StyleSensei Platform")
        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True,
                         download_name="style_sensei_design_certificate.pdf",
                         mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================
# BLOCKCHAIN - GET DESIGNS
# ==========================

@app.route("/get_user_designs", methods=["GET"])
def get_user_designs_route():
    if not BLOCKCHAIN_AVAILABLE:
        return jsonify({
            "error": "Blockchain (Ganache) is only available when running locally. This is the deployed demo version."
        }), 503
    wallet = request.args.get("wallet")
    if not wallet:
        return jsonify({"error": "Wallet address required"}), 400
    try:
        from web3 import Web3
        wallet_address = Web3.to_checksum_address(wallet)
        designs = _get_user_designs(wallet_address)
        result = [{"cid": d[0], "timestamp": d[1]} for d in designs]
        return jsonify({"designs": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
