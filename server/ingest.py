import os
import json
from datetime import date

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "db", "tax_vector_db.json")

OFFICIAL_SOURCES = [
    {
        "title": "Income Tax Department - New Tax Regime vs Old Tax Regime & Tax Rates",
        "url": "https://www.incometaxindia.gov.in/Pages/charts-and-tables.aspx",
        "category": "Tax Slabs & Regimes",
        "content": """
OFFICIAL INCOME TAX DEPARTMENT GUIDE: TAX RATES & REGIMES (FY 2025-26 & FY 2026-27)
1. Default Tax Regime: The New Tax Regime under Section 115BAC is the default tax regime for all individual taxpayers.
2. New Tax Regime Slabs (FY 2025-26 & FY 2026-27):
   - Up to Rs. 4,00,000: NIL
   - Rs. 4,00,001 to Rs. 8,00,000: 5%
   - Rs. 8,00,001 to Rs. 12,00,000: 10%
   - Rs. 12,00,001 to Rs. 16,00,000: 15%
   - Rs. 16,00,001 to Rs. 20,00,000: 20%
   - Rs. 20,00,001 to Rs. 24,00,000: 25%
   - Above Rs. 24,00,000: 30%
3. Standard Deduction:
   - New Tax Regime: Rs. 75,000 for salaried employees.
   - Old Tax Regime: Rs. 50,000 for salaried employees.
4. Section 87A Rebate:
   - New Tax Regime: Taxable income up to Rs. 12,00,000 gets a 100% tax rebate (max Rs. 60,000). Effective tax is ZERO for gross salary up to Rs. 12.75 Lakhs.
        """
    },
    {
        "title": "Income Tax Department Guide - Loan Interest Deductions (Section 80E, 80EEB, 24(b))",
        "url": "https://www.incometaxindia.gov.in/tutorials/loan-tax-deductions.pdf",
        "category": "Loan Deductions",
        "content": """
OFFICIAL GUIDE: TAX DEDUCTIONS ON LOANS UNDER THE INCOME TAX ACT
1. Section 80E - Interest on Education Loan for Higher Studies:
   - Deduction is allowed for total interest paid on a loan taken for higher education of self, spouse, children, or a student for whom the individual is a legal guardian.
   - NO MAXIMUM UPPER LIMIT on the interest amount deductible!
   - Deduction is available for up to 8 consecutive assessment years starting from the year you start paying interest.

2. Section 80EEB - Interest on Electric Vehicle (EV) Loan:
   - Deduction up to Rs. 1,50,000 per financial year on interest paid for loan taken to purchase an Electric Vehicle.
   - Loan must be sanctioned by a financial institution.

3. Section 24(b) - Home Loan Interest:
   - Deduction up to Rs. 2,00,000 per year on home loan interest for self-occupied residential property.
        """
    },
    {
        "title": "Income Tax Department Guide - Special Medical Deductions (Section 80DDB, 80DD, 80U) & Donations (80G)",
        "url": "https://www.incometaxindia.gov.in/tutorials/medical-deductions-80ddb-80g.pdf",
        "category": "Medical & Donations",
        "content": """
OFFICIAL GUIDE: DEDUCTIONS FOR MEDICAL TREATMENT & DONATIONS
1. Section 80DDB - Medical Treatment of Specified Critical Illnesses:
   - Deduction for medical treatment of specified diseases (neurological disorders, cancer, full-blown AIDS, chronic renal failure).
   - Maximum deduction: Rs. 40,000 (increases to Rs. 1,00,000 if the patient is a Senior Citizen aged 60+).

2. Section 80DD / Section 80U - Maintenance / Self Disability:
   - Flat deduction of Rs. 75,000 for disability (40% or more), or Rs. 1,25,000 for severe disability (80% or more).

3. Section 80G - Charitable Donations:
   - 50% or 100% deduction for donations made to specified relief funds and charitable institutions. Cash donations allowed only up to Rs. 2,000.
        """
    },
    {
        "title": "Income Tax Department Guide - ESOP & RSU Taxation (Section 17(2) & Section 192(1C))",
        "url": "https://www.incometaxindia.gov.in/tutorials/esop-rsu-taxation.pdf",
        "category": "ESOPs & RSUs",
        "content": """
OFFICIAL GUIDE: TAXATION OF ESOPs AND RSUs IN INDIA
ESOPs (Employee Stock Option Plans) and RSUs (Restricted Stock Units) are taxed at two distinct stages:

1. STAGE 1: AT VESTING / EXERCISE (Perquisite Tax under Section 17(2))
   - Perquisite Value = (Fair Market Value of share on allotment date - Exercise Price paid by employee) * Number of shares.
   - Added directly to Gross Salary income and taxed at your applicable slab rate.
   - TDS: Employer is required to deduct TDS on this perquisite value.
   - Startup Deferral under Section 192(1C): Eligible DPIIT-recognized startups can defer TDS payment on ESOP perquisites to 48 months from exercise, or when employee leaves the company, or sells shares (whichever is earliest).

2. STAGE 2: AT SALE / CAPITAL GAINS (Section 45)
   - Capital Gain = (Sale Price - Fair Market Value on allotment date).
   - Cost of Acquisition is the FMV used at vesting.
   - Foreign RSUs (e.g. US stock like Google, Apple, Meta): Treated as unlisted securities. Short-Term Capital Gains (holding <= 24 months) taxed at slab rate. Long-Term Capital Gains (holding > 24 months) taxed at 12.5%.
        """
    },
    {
        "title": "Income Tax Department Guide - Foreign Income, DTAA Relief (Section 90) & Form 67",
        "url": "https://www.incometaxindia.gov.in/tutorials/dtaa-form-67.pdf",
        "category": "Foreign Income",
        "content": """
OFFICIAL GUIDE: FOREIGN INCOME, DTAA RELIEF (SECTION 90) & FORM 67
1. Double Taxation Avoidance Agreement (DTAA) - Section 90 / 90A:
   - Resident taxpayers earning foreign income (e.g. US salary, dividends, RSU sale) that was taxed in a foreign country can claim Foreign Tax Credit (FTC) in India to prevent double taxation.
   - Credit Amount = Lower of (Foreign Tax Paid) or (Indian Tax payable attributable to foreign income).

2. Mandatory Filing of Form 67:
   - To claim Foreign Tax Credit under Section 90, the taxpayer MUST file Form 67 online on the Income Tax e-Filing portal on or before the due date of filing ITR under Section 139(1).
   - Proof of foreign tax paid (W-2 form, Tax return copy, or Tax withholding certificate) must be attached.

3. Schedule FA (Foreign Assets Disclosure):
   - Every ordinary resident of India who holds foreign shares (RSUs/ESOPs), foreign bank accounts, or foreign immovable property MUST mandatorily disclose them in Schedule FA of ITR-2 or ITR-3. Failure to disclose attracts heavy penalties under the Black Money Act.
        """
    },
    {
        "title": "Income Tax Department Guide - Capital Gains & Tax Loss Harvesting (Sections 45, 111A, 112A, 70-74)",
        "url": "https://www.incometaxindia.gov.in/tutorials/capital-gains-tax-loss-harvesting.pdf",
        "category": "Capital Gains",
        "content": """
OFFICIAL GUIDE: CAPITAL GAINS TAX RATES & LOSS SET-OFF RULES (FINANCE ACT 2024)
1. Equity & Mutual Funds Tax Rates:
   - Short-Term Capital Gains (STCG - Section 111A, holding <= 12 months): Taxed at 20%.
   - Long-Term Capital Gains (LTCG - Section 112A, holding > 12 months): Taxed at 12.5% on aggregate gains exceeding Rs. 1,25,000 exemption limit per financial year.

2. Real Estate & Unlisted Assets Tax Rates:
   - Long-Term Capital Gains (LTCG - Section 112, holding > 24 months): Taxed at 12.5% without indexation.

3. Tax Loss Harvesting & Set-Off Rules (Sections 70 to 74):
   - Short-Term Capital Loss (STCL) can be set off against BOTH STCG and LTCG.
   - Long-Term Capital Loss (LTCL) can be set off ONLY against LTCG.
   - Unadjusted capital losses can be carried forward for up to 8 Assessment Years to set off against future capital gains, provided return is filed on time.
        """
    },
    {
        "title": "Income Tax Department Guide - Property Capital Gains Exemptions (Sections 54, 54F & 54EC)",
        "url": "https://www.incometaxindia.gov.in/tutorials/capital-gains-exemptions-54-54f.pdf",
        "category": "Capital Gains Exemptions",
        "content": """
OFFICIAL GUIDE: CAPITAL GAINS EXEMPTIONS UNDER SECTIONS 54, 54F & 54EC
1. Section 54 Exemption (Sale of Residential House Property):
   - Reinvest LTCG from sale of a residential house into purchasing another residential house (within 1 year before or 2 years after sale, or constructing within 3 years).
   - Maximum cap: Rs. 10 Crores.

2. Section 54F Exemption (Sale of Non-Residential Assets like RSUs, Shares, Gold):
   - Exemption on LTCG from any long-term asset (other than a house property) if Net Consideration is invested in purchasing/constructing one residential house.
   - Exemption Formula = LTCG * (Amount Invested in House / Net Consideration).

3. Section 54EC Exemption (Capital Gain Bonds):
   - Reinvest LTCG from sale of land/building into specified 54EC Capital Gain Bonds issued by NHAI, REC, PFC, or IRFC.
   - Reinvestment must be made within 6 months of sale.
   - Maximum investment limit: Rs. 50,00,000 per financial year. 5-year lock-in period.
        """
    }
]


