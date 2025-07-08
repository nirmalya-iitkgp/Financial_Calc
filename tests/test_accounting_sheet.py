# tests/test_accounting_sheet.py

import pytest
from pytest import approx

# Import the necessary classes and functions from your modules
from mathematical_functions.accounting_basics import (
    PnL, BalanceSheet, CashFlowStatement, FinancialStatements,
    BaseYearData, Assumptions, generate_basic_financials
)
from mathematical_functions.accounting_advanced import (
    AdvancedAssumptions, generate_advanced_financials
)
from mathematical_functions.accounting_ratios import calculate_ratios_for_year, calculate_all_ratios

# --- Fixtures for Reusable Test Data ---

@pytest.fixture
def base_year_data_fixture():
    """Provides a consistent base year data for tests."""
    base_pnl = PnL(
        Revenue=1000.0, COGS=600.0, GrossProfit=400.0, OperatingExpenses=250.0,
        Depreciation=50.0, InterestExpense=10.0, InterestIncome=0.0,
        EBIT=100.0, EBT=90.0, Taxes=22.5, NetIncome=67.5 # Ensures base P&L balances with 25% tax
    )
    base_bs = BalanceSheet(
        Cash=100.0, AccountsReceivable=50.0, Inventory=70.0, GrossPPE=500.0,
        AccumulatedDepreciation=200.0, NetPPE=300.0,
        AccountsPayable=60.0, Debt=150.0, ShareCapital=200.0, RetainedEarnings=110.0
    )
    # Ensure the base BS is internally consistent and balances
    base_bs.TotalAssets = base_bs.Cash + base_bs.AccountsReceivable + base_bs.Inventory + base_bs.NetPPE
    base_bs.TotalLiabilities = base_bs.AccountsPayable + base_bs.Debt
    base_bs.TotalEquity = base_bs.ShareCapital + base_bs.RetainedEarnings
    base_bs.TotalLiabilitiesAndEquity = base_bs.TotalLiabilities + base_bs.TotalEquity
    
    return BaseYearData(pnl=base_pnl, balance_sheet=base_bs, cash=base_bs.Cash)

@pytest.fixture
def basic_assumptions_fixture():
    """Provides basic forecasting assumptions."""
    return Assumptions(
        RevenueGrowthRate=0.10,          # 10%
        GrossProfitMargin=0.40,          # 40%
        OperatingExpenseAsPctRevenue=0.25, # 25%
        CapExAsPctRevenue=0.05,          # 5% of Revenue
        DepreciationRate=0.10,           # 10% of Gross PP&E
        AR_Days=30,
        AP_Days=45,
        Inventory_Days=60,
        InterestRateOnDebt=0.05,         # 5%
        TaxRate=0.25,                    # 25%
        DividendPayoutRatio=0.30         # 30% of Net Income
    )

@pytest.fixture
def advanced_assumptions_fixture():
    """Provides advanced forecasting assumptions."""
    return AdvancedAssumptions(
        RevenueGrowthRate=0.10,
        GrossProfitMargin=0.40,
        OperatingExpenseAsPctRevenue=0.25,
        CapExAsPctRevenue=0.05,
        DepreciationRate=0.10,
        AR_Days=30,
        AP_Days=45,
        Inventory_Days=60,
        InterestRateOnDebt=0.05,
        TaxRate=0.25,
        DividendPayoutRatio=0.30,
        TargetMinimumCash=50.0, # Target $50 cash balance
        InterestIncomeOnCashRate=0.01,
        NewEquityIssued=10.0, # Issue $10 new equity
        ShareBuybacks=5.0     # Buy back $5 shares
    )

# --- Tests for accounting_basics.py ---

def test_generate_basic_financials_structure(base_year_data_fixture, basic_assumptions_fixture):
    """Test that generate_basic_financials returns a list of FinancialStatements."""
    forecasted_statements = generate_basic_financials(
        base_year_data=base_year_data_fixture,
        assumptions=basic_assumptions_fixture,
        num_forecast_years=2
    )
    assert isinstance(forecasted_statements, list)
    assert len(forecasted_statements) == 2
    assert all(isinstance(fs, FinancialStatements) for fs in forecasted_statements)

