# FinGuard Test Data

> ⚠️ **All documents and data in this directory are entirely synthetic and fictional.**
> They are created solely for testing, development, and demonstration purposes.

## Contents

### Synthetic Documents (`synthetic_documents/`)

| File | Description |
|------|-------------|
| `standard_loan_agreement.pdf` | A straightforward personal loan with clear, fair terms |
| `multi_fee_loan.pdf` | A loan with many fees (processing, maintenance, insurance, etc.) |
| `concerning_terms_loan.pdf` | A predatory-style loan with high rates and aggressive clauses |
| `ambiguous_terms_loan.pdf` | A loan riddled with vague, undefined terms |
| `khmer_loan_sample.txt` | Synthetic Khmer-language loan clauses for OCR/extraction testing |

### Synthetic User Profiles (`synthetic_profiles/`)

| File | Description |
|------|-------------|
| `stable_income_user.json` | A user with stable full-time income and manageable debt |
| `high_debt_user.json` | A user with variable income, high existing debt, and dependents |

## Generating PDFs

The PDF documents are generated programmatically using `fpdf2`:

```bash
pip install fpdf2
python test_data/generate_pdfs.py
```

This will create (or overwrite) the four English PDF files in `synthetic_documents/`.

## Disclaimer

- **No real persons, companies, or financial products are represented.**
- All lender names (Sample Financial Corp, Global Lending Partners, FastMoney Services, Horizon Capital Group) are fictional.
- All monetary amounts, interest rates, and terms are fabricated for testing scenarios.
- These documents should **never** be used as actual financial agreements.
