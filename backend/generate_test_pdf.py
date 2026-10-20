"""Generate sample loan agreement PDFs for FinGuard demo."""

import sys
sys.path.insert(0, '.')

def generate_sample_loan_pdf():
    """Generate a realistic sample loan agreement PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        # Use reportlab as fallback, or just create with pymupdf
        pass

    # Use PyMuPDF (fitz) to create the PDF - already installed
    import fitz

    doc = fitz.open()

    # Page 1: Title and basic terms
    page = doc.new_page()
    rect = page.rect

    # Title
    page.insert_text(
        fitz.Point(72, 72),
        "PERSONAL LOAN AGREEMENT",
        fontsize=18,
        fontname="helv",
    )
    page.insert_text(
        fitz.Point(72, 95),
        "QuickCash Finance Ltd.",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        fitz.Point(72, 115),
        "Agreement No: QCF-2026-00847",
        fontsize=10,
        fontname="helv",
    )

    y = 150
    sections = [
        ("1. LOAN AMOUNT AND DISBURSEMENT", [
            "The Lender agrees to provide a personal loan of $10,000.00 (Ten Thousand US Dollars)",
            "to the Borrower. The loan amount shall be disbursed within 3 business days of signing",
            "this agreement, subject to completion of all verification procedures.",
            "A processing fee of $250.00 (2.5% of the principal) shall be deducted at disbursement.",
        ]),
        ("2. INTEREST RATE", [
            "The annual interest rate shall be 18.5% per annum, calculated on the outstanding",
            "principal balance. The interest rate is variable and may be adjusted at the Lender's",
            "discretion based on market conditions. The Lender reserves the right to modify the",
            "rate with 30 days written notice to the Borrower.",
        ]),
        ("3. REPAYMENT SCHEDULE", [
            "The Borrower shall repay the loan in 36 monthly installments. Each monthly payment",
            "shall be approximately $364.00, consisting of principal and interest portions.",
            "The first payment is due 30 days from the date of disbursement.",
        ]),
        ("4. FEES AND CHARGES", [
            "Processing Fee: $250.00 (deducted from disbursement)",
            "Annual Account Maintenance Fee: $50.00",
            "Statement Request Fee: $5.00 per statement",
            "Payment Processing Fee: $2.50 per transaction",
        ]),
        ("5. LATE PAYMENT PENALTIES", [
            "If any installment is not received within 7 days of the due date, a late payment",
            "fee of 5% of the overdue amount shall be charged. Late fees shall compound monthly.",
            "After 30 days of non-payment, the default interest rate of 24% per annum shall apply",
            "to the entire outstanding balance.",
        ]),
    ]

    for heading, lines in sections:
        page.insert_text(fitz.Point(72, y), heading, fontsize=11, fontname="hebo")
        y += 18
        for line in lines:
            page.insert_text(fitz.Point(72, y), line, fontsize=9, fontname="helv")
            y += 13
        y += 10

    # Page 2: More clauses
    page2 = doc.new_page()
    y = 72

    sections2 = [
        ("6. EARLY REPAYMENT", [
            "The Borrower may repay the loan in full before the maturity date. An early",
            "repayment penalty of 3% of the remaining principal balance shall apply if the",
            "loan is repaid within the first 12 months. After 12 months, the early repayment",
            "penalty reduces to 1.5% of the remaining principal balance.",
        ]),
        ("7. DEFAULT AND ACCELERATION", [
            "If the Borrower fails to make three consecutive monthly payments, the entire",
            "outstanding balance, including accrued interest and fees, shall become immediately",
            "due and payable (acceleration clause). The Lender may pursue all available legal",
            "remedies to recover the outstanding amounts.",
        ]),
        ("8. COLLATERAL", [
            "This is an unsecured personal loan. However, the Borrower agrees that in the event",
            "of default, the Lender may pursue a wage assignment to recover outstanding amounts.",
            "The Borrower authorizes the Lender to contact the Borrower's employer for this purpose.",
        ]),
        ("9. DISPUTE RESOLUTION", [
            "Any disputes arising from this agreement shall be resolved through mandatory binding",
            "arbitration under the rules of the National Arbitration Association. The Borrower",
            "waives the right to participate in class action lawsuits. The arbitration shall be",
            "conducted in the Lender's principal place of business.",
        ]),
        ("10. GOVERNING LAW AND AMENDMENTS", [
            "This agreement shall be governed by the laws of the relevant jurisdiction. The Lender",
            "may amend the terms of this agreement, including the interest rate and fees, subject",
            "to applicable regulations. Amendments may be subject to change as determined by",
            "the Lender's internal policies. Continued use of the loan facility after notification",
            "of changes constitutes acceptance of the amended terms.",
        ]),
        ("11. AUTOMATIC RENEWAL", [
            "Upon maturity, if the outstanding balance has not been fully repaid, this agreement",
            "shall be automatically renewed for an additional 12-month period at the prevailing",
            "interest rate, unless the Borrower provides written notice of non-renewal at least",
            "30 days prior to the maturity date.",
        ]),
        ("12. INSURANCE REQUIREMENT", [
            "The Borrower is required to maintain credit life insurance for the duration of the",
            "loan. The monthly insurance premium of $15.00 shall be added to each monthly payment.",
            "Failure to maintain insurance coverage constitutes a breach of this agreement.",
        ]),
    ]

    for heading, lines in sections2:
        page2.insert_text(fitz.Point(72, y), heading, fontsize=11, fontname="hebo")
        y += 18
        for line in lines:
            page2.insert_text(fitz.Point(72, y), line, fontsize=9, fontname="helv")
            y += 13
        y += 10

    # Page 3: Signature
    page3 = doc.new_page()
    y = 72

    page3.insert_text(fitz.Point(72, y), "DECLARATION AND SIGNATURES", fontsize=14, fontname="hebo")
    y += 30
    page3.insert_text(fitz.Point(72, y), "The Borrower acknowledges that they have read, understood, and agree to all", fontsize=9, fontname="helv")
    y += 14
    page3.insert_text(fitz.Point(72, y), "the terms and conditions set forth in this Personal Loan Agreement.", fontsize=9, fontname="helv")
    y += 30

    page3.insert_text(fitz.Point(72, y), "Borrower: ____________________________    Date: _______________", fontsize=10, fontname="helv")
    y += 25
    page3.insert_text(fitz.Point(72, y), "Lender Representative: ________________    Date: _______________", fontsize=10, fontname="helv")
    y += 40
    page3.insert_text(fitz.Point(72, y), "QuickCash Finance Ltd.", fontsize=10, fontname="hebo")
    y += 15
    page3.insert_text(fitz.Point(72, y), "Licensed Financial Services Provider", fontsize=8, fontname="helv")
    y += 13
    page3.insert_text(fitz.Point(72, y), "Registration No: FSP-2024-1847", fontsize=8, fontname="helv")

    output_path = "../test_data/sample_loan_agreement.pdf"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    print(f"Generated: {output_path}")

    return output_path


if __name__ == "__main__":
    generate_sample_loan_pdf()
    print("Done!")