def test_basic_financials_year1_pnl(base_year_data_fixture, basic_assumptions_fixture):
    """Test key P&L figures for Year 1 in basic model."""
    forecasted_statements = generate_basic_financials(
        base_year_data=base_year_data_fixture,
        assumptions=basic_assumptions_fixture,
        num_forecast_years=1
    )
    y1_pnl = forecasted_statements[0].pnl

    # Expected calculations for Year 1 based on base data and basic assumptions:
    # Base Revenue: 1000, Growth: 10% -> Y1 Revenue: 1100
    # Gross Profit Margin: 40% -> Y1 COGS: 1100 * 0.60 = 660, Y1 Gross Profit: 440
    # OpEx % Revenue: 25% -> Y1 OpEx: 1100 * 0.25 = 275
    # Base Gross PPE: 500, Dep Rate: 10% -> Y1 Depreciation: 500 * 0.10 = 50
    # EBIT: 440 - 275 - 50 = 115
    # Base Debt: 150, Int Rate: 5% -> Y1 Interest Expense: 150 * 0.05 = 7.5
    # EBT: 115 - 7.5 = 107.5
    # Tax Rate: 25% -> Y1 Taxes: 107.5 * 0.25 = 26.875
    # Net Income: 107.5 - 26.875 = 80.625

    assert y1_pnl.Revenue == approx(1100.0)
    assert y1_pnl.COGS == approx(660.0)
    assert y1_pnl.GrossProfit == approx(440.0)
    assert y1_pnl.OperatingExpenses == approx(275.0)
    assert y1_pnl.Depreciation == approx(50.0)
    assert y1_pnl.EBIT == approx(115.0)
    assert y1_pnl.InterestExpense == approx(7.5)
    assert y1_pnl.EBT == approx(107.5)
    assert y1_pnl.Taxes == approx(26.875)
    assert y1_pnl.NetIncome == approx(80.625)

def test_basic_financials_balance_sheet_balance(base_year_data_fixture, basic_assumptions_fixture):
    """Ensure the balance sheet balances for all forecasted years in basic model."""
    forecasted_statements = generate_basic_financials(
        base_year_data=base_year_data_fixture,
        assumptions=basic_assumptions_fixture,
        num_forecast_years=3
    )
    for fs in forecasted_statements:
        assert fs.balance_sheet.TotalAssets == approx(fs.balance_sheet.TotalLiabilitiesAndEquity, abs=1e-6)
        # Also check internal consistency of TotalAssets and TotalLiabilitiesAndEquity sums
        assert fs.balance_sheet.TotalAssets == approx(
            fs.balance_sheet.Cash + fs.balance_sheet.AccountsReceivable +
            fs.balance_sheet.Inventory + fs.balance_sheet.NetPPE
        )
        assert fs.balance_sheet.TotalLiabilitiesAndEquity == approx(
            fs.balance_sheet.AccountsPayable + fs.balance_sheet.Debt +
            fs.balance_sheet.ShareCapital + fs.balance_sheet.RetainedEarnings
        )


def test_basic_financials_cash_flow_linking(base_year_data_fixture, basic_assumptions_fixture):
    """Test cash flow statement and its link to balance sheet in basic model."""
    forecasted_statements = generate_basic_financials(
        base_year_data=base_year_data_fixture,
        assumptions=basic_assumptions_fixture,
        num_forecast_years=2
    )
    y1_cfs = forecasted_statements[0].cash_flow_statement
    y1_bs_cash = forecasted_statements[0].balance_sheet.Cash
    
    # Check Y1 Ending Cash matches BS Cash
    assert y1_cfs.EndingCash == approx(y1_bs_cash, abs=1e-6)

    # Check Y1 Net Change in Cash
    # Net Income: 80.625
    # Dep: 50
    # Change AR: (1100/365*30) - 50 = 90.41095 - 50 = 40.41095 (outflow)
    # Change Inv: (660/365*60) - 70 = 108.49315 - 70 = 38.49315 (outflow)
    # Change AP: (660/365*45) - 60 = 81.36986 - 60 = 21.36986 (inflow)
    # CFO = 80.625 + 50 - 40.41095 - 38.49315 + 21.36986 = 73.19076
    # CapEx: 1100 * 0.05 = 55 (outflow)
    # Dividends: 80.625 * 0.30 = 24.1875 (outflow)
    # Net Change = 73.19076 - 55 - 24.1875 = -6.99674
    # Beg Cash: 100
    # End Cash: 100 - 6.99674 = 93.00326

    assert y1_cfs.NetChangeInCash == approx(y1_cfs.NetCashFromOperations + y1_cfs.NetCashFromInvesting + y1_cfs.NetCashFromFinancing, abs=1e-6)
    assert y1_cfs.EndingCash == approx(y1_cfs.BeginningCash + y1_cfs.NetChangeInCash, abs=1e-6)
    assert y1_cfs.EndingCash == approx(93.90325, abs=1e-5) # Specific value check


