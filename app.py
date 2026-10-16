"""
Anaya Elegance — AI Backend (Flask)
Free-tier deployment: Render.com or Hugging Face Spaces

Endpoints:
  POST /api/tryon        — Virtual try-on (garment + person → dressed photo)
  POST /api/skin-analysis — Skin diagnosis via Gemini Flash (proxy, optional)

Try-on modes:
  TRYON_MODE=gradio  (default, FREE) — calls a free community Hugging Face Space
  TRYON_MODE=local   (needs GPU)     — runs IDM-VTON locally (see README)
"""
import os
import io
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow the static storefront to call this API

# Free community IDM-VTON demo on Hugging Face Spaces (gradio API).
# If this Space is down, set TRYON_MODE=local with a GPU, or point to another
# public Space URL. See README §Try-On.
GRADIO_SPACE_URL = os.environ.get(
    "GRADIO_SPACE_URL",
    "https://yisol-idm-vton.hf.space",  # free community demo
)

TRYON_MODE = os.environ.get("TRYON_MODE", "gradio")


def _b64_to_bytes(b64: str) -> bytes:
    """Convert a data URL or raw base64 string to bytes."""
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "mode": TRYON_MODE})


@app.route("/api/tryon", methods=["POST"])
def tryon():
    """
    JSON body:
      {
        "person": "<dataURL>",   # customer selfie
        "garment": "<dataURL>",  # product photo (front/side/back)
        "angle": "front"         # front | side | back
      }
    Returns: { "image": "<dataURL>" }
    """
    data = request.get_json(force=True, silent=True) or {}
    person_b64 = data.get("person")
    garment_b64 = data.get("garment")
    angle = data.get("angle", "front")

    if not person_b64 or not garment_b64:
        return jsonify({"error": "person and garment images are required"}), 400

    if TRYON_MODE == "gradio":
        return _tryon_gradio(person_b64, garment_b64, angle)
    return jsonify({"error": "TRYON_MODE=local requires a GPU server"}), 501


def _tryon_gradio(person_b64: str, garment_b64: str, angle: str):
    """Call a free community IDM-VTON Space via its gradio API."""
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        return jsonify({"error": "gradio-client not installed on server"}), 500

    try:
        client = Client(GRADIO_SPACE_URL)
        # IDM-VTON demo signature: (person_img, garment_img, description, ...)
        result = client.predict(
            handle_file(_dataurl_to_temp(person_b64)),
            handle_file(_dataurl_to_temp(garment_b64)),
            f"a photo of a person wearing the garment, {angle} view",
            True,   # auto crop
            32,     # steps
            20.0,   # guidance scale
            -1,     # seed (random)
            api_name="/on_submit",
        )
        # result is typically a dict or list with the output image path
        out = result[0] if isinstance(result, (list, tuple)) else result
        if isinstance(out, dict):
            out = out.get("image") or out.get("path")
        if not out:
            return jsonify({"error": "try-on model returned no image"}), 502

        with open(out, "rb") as f:
            out_b64 = base64.b64encode(f.read()).decode()
        return jsonify({"image": f"data:image/png;base64,{out_b64}"})

    except Exception as e:
        return jsonify({"error": f"try-on failed: {str(e)}"}), 502


def _dataurl_to_temp(dataurl: str) -> str:
    """Save a data URL to a temp file, return its path (gradio needs a path)."""
    import tempfile
    suffix = ".png"
    if "image/jpeg" in dataurl:
        suffix = ".jpg"
    path = tempfile.mktemp(suffix=suffix)
    with open(path, "wb") as f:
        f.write(_b64_to_bytes(dataurl))
    return path


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
