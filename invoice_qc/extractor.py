# invoice_qc/extractor.py

import pdfplumber
import re
from typing import List, Dict, Any
from .schemas import Invoice, LineItem
from .utils import parse_amount, parse_date
import os


# --------------------- Helper: Match first regex ---------------------
def get_first_match(patterns, text):
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1)
    return None


# --------------------- MAIN EXTRACTION FUNCTION ----------------------
def extract_invoice_from_pdf(pdf_path: str) -> Dict[str, Any]:

    # Read entire PDF text
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    text = raw_text.replace("\t", " ").replace("  ", " ")

    # ---------------- FIELD PATTERNS ----------------
    patterns = {
        "invoice_number": [
            r"Bestellung\s+(AUFNR[0-9]+)",
            r"Bestellung.*?(AUFNR[0-9]+)",
            r"(AUFNR[0-9]+)"
        ],
        "invoice_date": [
            r"vom\s+([0-9]{2}\.[0-9]{2}\.[0-9]{4})",
            r"([0-9]{2}\.[0-9]{2}\.[0-9]{4})"
        ],
        "net_total": [
            r"Gesamtwert\s*EUR\s*([0-9\.,]+)",
            r"Gesamtwert.*?([0-9\.,]+)"
        ],
        "tax_amount": [
            r"MwSt\.\s*[0-9,]+%?\s*EUR\s*([0-9\.,]+)",
            r"MwSt.*?EUR\s*([0-9\.,]+)"
        ],
        "gross_total": [
            r"Gesamtwert inkl\. MwSt\.\s*EUR\s*([0-9\.,]+)",
            r"inkl\. MwSt.*?EUR\s*([0-9\.,]+)"
        ],
        "currency": [
            r"\b(EUR)\b"
        ]
    }

    extracted = {
        "invoice_id": os.path.basename(pdf_path),
        "raw_text": raw_text
    }

    # ---------------- EXTRACT SIMPLE FIELDS ----------------
    for field, pats in patterns.items():
        value = get_first_match(pats, text)

        # Date conversion
        if field == "invoice_date":
            value = parse_date(value)

        # Amount conversion
        if field in ["net_total", "tax_amount", "gross_total"]:
            value = parse_amount(value)

        extracted[field] = value

    # ---------------------- LINE ITEMS (STRICT FIXED VERSION) ---------------------
    line_items = []

    # Strict Euro price format: 2 decimal digits after comma
    MONEY = r"[0-9]{1,6},[0-9]{2}"

    item_pattern = rf"^\s*(\d+)\s+([A-Za-zÄÖÜäöüß\- ]+)\s+(\d+).*?({MONEY})$"

    for line in raw_text.split("\n"):
        line = line.strip()

        # Reject lines containing phone numbers, slashes, or long IDs
        if "/" in line:
            continue
        if re.search(r"\b[0-9]{7,}\b", line):  
            continue  # rejects 11223344, 3498578433, 0102860405, etc.

        # Must end with valid price
        if not re.search(rf"{MONEY}$", line):
            continue

        m = re.match(item_pattern, line)
        if m:
            _, desc, qty, total = m.groups()
            line_items.append(LineItem(
                description=desc.strip(),
                quantity=float(qty),
                unit_price=None,
                line_total=parse_amount(total)
            ))

    extracted["line_items"] = line_items

    # ---------------- RETURN AS INVOICE OBJECT ----------------
    return Invoice(**extracted).dict()