# --- Tests for accounting_advanced.py ---

def test_generate_advanced_financials_structure(base_year_data_fixture, advanced_assumptions_fixture):
    """Test that generate_advanced_financials returns a list of FinancialStatements."""
    forecasted_statements = generate_advanced_financials(
        base_year_data=base_year_data_fixture,
        assumptions=advanced_assumptions_fixture,
        num_forecast_years=2
    )
    assert isinstance(forecasted_statements, list)
    assert len(forecasted_statements) == 2
    assert all(isinstance(fs, FinancialStatements) for fs in forecasted_statements)

def test_advanced_financials_balance_sheet_balance(base_year_data_fixture, advanced_assumptions_fixture):
    """Ensure the balance sheet balances for all forecasted years in advanced model."""
    forecasted_statements = generate_advanced_financials(
        base_year_data=base_year_data_fixture,
        assumptions=advanced_assumptions_fixture,
        num_forecast_years=3
    )
    for fs in forecasted_statements:
        assert fs.balance_sheet.TotalAssets == approx(fs.balance_sheet.TotalLiabilitiesAndEquity, abs=1e-6)
        assert fs.balance_sheet.TotalAssets == approx(
            fs.balance_sheet.Cash + fs.balance_sheet.AccountsReceivable +
            fs.balance_sheet.Inventory + fs.balance_sheet.NetPPE
        )
        assert fs.balance_sheet.TotalLiabilitiesAndEquity == approx(
            fs.balance_sheet.AccountsPayable + fs.balance_sheet.Debt +
            fs.balance_sheet.ShareCapital + fs.balance_sheet.RetainedEarnings
        )

def test_advanced_financials_debt_plug_and_equity_activities(base_year_data_fixture, advanced_assumptions_fixture):
    """Test dynamic debt sizing (plug) and explicit equity activities in advanced model."""
    # This scenario should cause debt to be issued/repaid to hit the target cash
    # Y1 cash before financing: 93.00326 (from basic model, minus base interest income)
    # Add new equity: +10
    # Subtract buybacks: -5
    # Subtract dividends: -24.1875
    # Cash before debt adjustment: 93.00326 + 10 - 5 - 24.1875 = 73.81576
    # Target cash: 50
    # Cash surplus: 73.81576 - 50 = 23.81576 (should be repaid debt)

    forecasted_statements = generate_advanced_financials(
        base_year_data=base_year_data_fixture,
        assumptions=advanced_assumptions_fixture,
        num_forecast_years=1
    )
    y1_fs = forecasted_statements[0]
    
    # Check interest income
    # Base Cash: 100, Interest Income Rate: 1% -> 100 * 0.01 = 1
    assert y1_fs.pnl.InterestIncome == approx(1.0)
    assert y1_fs.pnl.EBT == approx(107.5 + 1.0) # EBT from basic + interest income

    # Check debt plug
    # Previous debt: 150
    # Cash surplus should lead to debt repayment
    assert y1_fs.cash_flow_statement.NewDebtIssued == approx(0.0)
    assert y1_fs.cash_flow_statement.DebtRepaid == approx(49.42825, abs=1e-5) # Expect debt repayment
    assert y1_fs.balance_sheet.Debt == approx(150.0 - 49.42825, abs=1e-5) # New debt balance
    assert y1_fs.balance_sheet.Cash == approx(advanced_assumptions_fixture.TargetMinimumCash, abs=1e-6) # Ending cash is target

    # Check equity activities
    assert y1_fs.cash_flow_statement.NewEquityIssued == approx(10.0)
    assert y1_fs.cash_flow_statement.ShareBuybacks == approx(5.0)
    assert y1_fs.balance_sheet.ShareCapital == approx(
        base_year_data_fixture.balance_sheet.ShareCapital + 10.0 - 5.0
    )

