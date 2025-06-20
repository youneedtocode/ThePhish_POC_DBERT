# utils.py

import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# ✅ Path to the re-trained FineTunedBEST model
MODEL_PATH = "distilbert_phishing_finetuned_best"

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

def predict_phishing(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).squeeze()
        predicted_class = torch.argmax(probs).item()
    return predicted_class, probs.tolist()

