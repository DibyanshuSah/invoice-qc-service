from typing import Optional, List
from pydantic import BaseModel

class LineItem(BaseModel):
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]
    line_total: float

class Invoice(BaseModel):
    invoice_id: str
    invoice_number: Optional[str] = None
    external_reference: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    payment_terms: Optional[str] = None
    line_items: List[LineItem] = []
    raw_text: Optional[str] = None