# --- Tests for accounting_ratios.py ---

@pytest.fixture
def sample_financial_statements_for_ratios():
    """Provides a sample of FinancialStatements to test ratio calculations."""
    # Year 0 Base (as used in fixtures)
    pnl_y0 = PnL(Revenue=1000.0, COGS=600.0, GrossProfit=400.0, OperatingExpenses=250.0, Depreciation=50.0, InterestExpense=10.0, InterestIncome=0.0, EBIT=100.0, EBT=90.0, Taxes=22.5, NetIncome=67.5)
    bs_y0 = BalanceSheet(Cash=100.0, AccountsReceivable=50.0, Inventory=70.0, GrossPPE=500.0, AccumulatedDepreciation=200.0, NetPPE=300.0, AccountsPayable=60.0, Debt=150.0, ShareCapital=200.0, RetainedEarnings=110.0)
    bs_y0.TotalAssets = bs_y0.Cash + bs_y0.AccountsReceivable + bs_y0.Inventory + bs_y0.NetPPE
    bs_y0.TotalLiabilities = bs_y0.AccountsPayable + bs_y0.Debt
    bs_y0.TotalEquity = bs_y0.ShareCapital + bs_y0.RetainedEarnings
    bs_y0.TotalLiabilitiesAndEquity = bs_y0.TotalLiabilities + bs_y0.TotalEquity
    fs_y0 = FinancialStatements(year=0, pnl=pnl_y0, balance_sheet=bs_y0)

    # Year 1 (simplified mock, ensure internal consistency for ratio calculation)
    pnl_y1 = PnL(Revenue=1200.0, COGS=700.0, GrossProfit=500.0, OperatingExpenses=300.0, Depreciation=60.0, InterestExpense=15.0, InterestIncome=5.0, EBIT=140.0, EBT=130.0, Taxes=32.5, NetIncome=97.5)
    bs_y1 = BalanceSheet(Cash=150.0, AccountsReceivable=70.0, Inventory=80.0, GrossPPE=600.0, AccumulatedDepreciation=260.0, NetPPE=340.0, AccountsPayable=80.0, Debt=160.0, ShareCapital=200.0, RetainedEarnings=195.0) # RE = 110 + 97.5 - 12.5 (div)
    cfs_y1 = CashFlowStatement(NetIncome=97.5, Depreciation=60.0, ChangeInAR=20.0, ChangeInInventory=10.0, ChangeInAP=20.0, CapitalExpenditures=100.0, DividendsPaid=12.5, NewDebtIssued=20.0, DebtRepaid=10.0, NewEquityIssued=0.0, ShareBuybacks=0.0)
    cfs_y1.NetCashFromOperations = pnl_y1.NetIncome + cfs_y1.Depreciation - cfs_y1.ChangeInAR - cfs_y1.ChangeInInventory + cfs_y1.ChangeInAP # 97.5 + 60 - 20 - 10 + 20 = 147.5
    cfs_y1.NetCashFromInvesting = -cfs_y1.CapitalExpenditures # -100
    cfs_y1.NetCashFromFinancing = -cfs_y1.DividendsPaid + cfs_y1.NewDebtIssued - cfs_y1.DebtRepaid # -12.5 + 20 - 10 = -2.5
    cfs_y1.NetChangeInCash = cfs_y1.NetCashFromOperations + cfs_y1.NetCashFromInvesting + cfs_y1.NetCashFromFinancing # 147.5 - 100 - 2.5 = 45
    cfs_y1.BeginningCash = fs_y0.balance_sheet.Cash # 100
    cfs_y1.EndingCash = cfs_y1.BeginningCash + cfs_y1.NetChangeInCash # 100 + 45 = 145 (Note: this is why mock data can be tricky to balance perfectly for all checks if not generated by actual model)
    # Adjusting BS cash to match CFS ending cash for this mock example
    bs_y1.Cash = cfs_y1.EndingCash 

    # Re-calculate BS totals after mock adjustments
    bs_y1.TotalAssets = bs_y1.Cash + bs_y1.AccountsReceivable + bs_y1.Inventory + bs_y1.NetPPE # 145 + 70 + 80 + 340 = 635
    bs_y1.TotalLiabilities = bs_y1.AccountsPayable + bs_y1.Debt # 80 + 160 = 240
    bs_y1.TotalEquity = bs_y1.ShareCapital + bs_y1.RetainedEarnings # 200 + 195 = 395
    bs_y1.TotalLiabilitiesAndEquity = bs_y1.TotalLiabilities + bs_y1.TotalEquity # 240 + 395 = 635
    
    fs_y1 = FinancialStatements(year=1, pnl=pnl_y1, balance_sheet=bs_y1, cash_flow_statement=cfs_y1)

    return [fs_y0, fs_y1] # Return base year and year 1 for testing averages

