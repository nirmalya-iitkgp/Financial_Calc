# mathematical_functions/accounting_advanced.py

from dataclasses import dataclass, field
from typing import Dict, List, Any

# Import basic financial statement dataclasses from accounting_basics
from mathematical_functions.accounting_basics import PnL, BalanceSheet, CashFlowStatement, FinancialStatements, BaseYearData

# We are NOT directly importing specific depreciation calculation functions from mathematical_functions.accounting
# for the aggregate PP&E depreciation in this advanced model, as truly accurate advanced depreciation
# often requires asset-by-asset tracking (which is too input-heavy for this calculator's current scope).
# Instead, we continue to use a depreciation rate, but allow for more complex financial plug logic.
# from mathematical_functions.accounting import calculate_depreciation_straight_line, calculate_depreciation_double_declining_balance

@dataclass
class AdvancedAssumptions:
    """Advanced forecasting assumptions."""
    RevenueGrowthRate: float
    GrossProfitMargin: float
    OperatingExpenseAsPctRevenue: float # Excludes Depreciation
    CapExAsPctRevenue: float # PP&E Purchases
    DepreciationRate: float # As % of Gross PP&E
    AR_Days: int # Accounts Receivable in days
    AP_Days: int # Accounts Payable in days
    Inventory_Days: int # Inventory in days
    InterestRateOnDebt: float # Cost of Debt
    TaxRate: float
    DividendPayoutRatio: float # As % of Net Income

    # --- New Advanced Inputs ---
    TargetMinimumCash: float # The cash balance the company aims to maintain; debt acts as a plug
    InterestIncomeOnCashRate: float = 0.0 # Rate at which excess cash earns interest
    NewEquityIssued: float = 0.0 # Explicit annual new equity raised
    ShareBuybacks: float = 0.0 # Explicit annual share buybacks

