# invoice_qc/validator.py

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import date, datetime

from .schemas import Invoice
from .utils import parse_date, today_iso


ALLOWED_CURRENCIES = {"EUR", "USD", "INR", "GBP", "AUD", "CAD"}


def _parse_iso_date(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        # try generic parse again
        parsed = parse_date(value)
        if not parsed:
            return None
        try:
            return datetime.strptime(parsed, "%Y-%m-%d").date()
        except Exception:
            return None


def _approx_equal(a: float, b: float, rel_tol: float = 0.005, abs_tol: float = 0.01) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= max(abs(b) * rel_tol, abs_tol)


def validate_invoice(invoice: Invoice, seen_keys: set) -> Dict[str, Any]:
    """
    Apply completeness, format, business, and anomaly rules
    to a single invoice.
    Returns a dict with: invoice_id, invoice_number, is_valid, errors, warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []

    inv = invoice  # alias

    # ---------- COMPLETENESS RULES ----------
    if not inv.invoice_number:
        errors.append("missing_field: invoice_number")

    if not inv.invoice_date:
        errors.append("missing_field: invoice_date")

    if not inv.seller_name:
        errors.append("missing_field: seller_name")

    if not inv.buyer_name:
        errors.append("missing_field: buyer_name")

    # Money fields presence (for business rules)
    if inv.net_total is None:
        errors.append("missing_field: net_total")
    if inv.tax_amount is None:
        errors.append("missing_field: tax_amount")
    if inv.gross_total is None:
        errors.append("missing_field: gross_total")

    # ---------- FORMAT / TYPE RULES ----------

    # Date format and range check
    today = date.today()
    invoice_dt = _parse_iso_date(inv.invoice_date) if inv.invoice_date else None
    if inv.invoice_date and not invoice_dt:
        errors.append("format_error: invoice_date_unparseable")
    if invoice_dt:
        if invoice_dt < date(2000, 1, 1) or invoice_dt > (today.replace(year=today.year + 1)):
            errors.append("format_error: invoice_date_out_of_range")

    due_dt = _parse_iso_date(inv.due_date) if inv.due_date else None
    if inv.due_date and not due_dt:
        errors.append("format_error: due_date_unparseable")

    # Currency rule
    if inv.currency and inv.currency not in ALLOWED_CURRENCIES:
        errors.append("format_error: currency_invalid")

    # ---------- BUSINESS RULES ----------

    # Non-negative totals
    for field_name in ["net_total", "tax_amount", "gross_total"]:
        value = getattr(inv, field_name)
        if value is not None and value < 0:
            errors.append(f"business_rule_failed: {field_name}_negative")

    # net_total + tax_amount ≈ gross_total
    if inv.net_total is not None and inv.tax_amount is not None and inv.gross_total is not None:
        if not _approx_equal(inv.net_total + inv.tax_amount, inv.gross_total):
            errors.append("business_rule_failed: totals_mismatch")

    # Sum of line_items ≈ net_total
    if inv.line_items and inv.net_total is not None:
        sum_lines = sum(item.line_total for item in inv.line_items if item.line_total is not None)
        if not _approx_equal(sum_lines, inv.net_total):
            errors.append("business_rule_failed: line_items_mismatch")

    # due_date >= invoice_date
    if invoice_dt and due_dt:
        if due_dt < invoice_dt:
            errors.append("business_rule_failed: due_before_invoice")

    # ---------- ANOMALY / DUPLICATE RULE ----------
    # key: (invoice_number, seller_name, invoice_date)
    dup_key = (
        inv.invoice_number or "",
        inv.seller_name or "",
        inv.invoice_date or "",
    )
    if all(dup_key) and dup_key in seen_keys:
        errors.append("anomaly: duplicate_invoice")
    else:
        if all(dup_key):
            seen_keys.add(dup_key)

    # ---------- RESULT STRUCTURE ----------
    result = {
        "invoice_id": inv.invoice_id,
        "invoice_number": inv.invoice_number,
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
    return result


def validate_invoices(invoices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Entry point for validating a batch of invoices.
    invoices_data: list of raw dicts (e.g. from extractor).
    Returns:
      {
        "invoices": [ per-invoice result ...],
        "summary": {
            "total_invoices": int,
            "valid_invoices": int,
            "invalid_invoices": int,
            "error_counts": { error_code: count, ... }
        }
      }
    """
    seen_keys = set()
    per_invoice_results: List[Dict[str, Any]] = []
    error_counts = defaultdict(int)

    # Convert dict -> Invoice model to reuse validation
    invoices: List[Invoice] = [Invoice(**data) for data in invoices_data]

    for inv in invoices:
        res = validate_invoice(inv, seen_keys)
        per_invoice_results.append(res)
        for err in res["errors"]:
            error_counts[err] += 1

    total = len(per_invoice_results)
    invalid = sum(1 for r in per_invoice_results if not r["is_valid"])
    valid = total - invalid

    summary = {
        "total_invoices": total,
        "valid_invoices": valid,
        "invalid_invoices": invalid,
        "error_counts": dict(error_counts),
    }

    return {
        "invoices": per_invoice_results,
        "summary": summary,
    }
