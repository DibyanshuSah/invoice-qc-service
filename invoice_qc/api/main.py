# invoice_qc/api/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from invoice_qc.validator import validate_invoices

app = FastAPI(title="Invoice QC API", version="1.0")


# ----------------------- Models -----------------------
class InvoiceInput(BaseModel):
    invoice_id: str
    invoice_number: str | None = None
    external_reference: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    seller_name: str | None = None
    seller_tax_id: str | None = None
    buyer_name: str | None = None
    buyer_tax_id: str | None = None
    currency: str | None = None
    net_total: float | None = None
    tax_amount: float | None = None
    gross_total: float | None = None
    payment_terms: str | None = None
    line_items: List[Dict[str, Any]] = []
    raw_text: str | None = None


# ----------------------- Endpoints -----------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate-json")
def validate_json(invoices: List[InvoiceInput]):
    """
    Validate invoice JSON payload.
    """
    invoices_data = [inv.dict() for inv in invoices]
    result = validate_invoices(invoices_data)
    return result