def generate_advanced_financials(
    base_year_data: BaseYearData,
    assumptions: AdvancedAssumptions,
    num_forecast_years: int
) -> List[FinancialStatements]:
    """
    Generates integrated P&L, Balance Sheet, and Cash Flow Statements
    for multiple years using advanced assumptions, including dynamic debt sizing.

    Args:
        base_year_data (BaseYearData): Initial financial data for Year 0.
        assumptions (AdvancedAssumptions): Advanced forecasting assumptions.
        num_forecast_years (int): Number of years to forecast.

    Returns:
        List[FinancialStatements]: A list of FinancialStatements objects, one for each forecast year.
    """
    if num_forecast_years <= 0:
        raise ValueError("Number of forecast years must be positive.")
    if assumptions.TargetMinimumCash < 0:
        raise ValueError("Target minimum cash cannot be negative.")

    all_statements: List[FinancialStatements] = []

    current_pnl = base_year_data.pnl
    current_bs = base_year_data.balance_sheet
    current_cash = base_year_data.cash # Track cash for CFS roll-forward

    for year_idx in range(1, num_forecast_years + 1):
        new_pnl = PnL()
        new_bs = BalanceSheet()
        new_cfs = CashFlowStatement()
        
        # --- 1. P&L Calculations ---
        new_pnl.Revenue = current_pnl.Revenue * (1 + assumptions.RevenueGrowthRate)
        new_pnl.COGS = new_pnl.Revenue * (1 - assumptions.GrossProfitMargin)
        new_pnl.GrossProfit = new_pnl.Revenue - new_pnl.COGS

        new_pnl.OperatingExpenses = new_pnl.Revenue * assumptions.OperatingExpenseAsPctRevenue
        
        # Depreciation (still simplified as a rate on gross PP&E for 'advanced' due to aggregate nature)
        new_pnl.Depreciation = current_bs.GrossPPE * assumptions.DepreciationRate
        
        new_pnl.EBIT = new_pnl.GrossProfit - new_pnl.OperatingExpenses - new_pnl.Depreciation

        # Interest Expense (based on prior year's debt)
        new_pnl.InterestExpense = current_bs.Debt * assumptions.InterestRateOnDebt

        # Interest Income (on prior year's cash balance)
        new_pnl.InterestIncome = current_cash * assumptions.InterestIncomeOnCashRate # New advanced P&L line

        new_pnl.EBT = new_pnl.EBIT - new_pnl.InterestExpense + new_pnl.InterestIncome # Include interest income
        new_pnl.Taxes = new_pnl.EBT * assumptions.TaxRate if new_pnl.EBT > 0 else 0.0
        new_pnl.NetIncome = new_pnl.EBT - new_pnl.Taxes

        # --- 2. Balance Sheet Calculations (Pre-Cash & Debt Plugs) ---
        
        # Assets
        new_bs.AccountsReceivable = (new_pnl.Revenue / 365) * assumptions.AR_Days
        new_bs.Inventory = (new_pnl.COGS / 365) * assumptions.Inventory_Days
        
        # PP&E (Gross)
        new_bs.GrossPPE = current_bs.GrossPPE + (new_pnl.Revenue * assumptions.CapExAsPctRevenue)
        # Accumulated Depreciation
        new_bs.AccumulatedDepreciation = current_bs.AccumulatedDepreciation + new_pnl.Depreciation
        new_bs.NetPPE = new_bs.GrossPPE - new_bs.AccumulatedDepreciation

        # Liabilities
        new_bs.AccountsPayable = (new_pnl.COGS / 365) * assumptions.AP_Days
        
        # Debt: Will be determined by the cash flow plug. Initialize it to prior year.
        # This will be updated after CFF calculations.
        new_bs.Debt = current_bs.Debt

        # Equity (Share Capital changes explicitly by input)
        new_bs.ShareCapital = current_bs.ShareCapital + assumptions.NewEquityIssued - assumptions.ShareBuybacks
        # Retained Earnings calculated after Net Income and Dividends determined
        new_bs.RetainedEarnings = current_bs.RetainedEarnings + new_pnl.NetIncome # Interim calculation, dividends subtracted later
        new_bs.TotalEquity = new_bs.ShareCapital + new_bs.RetainedEarnings # Interim calculation

        # --- 3. Cash Flow Statement Calculations (Pre-Debt Plug) ---
        new_cfs.BeginningCash = current_cash

        # CFO
        new_cfs.NetIncome = new_pnl.NetIncome
        new_cfs.Depreciation = new_pnl.Depreciation
        
        new_cfs.ChangeInAR = new_bs.AccountsReceivable - current_bs.AccountsReceivable
        new_cfs.ChangeInInventory = new_bs.Inventory - current_bs.Inventory
        new_cfs.ChangeInAP = new_bs.AccountsPayable - current_bs.AccountsPayable

        new_cfs.NetCashFromOperations = (
            new_cfs.NetIncome
            + new_cfs.Depreciation
            - new_cfs.ChangeInAR
            - new_cfs.ChangeInInventory
            + new_cfs.ChangeInAP
        )

        # CFI
        new_cfs.CapitalExpenditures = new_pnl.Revenue * assumptions.CapExAsPctRevenue
        new_cfs.NetCashFromInvesting = -new_cfs.CapitalExpenditures

        # Cash Before Financing (CBF) - Crucial for Debt Plug
        cash_before_financing = new_cfs.BeginningCash + new_cfs.NetCashFromOperations + new_cfs.NetCashFromInvesting

        # --- CFF (with Debt as Plug) ---
        new_cfs.DividendsPaid = new_pnl.NetIncome * assumptions.DividendPayoutRatio
        
        new_cfs.NetCashFromFinancing = -new_cfs.DividendsPaid # Start with dividends

        # Handle Equity Activities
        new_cfs.NewEquityIssued = assumptions.NewEquityIssued
        new_cfs.ShareBuybacks = assumptions.ShareBuybacks
        new_cfs.NetCashFromFinancing += new_cfs.NewEquityIssued - new_cfs.ShareBuybacks

        # Debt Sizing Logic (Debt as the Plug)
        cash_after_equity_financing_before_debt = cash_before_financing + new_cfs.NewEquityIssued - new_cfs.ShareBuybacks - new_cfs.DividendsPaid

        debt_change_needed = assumptions.TargetMinimumCash - cash_after_equity_financing_before_debt
        
        new_cfs.NewDebtIssued = max(0.0, debt_change_needed) # If cash is short, issue debt
        new_cfs.DebtRepaid = max(0.0, -debt_change_needed) # If cash is surplus, repay debt

        # Ensure debt is not repaid below zero
        if new_cfs.DebtRepaid > current_bs.Debt:
            new_cfs.DebtRepaid = current_bs.Debt
            # Recalculate NewDebtIssued based on max possible repayment
            new_cfs.NewDebtIssued = max(0.0, debt_change_needed + (new_cfs.DebtRepaid - (-debt_change_needed)))

        new_cfs.NetCashFromFinancing += new_cfs.NewDebtIssued - new_cfs.DebtRepaid
        
        # Update Debt on Balance Sheet based on the plug
        new_bs.Debt = current_bs.Debt + new_cfs.NewDebtIssued - new_cfs.DebtRepaid
        if new_bs.Debt < 0: # Ensure debt doesn't go negative
            new_bs.Debt = 0.0

        # --- Net Change in Cash ---
        new_cfs.NetChangeInCash = (
            new_cfs.NetCashFromOperations
            + new_cfs.NetCashFromInvesting
            + new_cfs.NetCashFromFinancing
        )
        new_cfs.EndingCash = new_cfs.BeginningCash + new_cfs.NetChangeInCash

        # --- 4. Final Balance Sheet Linking (Cash is the Plug) ---
        new_bs.Cash = new_cfs.EndingCash # This is the cash plug from the CFS

        new_bs.TotalAssets = (
            new_bs.Cash
            + new_bs.AccountsReceivable
            + new_bs.Inventory
            + new_bs.NetPPE
        )
        
        new_bs.TotalLiabilities = new_bs.AccountsPayable + new_bs.Debt
        
        # Final Retained Earnings calculation (incorporating dividends)
        new_bs.RetainedEarnings = current_bs.RetainedEarnings + new_pnl.NetIncome - new_cfs.DividendsPaid
        new_bs.TotalEquity = new_bs.ShareCapital + new_bs.RetainedEarnings
        
        new_bs.TotalLiabilitiesAndEquity = new_bs.TotalLiabilities + new_bs.TotalEquity

        # --- Critical Balance Check ---
        balance_check_tolerance = 1e-6
        if abs(new_bs.TotalAssets - new_bs.TotalLiabilitiesAndEquity) > balance_check_tolerance:
             print(f"Warning: Balance Sheet does not balance in Year {year_idx}!")
             print(f"Total Assets: {new_bs.TotalAssets:,.2f}, Total L&E: {new_bs.TotalLiabilitiesAndEquity:,.2f}")
             # In a robust system, you might raise a custom error here
        
        # Store the current year's statements
        all_statements.append(FinancialStatements(
            year=year_idx,
            pnl=new_pnl,
            balance_sheet=new_bs,
            cash_flow_statement=new_cfs
        ))

        # Set current year's data as previous for the next iteration
        current_pnl = new_pnl
        current_bs = new_bs
        current_cash = new_cfs.EndingCash

    return all_statements

