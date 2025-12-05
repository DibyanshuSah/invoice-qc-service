# 📄 Invoice QC API (FastAPI)

A clean, backend-only **Invoice Quality Check (QC) API** built using FastAPI.  
This service validates **structured invoice JSON** and performs:

- Missing field detection  
- Format validation  
- Math consistency checks  
- Structured validation report generation  

This API is suitable for backend automation, finance workflows,  
and enterprise invoice processing systems.

---

## 🚀 Features

### 🔍 **1. JSON-Based Invoice Validation**
No PDF needed.  
You directly send structured JSON containing invoice fields.

The validator checks:

- Mandatory fields  
- Missing values  
- Incorrect or null fields  
- Math validation  
  (`net_total + tax_amount == gross_total`)  
- Line item consistency  

---

### ⚡ **2. FastAPI — High-Performance Backend**
Provides:
- Automatic Swagger UI (`/docs`)
- Auto-generated schemas
- Clean endpoint design
- Pydantic validation

---

## 🏗️ Project Structure

