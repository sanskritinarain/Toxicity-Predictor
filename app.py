# ============================================================
# app.py
# Flask API: accepts a SMILES string, returns a toxicity-risk score
#
# Run:
#   python app.py
#
# Endpoints:
#   GET  /health            -> service status + loaded model info
#   GET  /schema            -> request/response schema
#   POST /predict            -> {"smiles": "CCO"} -> risk score
#   POST /predict/batch      -> {"smiles": ["CCO", "c1ccccc1"]} -> list of risk scores
# ============================================================

import time
import logging
from flask import Flask, request, jsonify

from inference import ToxicityPredictor, InvalidSMILESError

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("tox21_api")

app = Flask(__name__)
predictor = ToxicityPredictor()
log.info(f"Loaded model: {predictor.model_name}")

SCHEMA = {
    "predict": {
        "method": "POST",
        "path": "/predict",
        "request": {"smiles": "string (required)", "threshold": "float, optional, default 0.5"},
        "response_200": {
            "smiles": "string",
            "toxicity_risk_score": "float in [0, 1] â€” model's predicted probability of toxicity",
            "predicted_label": "'Toxic' | 'Non-toxic'",
            "threshold": "float used for the label cutoff",
            "model": "string â€” name of the deployed model",
        },
        "response_400": {"error": "string â€” reason the SMILES could not be scored"},
    },
    "predict_batch": {
        "method": "POST",
        "path": "/predict/batch",
        "request": {"smiles": "list[string] (required)", "threshold": "float, optional, default 0.5"},
        "response_200": {"results": "list of per-SMILES objects (same shape as /predict, or {smiles, error})"},
    },
}


@app.route("/")
def index():
    import os
    from flask import send_file
    return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": predictor.model_name}), 200


@app.route("/schema", methods=["GET"])
def schema():
    return jsonify(SCHEMA), 200


@app.route("/predict", methods=["POST"])
def predict():
    t0 = time.time()
    body = request.get_json(silent=True) or {}
    smiles = body.get("smiles")
    threshold = float(body.get("threshold", 0.5))

    if smiles is None:
        return jsonify({"error": "Missing required field 'smiles'."}), 400

    try:
        result = predictor.predict(smiles, threshold)
    except InvalidSMILESError as e:
        log.warning(f"Invalid SMILES rejected: {smiles!r} ({e})")
        return jsonify({"error": str(e)}), 400

    log.info(f"POST /predict smiles={smiles!r} -> "
             f"score={result['toxicity_risk_score']} label={result['predicted_label']} "
             f"({(time.time() - t0) * 1000:.1f} ms)")
    return jsonify(result), 200


@app.route("/predict/batch", methods=["POST"])
def predict_batch():
    body = request.get_json(silent=True) or {}
    smiles_list = body.get("smiles")
    threshold = float(body.get("threshold", 0.5))

    if not isinstance(smiles_list, list) or not smiles_list:
        return jsonify({"error": "Field 'smiles' must be a non-empty list of strings."}), 400

    results = predictor.predict_batch(smiles_list, threshold)
    log.info(f"POST /predict/batch n={len(smiles_list)} "
             f"errors={sum(1 for r in results if 'error' in r)}")
    return jsonify({"results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


