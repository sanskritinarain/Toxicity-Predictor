# Tox21 Toxicity-Risk API — Usage

## Setup
```bash
pip install flask rdkit joblib scikit-learn xgboost numpy
# Put experiment6_artifacts/final_selected_model.pkl + final_model_selection.json
# in the same directory as app.py / inference.py
python app.py
```
Runs at `http://127.0.0.1:5000`.

## Endpoints

### `GET /health`
Returns service status and the name of the loaded model.
```json
{"status": "ok", "model": "Random Forest"}
```

### `GET /schema`
Returns the request/response schema shown below as JSON.

### `POST /predict`
**Request**
```json
{"smiles": "CCO", "threshold": 0.5}
```
| Field | Type | Required | Notes |
|---|---|---|---|
| `smiles` | string | yes | Must be RDKit-parseable |
| `threshold` | float | no | Default `0.5`; cutoff for the binary label |

**Response — 200**
```json
{
  "smiles": "CCO",
  "toxicity_risk_score": 0.45,
  "predicted_label": "Non-toxic",
  "threshold": 0.5,
  "model": "Random Forest"
}
```
- `toxicity_risk_score`: model's predicted probability of toxicity, in [0, 1].
- `predicted_label`: `"Toxic"` if `toxicity_risk_score >= threshold`, else `"Non-toxic"`.

**Response — 400** (invalid or missing SMILES)
```json
{"error": "Could not parse SMILES: 'xyz'"}
```

### `POST /predict/batch`
**Request**
```json
{"smiles": ["CCO", "c1ccccc1"], "threshold": 0.5}
```
**Response — 200**
```json
{"results": [ {"...same shape as /predict..."}, {"smiles": "bad", "error": "..."} ]}
```

## Example
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CC(=O)Oc1ccccc1C(=O)O"}'
```

## Testing
`test_api.py` sends sample SMILES (including one invalid string) to a running
server and writes every request/response pair to `sample_request_response.log`.
```bash
python app.py &          # start the server
python test_api.py       # fires requests, writes the log
```

## Notes
- Featurisation matches Experiment 3/5: Morgan/ECFP4, radius 2, 2048 bits.
- This is the Flask dev server — for real deployment, run behind gunicorn/uwsgi.
- `inference.py` can be used standalone (`python inference.py`) without the API.
