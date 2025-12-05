# 📄 Invoice QC API (FastAPI)

A clean, backend-only **Invoice Quality Check (QC) API** built using **FastAPI**.  
This service validates **structured invoice JSON** and performs:

- Missing field detection  
- Incorrect / null values check  
- Amount & date format validation  
- Math consistency  
- Line-item verification  
- Structured validation summary  

Perfect for automation workflows, financial systems, and enterprise backend processing.

---

## 🚀 Features

### 🔍 JSON-Based Invoice Validation  
Send raw JSON → get clean validation response.

Validator checks:

- Mandatory fields  
- Missing values  
- Parsing errors  
- Math rules (`net_total + tax_amount == gross_total`)  
- Line-item issues  

---

### ⚡ FastAPI Backend  
- Automatic Swagger documentation  
- Built-in schema validation  
- Extremely fast API responses  
- Clear & modular code  

---

## 📂 Clone the Repository

```bash
git clone https://github.com/DibyanshuSah/invoice-qc-service.git
cd invoice-qc-service
```

---

## 🧱 Create Virtual Environment

```bash
python -m venv venv
```

---

## ▶️ Activate Virtual Environment

### 🔹 Windows
```bash
venv\Scripts\activate
```

### 🔹 macOS / Linux
```bash
source venv/bin/activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the FastAPI Server

```bash
uvicorn invoice_qc.api.main:app --reload --port 8000
```

---

## 🧪 Access API Documentation

### Swagger UI  
👉 http://127.0.0.1:8000/docs

### ReDoc  
👉 http://127.0.0.1:8000/redoc

---

## 📌 API Overview

### Health Check  
```bash
GET /health
```

Returns:
```
{ "status": "ok" }
```

---

## 🎯 Summary  
This API helps automate invoice verification with clean and structured validation logic.  
Ideal for integrating into ERP systems, finance pipelines, and backend automation tools.
