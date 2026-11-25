# TaxVeda Pro — Indian Tax Law RAG & Optimization Assistant

A Flask + vanilla JS web application that compares India's **New Tax Regime (Section 115BAC)** vs. **Old Tax Regime** (FY 2025-26 & FY 2026-27) using a deterministic tax calculator paired with a Gemini-powered RAG assistant.

## Features

- **Deterministic Regime Comparison (`server/tax_calculator.py`):**
  - New vs. Old Tax Regime slab computation, Standard Deduction (₹75,000 New / ₹50,000 Old), Section 87A rebate, marginal relief, and 4% Health & Education Cess.
  - Deductions & exemptions: HRA, LTA, Section 80C, 80D, 80CCD(1B), Employer NPS (80CCD(2)), Home Loan Interest (24(b)), Education Loan Interest (80E), EV Loan Interest (80EEB), Medical Treatment (80DDB), and Donations (80G).
  - **ESOPs/RSUs, Foreign Income & DTAA:** Foreign Tax Credit (Section 90 / Form 67) estimation.
  - **Capital Gains:** Equity STCG/LTCG (Sections 111A/112A), Property LTCG, loss set-off, and Section 54 / 54F / 54EC exemptions.
  - **Actionable Recommendations & Investment Roadmap:** Income-bracket-tailored tax-saving strategies.
- **RAG Tax Assistant (`server/rag_engine.py`):**
  - Retrieves relevant clauses from the local tax knowledge base (`server/db/tax_vector_db.json`) and generates answers via `gemini-3.7-flash` (`google-genai` SDK) when `GEMINI_API_KEY` is configured (with a built-in fallback guide when running offline without an API key).
- **Interactive Web UI (`public/`):**
  - Tabbed configurator for Salary, Loans, Foreign/RSU, and Capital Gains plus an integrated chat assistant with official citations.

## Project Structure

```text
.
├── public/                 # Static frontend (HTML, CSS, JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── server/
│   ├── app.py              # Flask server & REST API endpoints
│   ├── tax_calculator.py   # Deterministic Indian tax & capital gains engine
│   ├── rag_engine.py       # Context retrieval & Gemini 3.7 Flash integration
│   ├── ingest.py           # Knowledge base builder (tax_vector_db.json)
│   ├── db/
│   │   └── tax_vector_db.json
│   └── tests/
│       └── test_api.py     # Unit tests for calculator & strategy engine
├── .env.example
├── .gitignore
└── requirements.txt
```

## Quick Start

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables (optional):**
   ```bash
   cp .env.example .env
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```
   > **Note:** If `GEMINI_API_KEY` is not set, tax calculations still run deterministically and the RAG assistant returns an offline summary guide.

4. **Run the server:**
   ```bash
   python3 server/app.py
   ```
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Refreshing the Knowledge Base

To rebuild `server/db/tax_vector_db.json` from the official tax rules defined in `server/ingest.py`:

```bash
python3 server/ingest.py
```

## Running Tests

```bash
python3 -m unittest discover -s server/tests -p "test_*.py"
```

## API Endpoints

- `POST /api/calculate` — Compute New vs. Old regime taxes, capital gains, DTAA credit, and investment roadmap.
- `POST /api/rag/query` — Query the tax assistant with optional user profile context.
- `POST /api/ingest` — Rebuild `server/db/tax_vector_db.json`.

## Disclaimer

This tool is for educational and estimation purposes only and does not constitute professional tax, legal, or financial advice. Consult a qualified Chartered Accountant (CA) before filing your Income Tax Return.
