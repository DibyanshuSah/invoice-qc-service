# invoice_qc/cli.py

import json
import os
import typer
from typing import Optional, List

from .extractor import extract_invoice_from_pdf
from .validator import validate_invoices

app = typer.Typer(help="Invoice QC CLI Tool")


# ------------------- Extract Command -------------------
@app.command("extract")
def extract_cmd(
    pdf_dir: str = typer.Argument(..., help="Directory containing invoice PDFs"),
    output: str = typer.Option("extracted.json", help="Output JSON file"),
):
    """
    Extract structured invoice data from PDFs.
    """
    results = []

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            typer.echo(f"Extracting: {filename}")
            try:
                extracted = extract_invoice_from_pdf(pdf_path)
                results.append(extracted)
            except Exception as e:
                typer.echo(f"Failed to extract {filename}: {e}")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    typer.echo(f"\nSaved extracted data to {output}")


# ------------------- Validate Command -------------------
@app.command("validate")
def validate_cmd(
    input: str = typer.Argument(..., help="Extracted JSON file"),
    report: str = typer.Option("validation_report.json", help="Output report file"),
):
    """
    Validate extracted invoice JSON against QC rules.
    """
    with open(input, "r", encoding="utf-8") as f:
        invoices = json.load(f)

    typer.echo("Running validation...")
    results = validate_invoices(invoices)

    with open(report, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    typer.echo(f"\nValidation completed. Report saved to {report}")

    summary = results["summary"]
    typer.echo(f"\nSummary:")
    typer.echo(f"  Total invoices: {summary['total_invoices']}")
    typer.echo(f"  Valid invoices: {summary['valid_invoices']}")
    typer.echo(f"  Invalid invoices: {summary['invalid_invoices']}")


# ------------------- Full Run Command -------------------
@app.command("full-run")
def full_run_cmd(
    pdf_dir: str = typer.Argument(..., help="PDF directory"),
    report: str = typer.Option("validation_report.json"),
):
    """
    Extract + Validate in a single command.
    """
    typer.echo("Extracting PDFs...")
    extracted = []

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            typer.echo(f"Extracting {filename}")
            extracted.append(extract_invoice_from_pdf(pdf_path))

    typer.echo("\nValidating extracted data...")
    results = validate_invoices(extracted)

    with open(report, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    typer.echo(f"\nReport written to {report}")

    summary = results["summary"]
    typer.echo("\nSummary:")
    typer.echo(f"  Total invoices: {summary['total_invoices']}")
    typer.echo(f"  Valid invoices: {summary['valid_invoices']}")
    typer.echo(f"  Invalid invoices: {summary['invalid_invoices']}")


def main():
    app()


if __name__ == "__main__":
    main()
