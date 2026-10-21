# ============================================================
# inference.py
# Life-Project 2: Drug Molecule Toxicity Prediction
# Scoring script: SMILES string -> toxicity risk score
#
# Loads:
#   experiment6_artifacts/final_selected_model.pkl   (joblib)
#   experiment6_artifacts/final_model_selection.json (metadata)
#
# Supports joblib-saved sklearn-style models (RF, XGBoost sklearn
# wrapper, or a joblib-dumped NN wrapper) that expose predict_proba.
# ============================================================

import os
import json
import joblib
import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator

RDLogger.DisableLog('rdApp.*')

EVAL_DIR = "experiment6_artifacts"
MODEL_PATH = os.path.join(EVAL_DIR, "final_selected_model.pkl")
INFO_PATH = os.path.join(EVAL_DIR, "final_model_selection.json")

N_BITS = 2048
RADIUS = 2

_morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=RADIUS, fpSize=N_BITS)


class InvalidSMILESError(ValueError):
    pass


def smiles_to_fingerprint(smiles: str) -> np.ndarray:
    """Convert a SMILES string to a (1, N_BITS) ECFP4 fingerprint array."""
    if not isinstance(smiles, str) or not smiles.strip():
        raise InvalidSMILESError("SMILES string is empty.")
    mol = Chem.MolFromSmiles(smiles.strip())
    if mol is None:
        raise InvalidSMILESError(f"Could not parse SMILES: '{smiles}'")
    fp = _morgan_gen.GetFingerprintAsNumPy(mol)
    return fp.astype(np.float32).reshape(1, -1)


class ToxicityPredictor:
    def __init__(self, model_path: str = MODEL_PATH, info_path: str = INFO_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}. Run Experiment 6 first.")
        from xgboost import XGBClassifier; self.model = XGBClassifier(); self.model.load_model(os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment6_artifacts", "final_selected_model.json"))

        self.info = {}
        if os.path.exists(info_path):
            with open(info_path) as f:
                self.info = json.load(f)
        self.model_name = self.info.get("selected_model", type(self.model).__name__)

    def predict(self, smiles: str, threshold: float = 0.5) -> dict:
        """Return a toxicity-risk score (0-1) and a binary label for one SMILES string."""
        X = smiles_to_fingerprint(smiles)

        if hasattr(self.model, "predict_proba"):
            risk_score = float(self.model.predict_proba(X)[0, 1])
        elif hasattr(self.model, "decision_function"):
            raw = float(self.model.decision_function(X)[0])
            risk_score = 1 / (1 + np.exp(-raw))
        else:
            risk_score = float(self.model.predict(X)[0])

        return {
            "smiles": smiles,
            "toxicity_risk_score": round(risk_score, 6),
            "predicted_label": "Toxic" if risk_score >= threshold else "Non-toxic",
            "threshold": threshold,
            "model": self.model_name,
        }

    def predict_batch(self, smiles_list, threshold: float = 0.5) -> list:
        results = []
        for s in smiles_list:
            try:
                results.append(self.predict(s, threshold))
            except InvalidSMILESError as e:
                results.append({"smiles": s, "error": str(e)})
        return results


if __name__ == "__main__":
    predictor = ToxicityPredictor()

    sample_smiles = [
        "CCO",                      # ethanol
        "c1ccccc1",                 # benzene
        "CC(=O)Oc1ccccc1C(=O)O",    # aspirin
        "O=C(C)Oc1ccccc1C(=O)O",    # aspirin (alt form)
        "not_a_valid_smiles!!",     # invalid input
    ]

    print(f"Loaded model: {predictor.model_name}\n")
    for r in predictor.predict_batch(sample_smiles):
        print(r)
