Invoice QC Service

This project extracts data from invoice PDFs and validates them using custom rules.

How to run
1. Activate environment
venv\Scripts\activate

2. Extract invoices from PDF folder
python -m invoice_qc.cli extract samples --output extracted.json

3. Validate extracted invoices
python -m invoice_qc.cli validate extracted.json --report report.json

4. Run API
uvicorn invoice_qc.api.main:app --reload


Open Swagger Docs:

http://127.0.0.1:8000/docs