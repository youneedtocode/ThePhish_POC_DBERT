# ThePhish: AI-Powered Phishing Email Detection Tool

**ThePhish** is a standalone phishing email analysis tool that uses a fine-tuned DistilBERT model to detect and classify emails as either **malicious (phishing)** or **safe**. This tool augments the original open-source version with advanced NLP capabilities for high-accuracy threat detection.

---

## 🧠 Project Motivation

The motivation behind ThePhish project was to enhance a traditional phishing analysis tool with machine learning — specifically DistilBERT, a lightweight transformer model trained to detect subtle phishing cues in the email body and headers. This enables automated, intelligent phishing detection far beyond manual rules or keyword lists.

---

## 🔍 Features

- 📥 Automatically fetches and analyzes emails from a configured inbox
- 🧠 Utilizes a fine-tuned DistilBERT transformer model for phishing classification
- 💬 Displays verdicts (Safe or Malicious) along with phishing confidence scores
- 🖥️ Clean, browser-based UI for interacting with the tool
- 🔒 Supports secure credential setup via `.env` file or direct JSON editing
- 🧪 Trained on real-world email datasets (Enron, SpamAssassin, CEAS, Nazario, etc.)

---

## 🛠️ Quick Setup (Recommended)

To install all dependencies and prepare the environment automatically:

```bash
./setup.sh
````

This script will:

* Install system packages (Python, pip, venv, build tools)
* Install MongoDB 4.4 from the official MongoDB APT repository
* Create a virtual environment
* Install dependencies from both `requirements.txt` and `requirements-ml.txt`
* Provide next steps to launch the app

---

## 🚀 Manual Setup

### 1. Clone the Repository

```bash
git clone https://github.com/youneedtocode/ThePhish_POC_DBERT.git
cd ThePhish_POC_DBERT
```


> 💡 **Important:** You must also ensure MongoDB is installed and running on your system.

To install **MongoDB 4.4** manually on Ubuntu 20.04, run:

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl enable --now mongod
```
After installation, verify MongoDB is running:
```
sudo systemctl status mongod
```
You should see Active: active (running) in the output.

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
pip install -r app/requirements-ml.txt
```

---

## 🔐 Configure Email & MongoDB Credentials

You can configure credentials in **either of the following two ways**:

### ✅ Option 1 (Recommended): Use a `.env` file

1. Copy the template:

   ```bash
   cp app/env_template.txt app/.env
   nano app/.env
   ```

2. Fill in:

   ```env
   IMAP_HOST=imap.example.com
   IMAP_USER=your-email@example.com
   IMAP_PASS=your-app-password
   MONGO_URI=mongodb://localhost:27017
   ```

The app will use these variables to create or overwrite `configuration.json` automatically (if supported).

---

### 📝 Option 2: Manually Edit `configuration.json`

If you prefer, edit the following file directly:

```
app/configuration.json
```

Replace placeholders:

```json
{
  "imap": {
    "host": "imap.example.com",
    "port": "993",
    "user": "your-email@example.com",
    "password": "your-app-password",
    "folder": "inbox"
  }
}
```

---

## 📦 Place Model Files (Manual Step)

The DistilBERT fine-tuned model is not included due to size. Download or generate your model and place it in:

```bash
app/distilbert_phishing_finetuned_best/
```

Ensure it includes the `pytorch_model.bin`, `config.json`, and `tokenizer` files.

---

## ▶️ Run the App

```bash
cd app
python3 thephish_app.py
```

Visit [http://localhost:8080](http://localhost:8080) in your browser.

---

## 📂 Folder Structure

```
ThePhish_POC_DBERT/
├── setup.sh
├── app/
│   ├── run_analysis.py
│   ├── thephish_app.py
│   ├── utils.py
│   ├── templates/
│   ├── static/
│   ├── configuration.json
│   ├── whitelist.json
│   ├── requirements.txt
│   ├── requirements-ml.txt
│   └── ...
├── LICENSE
├── README.md
└── .gitignore
```

---

## 🧾 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions, feedback, and suggestions are welcome. Please fork the repo and submit a pull request.

```

