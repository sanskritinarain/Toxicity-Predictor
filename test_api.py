# ============================================================
# test_api.py
# Sends sample requests to the running Flask API and logs the
# request/response pairs to sample_request_response.log
#
# Run (after `python app.py` is up in another terminal):
#   python test_api.py
# ============================================================

import json
import requests

BASE_URL = "http://127.0.0.1:5000"
LOG_FILE = "sample_request_response.log"

SAMPLE_SMILES = [
    "CCO",                              # ethanol
    "c1ccccc1",                         # benzene
    "CC(=O)Oc1ccccc1C(=O)O",            # aspirin
    "CC(C)Cc1ccc(cc1)C(C)C(=O)O",       # ibuprofen
    "C1=CC=C2C(=C1)C=CC(=O)O2",         # coumarin
    "invalid_smiles_xyz",               # should 400
]


def log_pair(f, title, req, resp):
    f.write(f"--- {title} ---\n")
    f.write(f"Request:  {json.dumps(req)}\n")
    f.write(f"Status:   {resp.status_code}\n")
    f.write(f"Response: {json.dumps(resp.json(), indent=2)}\n\n")


def main():
    with open(LOG_FILE, "w") as f:

        r = requests.get(f"{BASE_URL}/health")
        log_pair(f, "GET /health", {}, r)

        for s in SAMPLE_SMILES:
            req = {"smiles": s}
            r = requests.post(f"{BASE_URL}/predict", json=req)
            log_pair(f, f"POST /predict ({s})", req, r)

        req = {"smiles": SAMPLE_SMILES[:4]}
        r = requests.post(f"{BASE_URL}/predict/batch", json=req)
        log_pair(f, "POST /predict/batch", req, r)

    print(f"Done. See {LOG_FILE}")


if __name__ == "__main__":
    main()
