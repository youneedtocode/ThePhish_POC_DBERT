import os
import sys
import json
import traceback
import logging.config
from utils import predict_phishing  # uses fine-tuned DistilBERT from ./distilbert_phishing_finetuned_best
from pymongo import MongoClient
from datetime import datetime

print("✅ Starting run_analysis.py...")

def main(wsl, case, external_from_field, subject_text, body_text, mail_uid):
    print(f"➡️ Arguments received: {sys.argv}")
    thehive_enabled = os.environ.get("THEHIVE_ENABLED", "False").lower() == "true"

    try:
        with open('logging_conf.json') as log_conf:
            log_conf_dict = json.load(log_conf)
            logging.config.dictConfig(log_conf_dict)
    except Exception:
        print("[ERROR]_[run_analysis]: Error while trying to open 'logging_conf.json': {}".format(traceback.format_exc()))
        return
    log = logging.getLogger(__name__)

    try:
        log.info("Skipping TheHive case creation logic (standalone mode).")
    except Exception:
        log.error("Unexpected error while skipping TheHive logic: {}".format(traceback.format_exc()))

    try:
        combined_text = ((subject_text or "") + " " + (body_text or "")).lower()
        distilbert_pred, probs = predict_phishing(combined_text)
        distilbert_prob = probs[1]  # probability of class 1 (phishing)

        log.info(f"📊 Model prediction: {distilbert_pred}")
        log.info(f"🔢 Probability (class 0 - Safe): {probs[0]}")
        log.info(f"🔢 Probability (class 1 - Phishing): {probs[1]}")
        wsl.emit_info(f"📊 Model prediction: {distilbert_pred}")
        wsl.emit_info(f"🔢 Probability (class 0 - Safe): {probs[0]:.6f}")
        wsl.emit_info(f"🔢 Probability (class 1 - Phishing): {probs[1]:.6f}")

        verdict = "Malicious" if distilbert_pred == 1 else "Safe"

        log.info(f"ML Model Verdict: {verdict}")
        wsl.emit_info(f"Verdict: {verdict}")

    except Exception as e:
        log.error(f"Model prediction failed: {str(e)}")
        verdict = "Safe"
        wsl.emit_info("Verdict: Safe (fallback due to model error)")

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['thephish']
        verdicts_collection = db['verdicts']

        verdict_doc = {
            "mail_to": external_from_field if external_from_field else "unknown",
            "mail_uid": mail_uid,
            "verdict": verdict,
            "subject": subject_text,
            "timestamp": datetime.utcnow()
        }
        verdicts_collection.insert_one(verdict_doc)
        log.info("Verdict successfully saved to MongoDB")
    except Exception as e:
        log.error(f"Failed to store verdict in MongoDB: {str(e)}")

    return verdict