# --- Example Usage for accounting_advanced.py ---
if __name__ == "__main__":
    # Define Base Year (Year 0) Data - Reusing structures from accounting_basics
    # Ensure this base data is balanced for a clean start
    base_pnl = PnL(
        Revenue=1000.0,
        COGS=600.0,
        GrossProfit=400.0,
        OperatingExpenses=250.0,
        Depreciation=50.0,
        InterestExpense=10.0,
        InterestIncome=0.0 # No interest income in base year for simplicity
    )
    base_pnl.EBIT = base_pnl.GrossProfit - base_pnl.OperatingExpenses - base_pnl.Depreciation
    base_pnl.EBT = base_pnl.EBIT - base_pnl.InterestExpense + base_pnl.InterestIncome
    base_pnl.Taxes = base_pnl.EBT * 0.25 if base_pnl.EBT > 0 else 0.0
    base_pnl.NetIncome = base_pnl.EBT - base_pnl.Taxes
    
    base_bs = BalanceSheet(
        Cash=100.0,
        AccountsReceivable=50.0,
        Inventory=70.0,
        GrossPPE=500.0,
        AccumulatedDepreciation=200.0,
        NetPPE=300.0,
        AccountsPayable=60.0,
        Debt=150.0,
        ShareCapital=200.0,
        RetainedEarnings=110.0 # This was adjusted to balance in basics' example
    )
    base_bs.TotalAssets = base_bs.Cash + base_bs.AccountsReceivable + base_bs.Inventory + base_bs.NetPPE
    base_bs.TotalLiabilities = base_bs.AccountsPayable + base_bs.Debt
    base_bs.TotalEquity = base_bs.ShareCapital + base_bs.RetainedEarnings
    base_bs.TotalLiabilitiesAndEquity = base_bs.TotalLiabilities + base_bs.TotalEquity
    
    base_year_cash_balance = base_bs.Cash

    base_data = BaseYearData(pnl=base_pnl, balance_sheet=base_bs, cash=base_year_cash_balance)

    # Define Advanced Assumptions for Forecasting
    advanced_forecast_assumptions = AdvancedAssumptions(
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
        # Advanced specific inputs:
        TargetMinimumCash=50.0, # Company wants to keep at least $50 cash
        InterestIncomeOnCashRate=0.01, # Earns 1% on cash
        NewEquityIssued=0.0, # No new equity issued by default
        ShareBuybacks=0.0 # No share buybacks by default
    )

    num_years_to_forecast = 3

    # Generate the financial statements with advanced logic
    forecasted_statements = generate_advanced_financials(
        base_year_data=base_data,
        assumptions=advanced_forecast_assumptions,
        num_forecast_years=num_years_to_forecast
    )

    # --- Print Results (Basic Display) ---
    print("--- Base Year (Year 0) Data ---")
    print(f"P&L: Revenue={base_data.pnl.Revenue}, Net Income={base_data.pnl.NetIncome}")
    print(f"BS: Cash={base_data.balance_sheet.Cash}, Total Assets={base_data.balance_sheet.TotalAssets}, Total L&E={base_data.balance_sheet.TotalLiabilitiesAndEquity}")
    print("\n--- Forecasted Financial Statements (Advanced) ---")

    for fs in forecasted_statements:
        print(f"\nYear: {fs.year}")
        print("--- P&L ---")
        print(f"  Revenue: {fs.pnl.Revenue:,.2f}")
        print(f"  COGS: {fs.pnl.COGS:,.2f}")
        print(f"  Gross Profit: {fs.pnl.GrossProfit:,.2f}")
        print(f"  Operating Expenses: {fs.pnl.OperatingExpenses:,.2f}")
        print(f"  Depreciation: {fs.pnl.Depreciation:,.2f}")
        print(f"  EBIT: {fs.pnl.EBIT:,.2f}")
        print(f"  Interest Expense: {fs.pnl.InterestExpense:,.2f}")
        print(f"  Interest Income: {fs.pnl.InterestIncome:,.2f}") # New P&L line
        print(f"  EBT: {fs.pnl.EBT:,.2f}")
        print(f"  Taxes: {fs.pnl.Taxes:,.2f}")
        print(f"  Net Income: {fs.pnl.NetIncome:,.2f}")

        print("\n--- Balance Sheet ---")
        print(f"  Cash: {fs.balance_sheet.Cash:,.2f}")
        print(f"  Accounts Receivable: {fs.balance_sheet.AccountsReceivable:,.2f}")
        print(f"  Inventory: {fs.balance_sheet.Inventory:,.2f}")
        print(f"  Gross PP&E: {fs.balance_sheet.GrossPPE:,.2f}")
        print(f"  Accumulated Depreciation: {fs.balance_sheet.AccumulatedDepreciation:,.2f}")
        print(f"  Net PP&E: {fs.balance_sheet.NetPPE:,.2f}")
        print(f"  Total Assets: {fs.balance_sheet.TotalAssets:,.2f}")
        print(f"  Accounts Payable: {fs.balance_sheet.AccountsPayable:,.2f}")
        print(f"  Debt: {fs.balance_sheet.Debt:,.2f}")
        print(f"  Total Liabilities: {fs.balance_sheet.TotalLiabilities:,.2f}")
        print(f"  Share Capital: {fs.balance_sheet.ShareCapital:,.2f}")
        print(f"  Retained Earnings: {fs.balance_sheet.RetainedEarnings:,.2f}")
        print(f"  Total Equity: {fs.balance_sheet.TotalEquity:,.2f}")
        print(f"  Total Liabilities & Equity: {fs.balance_sheet.TotalLiabilitiesAndEquity:,.2f}")
        print(f"  BS Balance Check (Assets - L&E): {fs.balance_sheet.TotalAssets - fs.balance_sheet.TotalLiabilitiesAndEquity:,.2f}")


        print("\n--- Cash Flow Statement ---")
        print(f"  Beginning Cash: {fs.cash_flow_statement.BeginningCash:,.2f}")
        print(f"  Net Income: {fs.cash_flow_statement.NetIncome:,.2f}")
        print(f"  Depreciation: {fs.cash_flow_statement.Depreciation:,.2f}")
        print(f"  Change in AR: {fs.cash_flow_statement.ChangeInAR:,.2f}")
        print(f"  Change in Inventory: {fs.cash_flow_statement.ChangeInInventory:,.2f}")
        print(f"  Change in AP: {fs.cash_flow_statement.ChangeInAP:,.2f}")
        print(f"  Net Cash From Operations: {fs.cash_flow_statement.NetCashFromOperations:,.2f}")
        print(f"  Capital Expenditures: {fs.cash_flow_statement.CapitalExpenditures:,.2f}")
        print(f"  Net Cash From Investing: {fs.cash_flow_statement.NetCashFromInvesting:,.2f}")
        print(f"  Dividends Paid: {fs.cash_flow_statement.DividendsPaid:,.2f}")
        print(f"  New Equity Issued: {fs.cash_flow_statement.NewEquityIssued:,.2f}") # New CFS line
        print(f"  Share Buybacks: {fs.cash_flow_statement.ShareBuybacks:,.2f}") # New CFS line
        print(f"  New Debt Issued: {fs.cash_flow_statement.NewDebtIssued:,.2f}") # New CFS line
        print(f"  Debt Repaid: {fs.cash_flow_statement.DebtRepaid:,.2f}") # New CFS line
        print(f"  Net Cash From Financing: {fs.cash_flow_statement.NetCashFromFinancing:,.2f}")
        print(f"  Net Change in Cash: {fs.cash_flow_statement.NetChangeInCash:,.2f}")
        print(f"  Ending Cash: {fs.cash_flow_statement.EndingCash:,.2f}")