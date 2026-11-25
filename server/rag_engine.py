import os
import json
import math

try:
    from google import genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "tax_vector_db.json")

def retrieve_context(query, top_k=4):
    if not os.path.exists(DB_PATH):
        return []
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    docs = data.get("documents", [])
    if not docs:
        return []
        
    query_words = [w.lower() for w in query.split() if len(w) > 2]
    
    scored_docs = []
    for doc in docs:
        score = 0
        doc_text = doc["text"].lower()
        title_text = doc["title"].lower()
        cat_text = doc["category"].lower()
        
        for w in query_words:
            if w in doc_text:
                score += doc_text.count(w)
            if w in title_text:
                score += 5
            if w in cat_text:
                score += 3
        scored_docs.append((score, doc))
        
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_k]]

def query_tax_assistant(user_query, calculation_result=None):
    retrieved_chunks = retrieve_context(user_query, top_k=4)
    
    context_str = "OFFICIAL INCOME TAX DEPARTMENT CLAUSES & TUTORIALS:\n"
    citations = []
    for chunk in retrieved_chunks:
        context_str += f"\n--- [{chunk['title']}] ({chunk['url']}) ---\n{chunk['text']}\n"
        citations.append({
            "title": chunk['title'],
            "url": chunk['url'],
            "category": chunk['category']
        })
        
    calc_str = ""
    if calculation_result:
        new_reg = calculation_result.get("new_regime", {})
        old_reg = calculation_result.get("old_regime", {})
        cg = calculation_result.get("capital_gains", {})
        ftc = calculation_result.get("foreign_tax_credit", {})
        roadmap = calculation_result.get("investment_roadmap", [])
        rec = calculation_result.get("recommended_regime", "New Tax Regime")
        savings = calculation_result.get("savings_amount", 0)
        
        roadmap_summary = ""
        if roadmap:
            roadmap_summary = f"- Recommended Strategy ({roadmap[0]['bracket']}): {roadmap[0]['title']} -> {roadmap[0]['action']}"
        
        calc_str = f"""
USER SALARY, LOANS, CAPITAL GAINS & STRATEGY SUMMARY:
- Gross Salary & Foreign Income: Rs. {new_reg.get('gross_income', 0):,.0f}
- Education Loan Interest Claimed (Sec 80E): Rs. {old_reg.get('education_loan_interest', 0):,.0f}
- EV Loan Interest Claimed (Sec 80EEB): Rs. {old_reg.get('ev_loan_interest', 0):,.0f}
- DTAA Foreign Tax Credit (Form 67): Rs. {ftc.get('dtaa_ftc_claim', 0):,.2f}
- Capital Gains Tax Payable: Rs. {cg.get('total_cg_tax', 0):,.2f}
- Net Tax Payable under New Regime: Rs. {calculation_result.get('final_new_tax', 0):,.2f}
- Net Tax Payable under Old Regime: Rs. {calculation_result.get('final_old_tax', 0):,.2f}
- Recommended Option: {rec} (Saves Rs. {savings:,.2f})
{roadmap_summary}
"""

    prompt = f"""
You are an expert Indian Income Tax Law RAG Assistant.
Answer the user's query clearly and professionally based on official Indian tax regulations, loan deduction provisions, and the calculated figures provided below.

{calc_str}

{context_str}

USER QUESTION:
"{user_query}"

INSTRUCTIONS:
1. Refer directly to official sections (e.g. Section 80E Education Loan unlimited deduction, Section 80EEB EV Loan, Section 80DDB Medical Treatment, Section 115BAC New Regime, Section 80CCD Employer NPS, Section 54/54F/54EC).
2. Suggest actionable wealth-building and tax-saving steps tailored to the user's specific income level.
3. Maintain a structured, professional, and clear tone.
"""

    api_key = os.environ.get("GEMINI_API_KEY")
    ai_response = None

    if api_key and HAS_GENAI_LIB:
        try:
            client = genai.Client(api_key=api_key)
            interaction = client.interactions.create(
                model="gemini-3.7-flash",
                input=prompt,
                system_instruction="You are a senior Indian Income Tax Specialist specializing in loan tax deductions, ESOPs, RSUs, DTAA Form 67, and income-bracket wealth strategies."
            )
            ai_response = interaction.output_text
        except Exception as e:
            print(f"GenAI API notice: {e}")
            
    if not ai_response:
        ai_response = f"""### Indian Income Tax Law & Loan Deductions Guide

Based on official **Income Tax Department** regulations:

#### 1. Loan Tax Deductions
* **Education Loan (Section 80E):** 100% of interest paid on higher education loans (self, spouse, children) is deductible under the Old Tax Regime with **NO UPPER LIMIT** for up to 8 consecutive years.
* **Electric Vehicle Loan (Section 80EEB):** Deduction up to **₹1,50,000** per financial year on EV loan interest.
* **Home Loan Interest (Section 24(b)):** Up to **₹2,00,000** deduction per year on home loan interest for self-occupied property.

#### 2. Specialized Medical & Donation Deductions
* **Medical Treatment of Critical Illnesses (Section 80DDB):** Up to **₹40,000** (₹1,00,000 for senior citizens).
* **Charitable Donations (Section 80G):** 50% or 100% deduction for eligible relief funds.

#### 3. Income-Based Investment & Tax Saving Strategy
* **For Income $\le$ ₹12.75 Lakhs:** Use the New Tax Regime to claim ₹75,000 Standard Deduction + Section 87A rebate for **₹0 Tax**. Focus on high-compounding ELSS / Index funds.
* **For Income ₹12.75L – ₹25 Lakhs:** Reallocate 10% of basic salary to Employer NPS (Section 80CCD(2)) which is tax-free in BOTH regimes. Maximize Section 80C and Section 80CCD(1B) Tier-1 NPS.
* **For Income > ₹25 Lakhs:** Utilize Section 80E unlimited education loan deduction, claim DTAA Foreign Tax Credit (Form 67), and reinvest stock/property gains under Section 54F or Section 54EC Capital Gain Bonds.
"""

    return {
        "response": ai_response,
        "citations": citations
    }

if __name__ == "__main__":
    res = query_tax_assistant("What tax benefits can I claim on an education loan under Section 80E?")
    print(res["response"])
