import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ✅ Load and preprocess the test data
df = pd.read_csv("final_combined_email_dataset.csv")
df = df.rename(columns={"body": "text", "label": "label"})
df = df[df['text'].notna()]
df = df.reset_index(drop=True)

# ✅ Use a fixed test split (optional: change this logic if needed)
test_df = df.sample(n=5000, random_state=42)

# ✅ Load tokenizer and model
model_path = "distilbert_phishing_finetuned_best"
tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# ✅ Dataset class
class EmailDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=max_len)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# ✅ Prepare DataLoader
test_dataset = EmailDataset(test_df['text'].tolist(), test_df['label'].tolist(), tokenizer)
test_loader = DataLoader(test_dataset, batch_size=16)

# ✅ Inference
preds, true = [], []
with torch.no_grad():
    for batch in test_loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        preds.extend(predictions.cpu().numpy())
        true.extend(batch["labels"].cpu().numpy())

# ✅ Results
print(f"\n✅ Accuracy: {accuracy_score(true, preds):.4f}")
print("📊 Classification Report:\n", classification_report(true, preds))
print("📊 Confusion Matrix:\n", confusion_matrix(true, preds))

