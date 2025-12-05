# Invoice QC Service

This project extracts data from invoice PDFs and validates them using custom rules.

## How to run

### 1. Activate environment
```bash
venv\Scripts\activate
```

### 2. Extract invoices from PDF folder
```bash
python -m invoice_qc.cli extract samples --output extracted.json
```

### 3. Validate extracted invoices
```bash
python -m invoice_qc.cli validate extracted.json --report report.json
```

### 4. Run API
```bash
uvicorn invoice_qc.api.main:app --reload
```

### Open Swagger Docs:
```
http://127.0.0.1:8000/docs
```
## AI Usage Notes

I used AI tools only for a few difficult parts of the assignment, mainly where human effort is usually higher:

### 1. Regex Complexity
Some of the regex patterns required to match invoice numbers, currency formats, and line-item structures were complex.  
I used AI to get initial ideas, but I manually refined and corrected them to fit the exact format of the provided PDFs.

For example, AI suggested a loose pattern:
```regex
([0-9\.,]+)$
```

I later replaced this with a stricter EUR-compatible pattern:
```regex
MONEY = r"[0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}"
```

This ensured the extractor did not incorrectly match phone numbers or unrelated numeric values.

---

### 2. Debugging & Issue Investigation
During development, I used AI to understand certain bugs quickly : - for example, why some text lines were being captured incorrectly or why a validation rule wasn’t triggering.  
The final fixes were implemented manually after testing on actual invoice samples.

---

### 3. High-Level Architecture Guidance
I used AI to confirm some high-level design choices, such as:
- separating the project into extractor, validator, schemas, and CLI modules  
- returning structured responses from the validator  
- exposing functionality through FastAPI  

The actual implementation and design details were written manually.

---

### Notes
AI acted only as a helper for complex patterns and debugging.  
All extraction logic, validation rules, CLI workflow, and API code were fully implemented by me.


## How This Could Integrate Into a Larger System

This Invoice QC Service is designed so that it can easily plug into a bigger workflow where companies receive and process invoices regularly.

### 1. Upstream Integration (Before QC)
In a real system, invoices may come from:
- Email automation
- A document upload portal
- A scanning/OCR service

Any of these services can simply call the `/validate-json` API after extracting the text.  
The QC service then checks whether the invoice is complete and valid before sending it further into the system.

### 2. Downstream Integration (After QC)
Once the invoice is validated, another service (for example, an ERP or accounting system) can:
- Automatically accept the invoice
- Flag it for manual review if errors are found
- Store the validation summary for reporting

### 3. Scheduled or Batch Processing
Some companies process invoices in batches (e.g., at night).  
A simple cron job could run:

```bash
python -m invoice_qc.cli full-run --pdf-dir invoices --report daily_report.json
```

This makes it easy to automate QC without manual intervention.

### 4. Containerization (Optional)
If needed, the service can be packaged into a Docker container so it can run as a small microservice inside cloud or on-prem systems.

The goal is that this QC service remains simple, modular, and reusable so it can fit into different setups depending on how the company handles invoices.