def test_calculate_ratios_for_year_profitability(sample_financial_statements_for_ratios):
    """Test profitability ratios for a single year."""
    # Testing Year 1 ratios
    fs_y1 = sample_financial_statements_for_ratios[1] # Year 1 statements
    fs_y0 = sample_financial_statements_for_ratios[0] # Year 0 statements (for averages)
    ratios = calculate_ratios_for_year(fs_y1, fs_y0)

    # Expected calculations for Y1
    # Revenue: 1200, Net Income: 97.5, Gross Profit: 500, EBIT: 140
    # Avg Assets: (635 + 520) / 2 = 577.5
    # Avg Equity: (395 + 310) / 2 = 352.5

    assert ratios["Gross Profit Margin"] == approx(500.0 / 1200.0) # 0.4166...
    assert ratios["Operating Profit Margin"] == approx(140.0 / 1200.0) # 0.1166...
    assert ratios["Net Profit Margin"] == approx(97.5 / 1200.0) # 0.08125
    assert ratios["Return on Assets (ROA)"] == approx(97.5 / 577.5) # 0.1688...
    assert ratios["Return on Equity (ROE)"] == approx(97.5 / 352.5) # 0.2766...

def test_calculate_ratios_for_year_liquidity(sample_financial_statements_for_ratios):
    """Test liquidity ratios for a single year."""
    fs_y1 = sample_financial_statements_for_ratios[1]
    ratios = calculate_ratios_for_year(fs_y1) # No prev_fs needed for simple liquidity

    # Expected calculations for Y1
    # Current Assets: Cash(145) + AR(70) + Inv(80) = 295
    # Current Liabilities: AP(80)
    assert ratios["Current Ratio"] == approx(295.0 / 80.0) # 3.6875
    assert ratios["Quick Ratio"] == approx((145.0 + 70.0) / 80.0) # 2.6875
    assert ratios["Cash Ratio"] == approx(145.0 / 80.0) # 1.8125

def test_calculate_ratios_for_year_solvency_leverage(sample_financial_statements_for_ratios):
    """Test solvency/leverage ratios for a single year."""
    fs_y1 = sample_financial_statements_for_ratios[1]
    ratios = calculate_ratios_for_year(fs_y1)

    # Expected calculations for Y1
    # Debt: 160, Equity: 395, Total Assets: 635, EBIT: 140, Interest Expense: 15
    assert ratios["Debt-to-Equity Ratio"] == approx(160.0 / 395.0) # 0.4050...
    assert ratios["Debt-to-Assets Ratio"] == approx(160.0 / 635.0) # 0.2519...
    assert ratios["Interest Coverage Ratio"] == approx(140.0 / 15.0) # 9.333...

