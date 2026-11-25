import unittest
from server.tax_calculator import analyze_and_compare, calculate_old_regime_tax, generate_income_based_investment_roadmap

class TestLoansAndStrategyEngine(unittest.TestCase):
    def test_education_loan_sec80e_unlimited(self):
        # 18L gross salary with 2L Education Loan Interest (Sec 80E)
        res = calculate_old_regime_tax(basic_salary=900000, gross_income=1800000, hra_received=0, rent_paid=0,
                                       is_metro=True, sec_80c=150000, sec_80d=25000, sec_80ccd_1b=50000,
                                       employer_nps=0, home_loan_interest=0, lta=0, prof_tax=2500,
                                       education_loan_interest=200000)
        self.assertEqual(res["education_loan_interest"], 200000)
        self.assertTrue(res["total_deductions"] >= 477500)

    def test_ev_loan_sec80eeb_cap(self):
        # EV Loan Interest 2L should be capped at 1.5L
        res = calculate_old_regime_tax(basic_salary=900000, gross_income=1800000, hra_received=0, rent_paid=0,
                                       is_metro=True, sec_80c=0, sec_80d=0, sec_80ccd_1b=0,
                                       employer_nps=0, home_loan_interest=0, lta=0, prof_tax=2500,
                                       ev_loan_interest=200000)
        self.assertEqual(res["ev_loan_interest"], 150000)

    def test_income_based_investment_roadmap(self):
        roadmap_under_12L = generate_income_based_investment_roadmap(1000000, {})
        self.assertIn("Under ₹12.75 Lakhs", roadmap_under_12L[0]["bracket"])
        
        roadmap_hni = generate_income_based_investment_roadmap(3000000, {})
        self.assertIn("Above ₹25 Lakhs", roadmap_hni[0]["bracket"])

if __name__ == "__main__":
    unittest.main()
