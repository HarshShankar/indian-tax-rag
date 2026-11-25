import math

def calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro=True):
    if rent_paid <= 0 or hra_received <= 0:
        return 0.0
    rent_minus_10_percent = max(0.0, rent_paid - (0.10 * basic_salary))
    metro_percent = 0.50 if is_metro else 0.40
    basic_limit = metro_percent * basic_salary
    return max(0.0, min(hra_received, rent_minus_10_percent, basic_limit))

def calculate_capital_gains_tax(stcg_equity=0, ltcg_equity=0, ltcg_property=0, 
                                sec54_reinvestment=0, sec54f_reinvestment=0, sec54ec_bonds=0,
                                stcl_available=0, ltcl_available=0):
    net_stcg_equity = max(0.0, stcg_equity - stcl_available)
    rem_stcl = max(0.0, stcl_available - stcg_equity)
    
    total_ltcg_raw = ltcg_equity + ltcg_property
    net_ltcg_raw = max(0.0, total_ltcg_raw - ltcl_available - rem_stcl)
    
    claim_54ec = min(sec54ec_bonds, 5000000.0)
    taxable_property_ltcg = max(0.0, ltcg_property - sec54_reinvestment - sec54f_reinvestment - claim_54ec)
    exemptions_claimed = min(ltcg_property, sec54_reinvestment + sec54f_reinvestment + claim_54ec)
    
    taxable_equity_ltcg = max(0.0, ltcg_equity - 125000.0)
    equity_ltcg_exemption = min(ltcg_equity, 125000.0)
    
    tax_stcg = net_stcg_equity * 0.20
    tax_ltcg_equity = taxable_equity_ltcg * 0.125
    tax_ltcg_property = taxable_property_ltcg * 0.125
    
    total_cg_tax_before_cess = tax_stcg + tax_ltcg_equity + tax_ltcg_property
    cg_cess = total_cg_tax_before_cess * 0.04
    total_cg_tax = total_cg_tax_before_cess + cg_cess
    
    return {
        "stcg_equity": stcg_equity,
        "ltcg_equity": ltcg_equity,
        "ltcg_property": ltcg_property,
        "net_stcg_equity": net_stcg_equity,
        "taxable_equity_ltcg": taxable_equity_ltcg,
        "equity_ltcg_exemption": equity_ltcg_exemption,
        "taxable_property_ltcg": taxable_property_ltcg,
        "exemptions_claimed_54_54f_54ec": exemptions_claimed,
        "tax_stcg": tax_stcg,
        "tax_ltcg_equity": tax_ltcg_equity,
        "tax_ltcg_property": tax_ltcg_property,
        "total_cg_tax_before_cess": total_cg_tax_before_cess,
        "cg_cess": cg_cess,
        "total_cg_tax": total_cg_tax
    }

def calculate_new_regime_tax(gross_income, employer_nps=0):
    std_deduction = 75000.0
    total_deductions = std_deduction + employer_nps
    taxable_income = max(0.0, gross_income - total_deductions)
    
    tax = 0.0
    if taxable_income > 400000:
        tax += min(taxable_income - 400000, 400000) * 0.05
    if taxable_income > 800000:
        tax += min(taxable_income - 800000, 400000) * 0.10
    if taxable_income > 1200000:
        tax += min(taxable_income - 1200000, 400000) * 0.15
    if taxable_income > 1600000:
        tax += min(taxable_income - 1600000, 400000) * 0.20
    if taxable_income > 2000000:
        tax += min(taxable_income - 2000000, 400000) * 0.25
    if taxable_income > 2400000:
        tax += (taxable_income - 2400000) * 0.30
        
    raw_tax = tax
    rebate_87a = 0.0
    marginal_relief = 0.0
    
    if taxable_income <= 1200000:
        rebate_87a = tax
        tax = 0.0
    else:
        excess_income = taxable_income - 1200000
        if tax > excess_income:
            marginal_relief = tax - excess_income
            tax = excess_income
            
    cess = tax * 0.04
    total_tax = tax + cess
    
    return {
        "regime": "New Tax Regime (FY 2025-26 / 2026-27)",
        "gross_income": gross_income,
        "standard_deduction": std_deduction,
        "employer_nps": employer_nps,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "raw_tax": raw_tax,
        "rebate_87a": rebate_87a,
        "marginal_relief": marginal_relief,
        "tax_before_cess": tax,
        "cess": cess,
        "total_tax": total_tax
    }