def chunk_text(text, max_words=150):
    paragraphs = text.strip().split('\n\n')
    chunks = []
    current_chunk = []
    current_count = 0

    for p in paragraphs:
        p_str = p.strip()
        if not p_str:
            continue
        words = len(p_str.split())
        if current_count + words > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p_str]
            current_count = words
        else:
            current_chunk.append(p_str)
            current_count += words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks


def ingest_official_docs(output_db_path=DEFAULT_DB_PATH):
    os.makedirs(os.path.dirname(os.path.abspath(output_db_path)), exist_ok=True)
    print("Ingesting official tax corpus (Slabs, Loans, Medical, ESOPs, DTAA, Capital Gains, Sec 54)...")

    documents = []
    for source in OFFICIAL_SOURCES:
        content_text = source["content"]
        chunks = chunk_text(content_text)
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{source['category']}_{len(documents)+1}",
                "title": source["title"],
                "url": source["url"],
                "category": source["category"],
                "chunk_index": i,
                "text": chunk
            })

    api_key = os.environ.get("GEMINI_API_KEY")
    embeddings_generated = False

    if api_key and HAS_GENAI:
        try:
            print("Generating vector embeddings using Gemini API (text-embedding-004)...")
            client = genai.Client(api_key=api_key)
            for doc in documents:
                res = client.models.embed_content(
                    model="text-embedding-004",
                    contents=doc["text"]
                )
                doc["embedding"] = res.embedding.values
            embeddings_generated = True
            print("Vector embeddings generated successfully!")
        except Exception as e:
            print(f"GenAI embedding notice: {e}")

    if not embeddings_generated:
        for doc in documents:
            words = [w.lower() for w in doc["text"].split() if len(w) > 2]
            doc["word_freq"] = {}
            for w in words:
                doc["word_freq"][w] = doc["word_freq"].get(w, 0) + 1

    with open(output_db_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": date.today().isoformat(),
            "has_embeddings": embeddings_generated,
            "documents": documents
        }, f, indent=2)

    print(f"Ingestion complete! Saved {len(documents)} document chunks to {output_db_path}")


if __name__ == "__main__":
    ingest_official_docs()
