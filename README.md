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

## How This Could Integrate Into a Larger System

This Invoice QC Service is built in a modular way so it can fit easily into a larger invoice-processing workflow.

### 1. Before QC (Upstream Systems)
Invoices usually come from:
- Email automation
- Upload portals
- Scanning/OCR tools

Any of these systems can call the `/validate-json` API after extracting invoice data.  
The QC service then checks whether the invoice is complete and correctly formatted.

### 2. After QC (Downstream Systems)
Once validation is done:
- Clean invoices can be automatically pushed into an ERP or accounting system.
- Invalid invoices can be flagged for manual review.
- The validation report can be logged for audit or analytics purposes.

### 3. Batch or Scheduled Processing
Organizations often process invoices in batches (e.g., daily).  
A simple cron job can run:

```bash
python -m invoice_qc.cli full-run --pdf-dir invoices --report daily_report.json
```

This allows the entire QC workflow to run automatically without human involvement.

Overall, the system is designed to stay simple and flexible so it can easily plug into any existing document pipeline.