def calculate_old_regime_tax(basic_salary, gross_income, hra_received, rent_paid, is_metro,
                             sec_80c, sec_80d, sec_80ccd_1b, employer_nps, home_loan_interest,
                             lta, prof_tax, education_loan_interest=0, ev_loan_interest=0,
                             medical_treatment_80ddb=0, donations_80g=0):
    """
    Calculates Old Tax Regime including Loan Interest Deductions:
    - Section 80E: Education Loan Interest (No Limit)
    - Section 80EEB: EV Loan Interest (Max Rs. 1,50,000)
    - Section 80DDB: Specified Medical Treatment (Max Rs. 40,000 / 1,00,000)
    - Section 80G: Charitable Donations
    """
    std_deduction = 50000.0
    hra_exemption = calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro)
    lta_exemption = min(lta, gross_income)
    
    claim_80c = min(sec_80c, 150000.0)
    claim_80d = min(sec_80d, 75000.0)
    claim_80ccd_1b = min(sec_80ccd_1b, 50000.0)
    claim_employer_nps = min(employer_nps, 0.10 * basic_salary)
    claim_home_loan = min(home_loan_interest, 200000.0)
    claim_prof_tax = min(prof_tax, 2500.0)
    
    # Loan Deductions & Special Exemptions
    claim_edu_loan = max(0.0, float(education_loan_interest)) # Unlimited under 80E
    claim_ev_loan = min(float(ev_loan_interest), 150000.0) # Capped at 1.5L under 80EEB
    claim_80ddb = min(float(medical_treatment_80ddb), 100000.0) # Up to 1L
    claim_80g = max(0.0, float(donations_80g))
    
    exemptions = hra_exemption + lta_exemption + std_deduction + claim_prof_tax
    chapter_6a_deductions = (claim_80c + claim_80d + claim_80ccd_1b + claim_employer_nps + 
                             claim_home_loan + claim_edu_loan + claim_ev_loan + claim_80ddb + claim_80g)
    
    total_deductions = exemptions + chapter_6a_deductions
    taxable_income = max(0.0, gross_income - total_deductions)
    
    raw_tax = 0.0
    if taxable_income > 250000:
        raw_tax += min(taxable_income - 250000, 250000) * 0.05
    if taxable_income > 500000:
        raw_tax += min(taxable_income - 500000, 500000) * 0.20
    if taxable_income > 1000000:
        raw_tax += (taxable_income - 1000000) * 0.30
        
    tax = raw_tax
    rebate_87a = 0.0
    if taxable_income <= 500000:
        rebate_87a = min(tax, 12500.0)
        tax = max(0.0, tax - rebate_87a)
        
    cess = tax * 0.04
    total_tax = tax + cess
    
    return {
        "regime": "Old Tax Regime",
        "gross_income": gross_income,
        "standard_deduction": std_deduction,
        "hra_exemption": hra_exemption,
        "lta_exemption": lta_exemption,
        "claim_80c": claim_80c,
        "claim_80d": claim_80d,
        "claim_80ccd_1b": claim_80ccd_1b,
        "employer_nps": claim_employer_nps,
        "home_loan_interest": claim_home_loan,
        "education_loan_interest": claim_edu_loan,
        "ev_loan_interest": claim_ev_loan,
        "medical_treatment_80ddb": claim_80ddb,
        "donations_80g": claim_80g,
        "prof_tax": claim_prof_tax,
        "total_exemptions": exemptions,
        "total_chapter_6a": chapter_6a_deductions,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "raw_tax": raw_tax,
        "rebate_87a": rebate_87a,
        "tax_before_cess": tax,
        "cess": cess,
        "total_tax": total_tax
    }

