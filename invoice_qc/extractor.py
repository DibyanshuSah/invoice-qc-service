import pdfplumber
import re
import tempfile
import os
from typing import Dict, Any


# ---------------------------- HELPERS ----------------------------

def clean(text: str):
    if not text:
        return ""
    return text.replace("\t", " ").replace("  ", " ").strip()


def find_value(patterns, text):
    """Try multiple regex patterns."""
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_amount(text):
    """Extract number 12,345.67 → 12345.67"""
    if not text:
        return None
    m = re.search(r"([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?)", text)
    if m:
        return float(m.group(1).replace(",", ""))
    return None


def extract_date(text):
    if not text:
        return None
    m = re.search(r"(\d{1,2}-[A-Za-z]{3}-\d{2,4})", text)
    return m.group(1) if m else None


# ---------------------------- MAIN EXTRACTION ----------------------------

def extract_invoice_from_pdf(filepath: str) -> Dict[str, Any]:

    # Load PDF
    with pdfplumber.open(filepath) as pdf:
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    text = clean(raw_text)

    extracted = {
        "invoice_id": os.path.basename(filepath),
        "raw_text": raw_text
    }

    # ---------------- INVOICE NUMBER ----------------
    extracted["invoice_number"] = find_value([
        r"Invoice\s*No[:\- ]*\s*(.+)",
        r"Invoice\s*Number[:\- ]*\s*(.+)",
        r"Inv\s*No[:\- ]*\s*(.+)",
        r"Bill\s*No[:\- ]*\s*(.+)",
        r"\b([A-Z]{2,10}\/[0-9]{2}-[0-9]{2}\/[0-9]+)\b",
        r"\b([A-Z]{2,10}\/[0-9]{2,4}\/[0-9]+)\b",
    ], text)

    # ---------------- INVOICE DATE ----------------
    extracted["invoice_date"] = extract_date(
        find_value([
            r"Dated[:\- ]*\s*(.+)",
            r"Invoice\s*Date[:\- ]*\s*(.+)",
            r"\b(\d{1,2}-[A-Za-z]{3}-\d{2,4})\b"
        ], text)
    )

    # ---------------- SELLER NAME (Works on your 4 invoices) ----------------
    seller = None
    lines = raw_text.split("\n")

    for i, line in enumerate(lines):
        if "GSTIN" in line:
            # Line above GSTIN
            if i > 0:
                possible = lines[i - 1].strip()
                if len(possible) > 2:
                    seller = possible

            # Fallback 2 lines above
            if not seller and i > 1:
                possible = lines[i - 2].strip()
                if len(possible) > 2:
                    seller = possible
            break

    extracted["seller_name"] = seller

    # ---------------- BUYER NAME (works on all your samples) ----------------
    buyer = find_value([
        r"Buyer.*?\n(.*?)\n",
        r"Buyer\s*\(Bill to\)\s*\n(.*?)\n",
        r"Billed To\s*\n(.*?)\n",
    ], raw_text)

    extracted["buyer_name"] = buyer

    # ---------------- TOTAL AMOUNTS ----------------
    extracted["gross_total"] = extract_amount(
        find_value([
            r"Grand\s*Total[:\- ]*\s*([0-9,]+\.[0-9]+)",
            r"Total\s*Amount[:\- ]*\s*([0-9,]+\.[0-9]+)",
            r"Total\s*[:\- ]*\s*([0-9,]+\.[0-9]+)",
        ], text)
    )

    extracted["net_total"] = extract_amount(
        find_value([
            r"Taxable\s*Value[:\- ]*\s*([0-9,]+\.[0-9]+)",
            r"Subtotal[:\- ]*\s*([0-9,]+\.[0-9]+)",
            r"Net\s*Total[:\- ]*\s*([0-9,]+\.[0-9]+)",
        ], text)
    )

    extracted["tax_amount"] = extract_amount(
        find_value([
            r"CGST.*?([0-9,]+\.[0-9]+)",
            r"SGST.*?([0-9,]+\.[0-9]+)",
            r"IGST.*?([0-9,]+\.[0-9]+)",
        ], text)
    )

    # ---------------- LINE ITEMS (optional for now) ----------------
    extracted["line_items"] = []  # you can upgrade later

    return extracted


# ---------------------------- WRAPPER FOR FASTAPI ----------------------------

def extract_invoice(pdf_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    return extract_invoice_from_pdf(tmp_path)