def test_calculate_ratios_for_year_efficiency(sample_financial_statements_for_ratios):
    """Test efficiency ratios for a single year."""
    fs_y1 = sample_financial_statements_for_ratios[1]
    fs_y0 = sample_financial_statements_for_ratios[0]
    ratios = calculate_ratios_for_year(fs_y1, fs_y0)

    # Expected calculations for Y1
    # COGS: 700, Revenue: 1200
    # Avg Inventory: (80 + 70) / 2 = 75
    # Avg AR: (70 + 50) / 2 = 60
    # Avg AP: (80 + 60) / 2 = 70
    # Avg Assets: (635 + 520) / 2 = 577.5

    assert ratios["Inventory Turnover"] == approx(700.0 / 75.0) # 9.333...
    assert ratios["Days Inventory Outstanding"] == approx(365.0 / (700.0 / 75.0)) # 39.107...
    assert ratios["Accounts Receivable Turnover"] == approx(1200.0 / 60.0) # 20.0
    assert ratios["Days Sales Outstanding"] == approx(365.0 / 20.0) # 18.25
    assert ratios["Accounts Payable Turnover"] == approx(700.0 / 70.0) # 10.0
    assert ratios["Days Payables Outstanding"] == approx(365.0 / 10.0) # 36.5
    assert ratios["Asset Turnover"] == approx(1200.0 / 577.5) # 2.078...

def test_calculate_ratios_division_by_zero():
    """Test handling of division by zero for ratios."""
    pnl_zero_revenue = PnL(Revenue=0.0, COGS=0.0, GrossProfit=0.0, EBIT=0.0, NetIncome=0.0, InterestExpense=10.0)
    bs_zero_liabilities = BalanceSheet(Cash=100.0, AccountsReceivable=50.0, Inventory=0.0, AccountsPayable=0.0, Debt=0.0, TotalEquity=100.0, TotalAssets=150.0) # Simplified for test
    fs_zero_rev_liab = FinancialStatements(year=1, pnl=pnl_zero_revenue, balance_sheet=bs_zero_liabilities)

    ratios = calculate_ratios_for_year(fs_zero_rev_liab)

    assert ratios["Gross Profit Margin"] is None
    assert ratios["Operating Profit Margin"] is None
    assert ratios["Net Profit Margin"] is None
    
    assert ratios["Current Ratio"] == float('inf') # Denominator is 0
    assert ratios["Quick Ratio"] == float('inf')
    assert ratios["Cash Ratio"] == float('inf')
    
    assert ratios["Debt-to-Equity Ratio"] == approx(0.0) # 0 / 100
    assert ratios["Interest Coverage Ratio"] == approx(0.0) # EBIT 0 / IE 10


def test_calculate_all_ratios_integration(base_year_data_fixture, advanced_assumptions_fixture):
    """Test the integration of generating statements and then calculating all ratios."""
    # Generate statements using the advanced model
    forecasted_statements = generate_advanced_financials(
        base_year_data=base_year_data_fixture,
        assumptions=advanced_assumptions_fixture,
        num_forecast_years=2
    )
    
    # Create a FinancialStatements object for the base year from BaseYearData for ratio calculations
    base_year_fs_object = FinancialStatements(
        year=0, 
        pnl=base_year_data_fixture.pnl, 
        balance_sheet=base_year_data_fixture.balance_sheet
    )

    # Calculate ratios for all generated years, including using base_year_fs_object for Year 1 averages
    all_ratios = calculate_all_ratios(
        forecasted_statements,
        base_year_fs=base_year_fs_object
    )

    assert isinstance(all_ratios, list)
    assert len(all_ratios) == 2 # Ratios for 2 forecast years

    # Check a specific ratio for a specific year
    y1_ratios = all_ratios[0]
    assert y1_ratios["Year"] == 1
    assert "Net Profit Margin" in y1_ratios
    assert "Debt-to-Equity Ratio" in y1_ratios
    assert "Days Inventory Outstanding" in y1_ratios

    # Verify a basic check for Y1 Net Profit Margin
    # Y1 Net Income (advanced model with interest income, etc.): ~81.425
    # Y1 Revenue (advanced model): 1100
    # Expected NPM: ~81.425 / 1100 = ~0.07402
    assert y1_ratios["Net Profit Margin"] == approx(forecasted_statements[0].pnl.NetIncome / forecasted_statements[0].pnl.Revenue, abs=1e-5)