def generate_income_based_investment_roadmap(total_gross_income, profile):
    """
    Generates tailored, income-bracket specific wealth building and tax reduction strategies.
    """
    basic_salary = float(profile.get("basic_salary", total_gross_income * 0.50))
    roadmap = []
    
    if total_gross_income <= 1275000:
        roadmap.append({
            "bracket": "Under ₹12.75 Lakhs (Tax-Free Zone)",
            "title": "Achieve 100% Tax-Free Income under New Tax Regime",
            "action": "Choose New Tax Regime to claim ₹75,000 Standard Deduction + Section 87A rebate for ₹0 Net Tax.",
            "investment_tip": "Focus on high-growth compounding: Invest in Nifty 50 Index Funds or ELSS mutual funds. Build an emergency fund covering 6 months of expenses."
        })
    elif total_gross_income <= 2500000:
        max_emp_nps = basic_salary * 0.10
        roadmap.append({
            "bracket": "₹12.75 Lakhs – ₹25 Lakhs (Moderate Bracket)",
            "title": "Structure Employer NPS & Utilize Dual Regime Optimization",
            "action": f"Request employer to allocate 10% of basic (up to ₹{max_emp_nps:,.0f}) towards Employer NPS under Sec 80CCD(2). It is tax-exempt under BOTH regimes!",
            "investment_tip": "If opting for Old Regime, split Section 80C into 70% ELSS (3-year lock-in for equity growth) and 30% PPF/EPF (guaranteed risk-free return). Claim extra ₹50k under 80CCD(1B) Tier-1 NPS."
        })
    else:
        max_emp_nps = basic_salary * 0.10
        roadmap.append({
            "bracket": "Above ₹25 Lakhs (High Bracket / HNI)",
            "title": "HNI Tax Reduction & Capital Gains Exemption Roadmap",
            "action": f"Maximize Employer NPS (Sec 80CCD(2) up to ₹{max_emp_nps:,.0f}), claim Education Loan Interest (Sec 80E - no upper cap!), and utilize Sec 54F / 54EC exemptions for stock & real estate gains.",
            "investment_tip": "Utilize Tax Loss Harvesting before March 31 to offset equity STCG/LTCG. Reinvest foreign RSU or property capital gains under Section 54F or Section 54EC Capital Gain Bonds."
        })
        
    return roadmap

