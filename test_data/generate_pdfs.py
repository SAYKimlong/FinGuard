"""
FinGuard — Synthetic Loan Agreement PDF Generator

Generates synthetic loan agreement PDFs for testing and demonstration.
All documents are clearly marked as synthetic and fictional.

Usage:
    pip install fpdf2
    python test_data/generate_pdfs.py
"""

import os
from fpdf import FPDF
from datetime import date


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_documents")

DISCLAIMER = (
    "SYNTHETIC DOCUMENT -- FOR TESTING AND DEMONSTRATION PURPOSES ONLY. "
    "This document is entirely fictional. No real persons, companies, "
    "or financial products are represented."
)


class LoanPDF(FPDF):
    """Custom FPDF subclass with helpers for loan-agreement formatting."""

    def __init__(self, title: str):
        super().__init__()
        self._doc_title = title
        self.set_auto_page_break(auto=True, margin=25)

    # ------------------------------------------------------------------ #
    #  Header / Footer
    # ------------------------------------------------------------------ #
    def header(self):
        # Disclaimer banner
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(180, 0, 0)
        self.cell(0, 4, DISCLAIMER, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)
        # Title
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, self._doc_title, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", align="C")

    # ------------------------------------------------------------------ #
    #  Convenience writers
    # ------------------------------------------------------------------ #
    def section_heading(self, number: int | str, title: str):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 0, 80)
        self.cell(0, 7, f"Section {number}: {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.set_text_color(0, 0, 0)

    def body_text(self, text: str, bold: bool = False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def key_value(self, key: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.cell(60, 5, f"{key}:")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")

    def add_signature_block(self):
        self.ln(10)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, "AGREED AND ACCEPTED:", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)

        for party in ("Lender", "Borrower"):
            self.cell(80, 5, f"{'_' * 35}")
            self.cell(0, 5, f"{'_' * 35}", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "I", 9)
            self.cell(80, 5, f"Signature ({party})")
            self.cell(0, 5, "Date", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 10)
            self.ln(6)


# ===================================================================== #
#  Document 1 — Standard Personal Loan Agreement
# ===================================================================== #
def generate_standard_loan():
    pdf = LoanPDF("STANDARD PERSONAL LOAN AGREEMENT")
    pdf.alias_nb_pages()
    pdf.add_page()

    today = date.today().strftime("%B %d, %Y")

    pdf.body_text(f"Date: {today}")
    pdf.body_text("Agreement Number: SFC-2024-SYNTH-001")
    pdf.ln(2)

    pdf.key_value("Lender", "Sample Financial Corp (Fictional Entity)")
    pdf.key_value("Borrower", "[SYNTHETIC BORROWER NAME]")
    pdf.key_value("Loan Amount", "$25,000.00")
    pdf.key_value("Annual Interest Rate", "8.5% (Fixed)")
    pdf.key_value("Loan Term", "36 months")
    pdf.key_value("Monthly Payment", "$789.02")
    pdf.key_value("Origination Fee", "1% ($250.00)")
    pdf.key_value("Total Cost of Credit", "$3,404.72")

    # Section 1
    pdf.section_heading(1, "LOAN AMOUNT AND DISBURSEMENT")
    pdf.body_text(
        "The Lender agrees to lend the Borrower the principal sum of Twenty-Five "
        "Thousand Dollars ($25,000.00) (the \"Loan\"). The Loan proceeds shall be "
        "disbursed to the Borrower's designated account within five (5) business "
        "days of the execution of this Agreement, less the origination fee of "
        "$250.00 (1% of the principal)."
    )

    # Section 2
    pdf.section_heading(2, "INTEREST RATE")
    pdf.body_text(
        "The Loan shall bear interest at a fixed annual rate of Eight and One-Half "
        "Percent (8.5%) per annum. Interest shall be calculated on the outstanding "
        "principal balance using the simple interest method (actual/365). The "
        "interest rate shall remain fixed for the entire term of the Loan."
    )

    # Section 3
    pdf.section_heading(3, "REPAYMENT TERMS")
    pdf.body_text(
        "The Borrower shall repay the Loan in thirty-six (36) equal monthly "
        "installments of Seven Hundred Eighty-Nine Dollars and Two Cents ($789.02), "
        "commencing on the first day of the month following disbursement. Payments "
        "shall be applied first to accrued interest and then to principal."
    )

    # Section 4
    pdf.section_heading(4, "LATE PAYMENT")
    pdf.body_text(
        "A payment is considered late if not received within fifteen (15) calendar "
        "days of the due date (the \"Grace Period\"). A late fee of Twenty-Five "
        "Dollars ($25.00) will be assessed for each late payment. No additional "
        "penalties or rate adjustments will apply due to late payment alone."
    )

    # Section 5
    pdf.section_heading(5, "EARLY REPAYMENT")
    pdf.body_text(
        "The Borrower may prepay all or any part of the outstanding principal "
        "balance at any time without penalty. Partial prepayments shall be applied "
        "to principal and shall reduce the remaining balance accordingly. No "
        "prepayment fee or early termination charge shall apply."
    )

    # Section 6
    pdf.section_heading(6, "COLLATERAL")
    pdf.body_text(
        "This Loan is unsecured. No collateral is required from the Borrower. The "
        "Borrower's obligation to repay is based solely on the Borrower's personal "
        "creditworthiness and promise to pay."
    )

    # Section 7
    pdf.section_heading(7, "DEFAULT")
    pdf.body_text(
        "An Event of Default shall occur if: (a) the Borrower fails to make any "
        "payment within thirty (30) days of its due date; (b) the Borrower files "
        "for bankruptcy or becomes insolvent; or (c) any representation made by the "
        "Borrower proves to be materially false. Upon an Event of Default, the "
        "Lender may declare the entire outstanding balance immediately due and "
        "payable after providing written notice and a thirty (30) day cure period."
    )

    # Section 8
    pdf.section_heading(8, "DISPUTE RESOLUTION")
    pdf.body_text(
        "Any disputes arising from this Agreement shall first be subject to good-"
        "faith negotiation between the parties. If negotiation fails, the parties "
        "agree to submit to mediation before pursuing litigation. Each party shall "
        "bear its own costs for mediation. Either party retains the right to "
        "pursue legal remedies in a court of competent jurisdiction."
    )

    # Section 9
    pdf.section_heading(9, "GOVERNING LAW")
    pdf.body_text(
        "This Agreement shall be governed by and construed in accordance with the "
        "laws of the applicable jurisdiction. All terms and conditions herein are "
        "subject to applicable federal and state/provincial consumer protection "
        "statutes and regulations."
    )

    # Section 10
    pdf.section_heading(10, "ENTIRE AGREEMENT")
    pdf.body_text(
        "This Agreement constitutes the entire understanding between the parties "
        "regarding the Loan and supersedes all prior negotiations, representations, "
        "and agreements. Any amendments must be made in writing and signed by both "
        "parties."
    )

    pdf.add_signature_block()

    path = os.path.join(OUTPUT_DIR, "standard_loan_agreement.pdf")
    pdf.output(path)
    print(f"  [OK] {path}")


# ===================================================================== #
#  Document 2 — Multi-Fee Loan (Personal Credit Facility)
# ===================================================================== #
def generate_multi_fee_loan():
    pdf = LoanPDF("PERSONAL CREDIT FACILITY AGREEMENT")
    pdf.alias_nb_pages()
    pdf.add_page()

    today = date.today().strftime("%B %d, %Y")

    pdf.body_text(f"Date: {today}")
    pdf.body_text("Agreement Number: GLP-2024-SYNTH-002")
    pdf.ln(2)

    pdf.key_value("Lender", "Global Lending Partners (Fictional Entity)")
    pdf.key_value("Borrower", "[SYNTHETIC BORROWER NAME]")
    pdf.key_value("Credit Facility Amount", "$15,000.00")
    pdf.key_value("Annual Interest Rate", "14.9% (Fixed)")
    pdf.key_value("Facility Term", "48 months")

    # Section 1
    pdf.section_heading(1, "CREDIT FACILITY AND DISBURSEMENT")
    pdf.body_text(
        "The Lender agrees to extend a personal credit facility of Fifteen "
        "Thousand Dollars ($15,000.00) to the Borrower. The net disbursement "
        "amount shall be reduced by the origination fee and document preparation "
        "fee as described in Section 3."
    )

    # Section 2
    pdf.section_heading(2, "INTEREST RATE")
    pdf.body_text(
        "The Credit Facility shall bear interest at a fixed annual rate of "
        "Fourteen and Nine-Tenths Percent (14.9%) per annum, calculated daily "
        "on the outstanding balance and compounded monthly."
    )

    # Section 3 — The big fee section
    pdf.section_heading(3, "FEES AND CHARGES")

    pdf.body_text("3.1 Origination Fee", bold=True)
    pdf.body_text(
        "An origination fee of Three Percent (3%) of the Credit Facility amount "
        "($450.00) shall be deducted from the disbursed proceeds at the time of "
        "funding."
    )

    pdf.body_text("3.2 Document Preparation Fee", bold=True)
    pdf.body_text(
        "A non-refundable document preparation fee of One Hundred Fifty Dollars "
        "($150.00) shall be charged at closing and deducted from proceeds."
    )

    pdf.body_text("3.3 Monthly Processing Fee", bold=True)
    pdf.body_text(
        "A monthly account processing fee of Nine Dollars and Ninety-Nine Cents "
        "($9.99) shall be added to each monthly statement. This fee covers "
        "account maintenance, statement generation, and payment processing."
    )

    pdf.body_text("3.4 Annual Account Maintenance Fee", bold=True)
    pdf.body_text(
        "An annual account maintenance fee of Seventy-Five Dollars ($75.00) shall "
        "be assessed on each anniversary of the Credit Facility. This fee is "
        "non-refundable and will be added to the outstanding balance if not paid "
        "within thirty (30) days of assessment."
    )

    pdf.body_text("3.5 Credit Life Insurance", bold=True)
    pdf.body_text(
        "The Borrower is required to maintain credit life insurance coverage for "
        "the duration of the Credit Facility. The monthly premium of Twelve "
        "Dollars and Fifty Cents ($12.50) shall be included in the Borrower's "
        "monthly payment. Coverage is provided through a third-party insurer "
        "selected by the Lender."
    )

    # Section 4
    pdf.section_heading(4, "REPAYMENT TERMS")
    pdf.body_text(
        "The Borrower shall make monthly payments sufficient to cover accrued "
        "interest, the monthly processing fee ($9.99), the credit life insurance "
        "premium ($12.50), and a portion of principal over the forty-eight (48) "
        "month term."
    )

    # Section 5
    pdf.section_heading(5, "LATE PAYMENT")
    pdf.body_text(
        "A payment shall be considered late if not received by the due date. "
        "Late charges shall consist of: (a) Five Percent (5%) of the overdue "
        "amount; PLUS (b) a flat administrative fee of Thirty-Five Dollars "
        "($35.00). Late charges will be added to the outstanding balance and "
        "will accrue interest at the applicable rate."
    )

    # Section 6
    pdf.section_heading(6, "EARLY REPAYMENT")
    pdf.body_text(
        "The Borrower may repay the Credit Facility in full prior to the end "
        "of the term, subject to an early repayment fee of Two Percent (2%) of "
        "the remaining outstanding principal balance at the time of prepayment. "
        "Partial prepayments are not permitted unless approved in writing by "
        "the Lender."
    )

    # Section 7
    pdf.section_heading(7, "FEE SUMMARY")
    pdf.body_text(
        "For the avoidance of doubt, the following is a summary of all fees "
        "applicable to this Credit Facility:"
    )
    pdf.body_text(
        "  - Origination Fee: $450.00 (one-time, at closing)\n"
        "  - Document Preparation Fee: $150.00 (one-time, at closing)\n"
        "  - Monthly Processing Fee: $9.99/month ($479.52 over term)\n"
        "  - Annual Maintenance Fee: $75.00/year ($300.00 over term)\n"
        "  - Credit Life Insurance: $12.50/month ($600.00 over term)\n"
        "  - Late Payment: 5% of overdue + $35.00 per occurrence\n"
        "  - Early Repayment: 2% of remaining balance"
    )
    pdf.body_text(
        "Total estimated non-interest costs over the full term (excluding late "
        "fees): $1,979.52."
    )

    # Section 8
    pdf.section_heading(8, "DEFAULT AND REMEDIES")
    pdf.body_text(
        "If the Borrower fails to make any payment within ten (10) days of its "
        "due date, or breaches any term of this Agreement, the Lender may: "
        "(a) declare the entire balance immediately due; (b) report the default "
        "to credit bureaus; (c) pursue collection through all available legal "
        "means; and (d) assess all collection costs to the Borrower's account."
    )

    # Section 9
    pdf.section_heading(9, "GOVERNING LAW")
    pdf.body_text(
        "This Agreement shall be governed by the laws of the applicable "
        "jurisdiction."
    )

    pdf.add_signature_block()

    path = os.path.join(OUTPUT_DIR, "multi_fee_loan.pdf")
    pdf.output(path)
    print(f"  [OK] {path}")


# ===================================================================== #
#  Document 3 — Concerning Terms (Quick Cash Advance)
# ===================================================================== #
def generate_concerning_terms_loan():
    pdf = LoanPDF("QUICK CASH ADVANCE AGREEMENT")
    pdf.alias_nb_pages()
    pdf.add_page()

    today = date.today().strftime("%B %d, %Y")

    pdf.body_text(f"Date: {today}")
    pdf.body_text("Agreement Number: FMS-2024-SYNTH-003")
    pdf.ln(2)

    pdf.key_value("Lender", "FastMoney Services (Fictional Entity)")
    pdf.key_value("Borrower", "[SYNTHETIC BORROWER NAME]")
    pdf.key_value("Advance Amount", "$5,000.00")
    pdf.key_value("Annual Interest Rate", "29.9%")
    pdf.key_value("Term", "24 months")

    # Section 1
    pdf.section_heading(1, "CASH ADVANCE")
    pdf.body_text(
        "The Lender shall provide a cash advance of Five Thousand Dollars "
        "($5,000.00) to the Borrower. By accepting the advance, the Borrower "
        "agrees to ALL terms and conditions contained herein without reservation."
    )

    # Section 2
    pdf.section_heading(2, "INTEREST RATE AND DEFAULT RATE")
    pdf.body_text(
        "The Advance shall bear interest at an annual rate of Twenty-Nine and "
        "Nine-Tenths Percent (29.9%), compounded monthly. In the event the "
        "Borrower is more than thirty (30) days late on any payment, the interest "
        "rate shall automatically increase to Thirty-Nine and Nine-Tenths Percent "
        "(39.9%) per annum (the \"Default Rate\"). The Default Rate shall apply "
        "to the ENTIRE outstanding balance from the date of default and shall "
        "remain in effect for the remainder of the term, even if the Borrower "
        "subsequently cures the default."
    )

    # Section 3
    pdf.section_heading(3, "LATE PAYMENT PENALTIES")
    pdf.body_text(
        "If any payment is not received on or before the due date, a late fee "
        "of Ten Percent (10%) of the overdue amount shall be assessed. Late fees "
        "shall compound monthly — that is, unpaid late fees shall themselves "
        "accrue additional late fees at the same rate. There is no grace period."
    )

    # Section 4
    pdf.section_heading(4, "ACCELERATION CLAUSE")
    pdf.body_text(
        "Upon ANY missed or late payment, the Lender reserves the right, at its "
        "sole discretion, to declare the ENTIRE outstanding balance — including "
        "all accrued interest, fees, and penalties — immediately due and payable. "
        "The Borrower waives any right to notice or cure period prior to "
        "acceleration."
    )

    # Section 5
    pdf.section_heading(5, "WAGE ASSIGNMENT")
    pdf.body_text(
        "The Borrower hereby irrevocably assigns to the Lender the right to "
        "collect payment directly from the Borrower's wages, salary, commissions, "
        "or other compensation. The Borrower authorizes the Lender to direct the "
        "Borrower's employer to remit payment directly to the Lender in the event "
        "of any default. This assignment shall survive termination of this "
        "Agreement until all amounts owed are paid in full."
    )

    # Section 6
    pdf.section_heading(6, "MANDATORY ARBITRATION")
    pdf.body_text(
        "ANY and ALL disputes arising from or related to this Agreement shall be "
        "resolved exclusively through binding arbitration. The Borrower waives the "
        "right to participate in any class action or collective proceeding. The "
        "Borrower shall bear ALL costs of arbitration, including the Lender's "
        "legal fees and the arbitrator's fees, regardless of the outcome. The "
        "arbitrator shall be selected solely by the Lender. The arbitration shall "
        "take place at a location chosen by the Lender."
    )

    # Section 7
    pdf.section_heading(7, "EARLY REPAYMENT RESTRICTIONS")
    pdf.body_text(
        "The Borrower may NOT repay the Advance in full or in part during the "
        "first twelve (12) months of the term (the \"Lock-In Period\"). After the "
        "Lock-In Period, the Borrower may prepay the full balance subject to an "
        "early repayment fee of Five Percent (5%) of the ORIGINAL principal "
        "amount ($250.00), regardless of the remaining balance at the time of "
        "prepayment. Partial prepayments are not permitted at any time."
    )

    # Section 8
    pdf.section_heading(8, "AUTO-RENEWAL")
    pdf.body_text(
        "This Agreement shall automatically renew for successive twelve (12) "
        "month periods at the then-applicable interest rate unless the Borrower "
        "provides written notice of non-renewal at least sixty (60) days prior "
        "to the expiration of the current term. Upon auto-renewal, a renewal "
        "fee of Three Percent (3%) of the outstanding balance shall be assessed. "
        "The Lender is not required to provide notice of the upcoming renewal."
    )

    # Section 9
    pdf.section_heading(9, "WAIVER OF RIGHTS")
    pdf.body_text(
        "By executing this Agreement, the Borrower waives: (a) the right to "
        "receive periodic account statements unless specifically requested in "
        "writing; (b) the right to assert any counterclaim against the Lender "
        "in any proceeding; (c) the right to a jury trial; and (d) any rights "
        "under consumer protection statutes to the fullest extent permitted by "
        "law."
    )

    # Section 10
    pdf.section_heading(10, "COLLECTION AND RECOVERY")
    pdf.body_text(
        "In the event of default, the Borrower shall be liable for ALL costs "
        "of collection, including attorney's fees, court costs, skip-tracing "
        "fees, and any other expenses incurred by the Lender. Interest shall "
        "continue to accrue at the Default Rate on all amounts owed until "
        "payment in full."
    )

    # Section 11
    pdf.section_heading(11, "GOVERNING LAW")
    pdf.body_text(
        "This Agreement shall be governed by the laws of the jurisdiction most "
        "favorable to the Lender's interests, as determined by the Lender."
    )

    pdf.add_signature_block()

    path = os.path.join(OUTPUT_DIR, "concerning_terms_loan.pdf")
    pdf.output(path)
    print(f"  [OK] {path}")


# ===================================================================== #
#  Document 4 — Ambiguous Terms (Flexible Financing Arrangement)
# ===================================================================== #
def generate_ambiguous_terms_loan():
    pdf = LoanPDF("FLEXIBLE FINANCING ARRANGEMENT")
    pdf.alias_nb_pages()
    pdf.add_page()

    today = date.today().strftime("%B %d, %Y")

    pdf.body_text(f"Date: {today}")
    pdf.body_text("Agreement Number: HCG-2024-SYNTH-004")
    pdf.ln(2)

    pdf.key_value("Lender", "Horizon Capital Group (Fictional Entity)")
    pdf.key_value("Borrower", "[SYNTHETIC BORROWER NAME]")
    pdf.key_value("Financing Amount", "$10,000.00")
    pdf.key_value("Interest Rate", "Variable (see Section 2)")
    pdf.key_value("Term", "As determined per the Arrangement")

    # Section 1
    pdf.section_heading(1, "FINANCING ARRANGEMENT")
    pdf.body_text(
        "The Lender agrees to provide the Borrower with financing in the amount "
        "of Ten Thousand Dollars ($10,000.00), subject to the terms and conditions "
        "set forth herein. The specific terms of disbursement, repayment, and "
        "associated costs may be adjusted from time to time at the Lender's "
        "discretion to reflect changing market conditions and the Borrower's "
        "account standing."
    )

    # Section 2
    pdf.section_heading(2, "INTEREST RATE")
    pdf.body_text(
        "The Financing Arrangement shall bear interest at a variable rate, "
        "adjusted periodically based on market conditions and the Lender's "
        "internal assessment of risk. The initial rate will be communicated to "
        "the Borrower at the time of first disbursement. Rate adjustments may "
        "occur at intervals determined by the Lender. No specific rate cap or "
        "floor is guaranteed under this Arrangement."
    )
    pdf.body_text(
        "The method of interest calculation (simple, compound, or otherwise) "
        "shall be as determined by the Lender and may be subject to change "
        "with reasonable notice."
    )

    # Section 3
    pdf.section_heading(3, "FEES")
    pdf.body_text(
        "Administrative fees may apply to this Financing Arrangement. The "
        "specific nature and amount of such fees will be determined in accordance "
        "with the Lender's fee schedule, which is subject to periodic revision. "
        "The Borrower acknowledges that fees not explicitly listed in this "
        "Agreement may nonetheless be applicable as determined by the Lender."
    )
    pdf.body_text(
        "Additional service charges may be assessed for account inquiries, "
        "statement requests, payment processing, or other activities as the "
        "Lender deems appropriate."
    )

    # Section 4
    pdf.section_heading(4, "REPAYMENT")
    pdf.body_text(
        "The Borrower shall make periodic payments in amounts and at intervals "
        "communicated by the Lender. The payment schedule may be modified from "
        "time to time to reflect changes in the interest rate, fees, or other "
        "factors at the Lender's discretion. The Lender will make reasonable "
        "efforts to notify the Borrower of material changes to the payment "
        "schedule."
    )

    # Section 5
    pdf.section_heading(5, "LATE PAYMENT")
    pdf.body_text(
        "Penalties will be assessed for late payments per the Lender's current "
        "penalty schedule. The penalty schedule is maintained internally by the "
        "Lender and may be updated periodically. The Borrower may request a "
        "copy of the current penalty schedule at any time, subject to an "
        "administrative processing fee."
    )

    # Section 6
    pdf.section_heading(6, "EARLY REPAYMENT")
    pdf.body_text(
        "Early repayment of the Financing Arrangement is subject to the terms "
        "and conditions in effect at the time of prepayment. Prepayment fees, "
        "if any, will be calculated based on the Lender's then-current policies. "
        "The Borrower is advised to contact the Lender prior to making any "
        "prepayment to obtain the applicable terms."
    )

    # Section 7
    pdf.section_heading(7, "MODIFICATIONS AND AMENDMENTS")
    pdf.body_text(
        "The Lender reserves the right to modify any term or condition of this "
        "Arrangement at its discretion, including but not limited to the interest "
        "rate, fees, payment schedule, and default provisions. The Lender will "
        "provide notice of material changes, though the definition of 'material' "
        "shall be at the Lender's sole discretion. Continued use of the financing "
        "after any change constitutes acceptance of the modified terms."
    )

    # Section 8
    pdf.section_heading(8, "DEFAULT")
    pdf.body_text(
        "The Lender may, at its sole discretion, determine that an Event of "
        "Default has occurred. Events that may constitute default include, but "
        "are not limited to, late payments, changes in the Borrower's financial "
        "circumstances, or other factors as determined by the Lender. Upon "
        "default, the Lender may exercise such remedies as it deems appropriate."
    )

    # Section 9
    pdf.section_heading(9, "COMMUNICATIONS")
    pdf.body_text(
        "The Lender may communicate with the Borrower through such channels as "
        "the Lender selects, including mail, email, telephone, or other methods. "
        "Notices shall be deemed received within a reasonable time after sending, "
        "as determined by the Lender."
    )

    # Section 10
    pdf.section_heading(10, "GENERAL PROVISIONS")
    pdf.body_text(
        "This Arrangement is subject to such additional terms and conditions as "
        "the Lender may establish from time to time. Where this Agreement is "
        "silent on any matter, the Lender's standard policies and procedures "
        "shall govern. The Borrower acknowledges that certain aspects of this "
        "Arrangement may be subject to change and agrees to be bound by the "
        "terms as they may exist at any given time."
    )

    # Section 11
    pdf.section_heading(11, "GOVERNING LAW")
    pdf.body_text(
        "This Arrangement shall be governed by the laws of such jurisdiction as "
        "the Lender may determine is applicable."
    )

    pdf.add_signature_block()

    path = os.path.join(OUTPUT_DIR, "ambiguous_terms_loan.pdf")
    pdf.output(path)
    print(f"  [OK] {path}")


# ===================================================================== #
#  Main
# ===================================================================== #
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating synthetic loan agreement PDFs ...\n")

    generate_standard_loan()
    generate_multi_fee_loan()
    generate_concerning_terms_loan()
    generate_ambiguous_terms_loan()

    print("\nDone. All PDFs written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