def analyze_and_compare(profile):
    base_salary = float(profile.get("gross_income", 0))
    rsu_esop_perquisite = float(profile.get("rsu_esop_perquisite", 0))
    foreign_income = float(profile.get("foreign_income", 0))
    foreign_tax_paid = float(profile.get("foreign_tax_paid", 0))
    
    total_gross_income = base_salary + rsu_esop_perquisite + foreign_income
    basic = float(profile.get("basic_salary", base_salary * 0.50))
    
    hra_rec = float(profile.get("hra_received", 0))
    rent_paid = float(profile.get("rent_paid", 0))
    is_metro = bool(profile.get("is_metro", True))
    
    sec_80c = float(profile.get("sec_80c", 0))
    sec_80d = float(profile.get("sec_80d", 0))
    sec_80ccd_1b = float(profile.get("sec_80ccd_1b", 0))
    employer_nps = float(profile.get("employer_nps", 0))
    home_loan_interest = float(profile.get("home_loan_interest", 0))
    lta = float(profile.get("lta", 0))
    prof_tax = float(profile.get("prof_tax", 2500))
    
    # Loan Deductions
    education_loan_interest = float(profile.get("education_loan_interest", 0))
    ev_loan_interest = float(profile.get("ev_loan_interest", 0))
    medical_treatment_80ddb = float(profile.get("medical_treatment_80ddb", 0))
    donations_80g = float(profile.get("donations_80g", 0))
    
    # Capital Gains
    stcg_equity = float(profile.get("stcg_equity", 0))
    ltcg_equity = float(profile.get("ltcg_equity", 0))
    ltcg_property = float(profile.get("ltcg_property", 0))
    sec54_reinvestment = float(profile.get("sec54_reinvestment", 0))
    sec54f_reinvestment = float(profile.get("sec54f_reinvestment", 0))
    sec54ec_bonds = float(profile.get("sec54ec_bonds", 0))
    stcl_available = float(profile.get("stcl_available", 0))
    ltcl_available = float(profile.get("ltcl_available", 0))
    
    new_res = calculate_new_regime_tax(total_gross_income, employer_nps)
    old_res = calculate_old_regime_tax(basic, total_gross_income, hra_rec, rent_paid, is_metro,
                                        sec_80c, sec_80d, sec_80ccd_1b, employer_nps,
                                        home_loan_interest, lta, prof_tax,
                                        education_loan_interest, ev_loan_interest,
                                        medical_treatment_80ddb, donations_80g)
    
    cg_res = calculate_capital_gains_tax(stcg_equity, ltcg_equity, ltcg_property,
                                         sec54_reinvestment, sec54f_reinvestment, sec54ec_bonds,
                                         stcl_available, ltcl_available)
                                         
    effective_tax_rate_new = new_res["total_tax"] / max(1.0, total_gross_income)
    indian_tax_on_foreign_income = foreign_income * effective_tax_rate_new
    dtaa_ftc_claim = min(foreign_tax_paid, indian_tax_on_foreign_income)
    
    final_new_tax = max(0.0, new_res["total_tax"] + cg_res["total_cg_tax"] - dtaa_ftc_claim)
    final_old_tax = max(0.0, old_res["total_tax"] + cg_res["total_cg_tax"] - dtaa_ftc_claim)
    
    diff = final_old_tax - final_new_tax
    recommended_regime = "New Tax Regime" if diff >= 0 else "Old Tax Regime"
    savings_amount = abs(diff)
    
    recommendations = []
    
    # Education Loan Tip (Sec 80E)
    if education_loan_interest > 0:
        recommendations.append({
            "title": "Full Education Loan Interest Deduction (Sec 80E)",
            "section": "Section 80E",
            "potential_saving": round(education_loan_interest * 0.30, 2),
            "description": f"You claimed ₹{education_loan_interest:,.0f} in education loan interest. Under Section 80E, 100% of interest paid for higher studies is deductible without any upper limit under the Old Regime!"
        })
        
    # EV Loan Tip (Sec 80EEB)
    if ev_loan_interest > 0:
        claim_ev = min(ev_loan_interest, 150000.0)
        recommendations.append({
            "title": "Electric Vehicle Loan Interest Deduction (Sec 80EEB)",
            "section": "Section 80EEB",
            "potential_saving": round(claim_ev * 0.30, 2),
            "description": f"Claim up to ₹1,50,000 deduction on interest paid towards Electric Vehicle loans under Section 80EEB."
        })
        
    if foreign_tax_paid > 0:
        recommendations.append({
            "title": "Claim Foreign Tax Credit (DTAA Sec 90) via Form 67",
            "section": "Section 90 / DTAA & Form 67",
            "potential_saving": round(dtaa_ftc_claim, 2),
            "description": f"Claim ₹{dtaa_ftc_claim:,.0f} Foreign Tax Credit in India by filing Form 67 online before submitting your return."
        })

    # Generate Income-Based Investment Strategy Roadmap
    investment_roadmap = generate_income_based_investment_roadmap(total_gross_income, profile)
        
    return {
        "new_regime": new_res,
        "old_regime": old_res,
        "capital_gains": cg_res,
        "foreign_tax_credit": {
            "foreign_income": foreign_income,
            "foreign_tax_paid": foreign_tax_paid,
            "dtaa_ftc_claim": dtaa_ftc_claim
        },
        "final_new_tax": round(final_new_tax, 2),
        "final_old_tax": round(final_old_tax, 2),
        "recommended_regime": recommended_regime,
        "tax_difference": round(diff, 2),
        "savings_amount": round(savings_amount, 2),
        "recommendations": recommendations,
        "investment_roadmap": investment_roadmap
    }

if __name__ == "__main__":
    sample = {
        "gross_income": 1800000,
        "education_loan_interest": 120000,
        "ev_loan_interest": 150000
    }
    res = analyze_and_compare(sample)
    print("Old Tax with Loan Deductions:", res["old_regime"]["total_tax"])
    print("Investment Roadmap:", res["investment_roadmap"][0]["title"])
