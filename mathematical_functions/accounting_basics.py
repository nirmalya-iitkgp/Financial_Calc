# mathematical_functions/accounting_basics.py

from dataclasses import dataclass, field
from typing import Dict, List, Any

# We're simplifying depreciation for the 'basics' module to a rate input.
# If we were to use the specific straight-line function from mathematical_functions,
# we would need to track individual asset costs, salvage values, and useful lives,
# which goes beyond the 'minimum inputs' philosophy for this basic model.
# from mathematical_functions.accounting import calculate_depreciation_straight_line

@dataclass
class PnL:
    """Represents a single year's Profit & Loss Statement."""
    Revenue: float = 0.0
    COGS: float = 0.0
    GrossProfit: float = 0.0
    OperatingExpenses: float = 0.0
    Depreciation: float = 0.0
    EBIT: float = 0.0
    InterestExpense: float = 0.0
    InterestIncome: float = 0.0
    EBT: float = 0.0
    Taxes: float = 0.0
    NetIncome: float = 0.0

@dataclass
class BalanceSheet:
    """Represents a single year's Balance Sheet."""
    # Assets
    Cash: float = 0.0
    AccountsReceivable: float = 0.0
    Inventory: float = 0.0
    GrossPPE: float = 0.0
    AccumulatedDepreciation: float = 0.0
    NetPPE: float = 0.0
    TotalAssets: float = 0.0

    # Liabilities & Equity
    AccountsPayable: float = 0.0
    Debt: float = 0.0
    TotalLiabilities: float = 0.0
    ShareCapital: float = 0.0 # Assumed static for basic model unless explicitly changed
    RetainedEarnings: float = 0.0
    TotalEquity: float = 0.0
    TotalLiabilitiesAndEquity: float = 0.0

@dataclass
class CashFlowStatement:
    """Represents a single year's Cash Flow Statement."""
    # Cash Flow from Operations
    NetIncome: float = 0.0
    Depreciation: float = 0.0
    ChangeInAR: float = 0.0
    ChangeInInventory: float = 0.0
    ChangeInAP: float = 0.0
    NetCashFromOperations: float = 0.0

    # Cash Flow from Investing
    CapitalExpenditures: float = 0.0
    NetCashFromInvesting: float = 0.0

    # Cash Flow from Financing
    DividendsPaid: float = 0.0
    NewDebtIssued: float = 0.0      
    DebtRepaid: float = 0.0         
    NewEquityIssued: float = 0.0    
    ShareBuybacks: float = 0.0      
    NetCashFromFinancing: float = 0.0

    # Net Change in Cash
    NetChangeInCash: float = 0.0
    BeginningCash: float = 0.0
    EndingCash: float = 0.0

@dataclass
class FinancialStatements:
    """Holds the P&L, Balance Sheet, and Cash Flow Statement for a given year."""
    year: int
    pnl: PnL = field(default_factory=PnL)
    balance_sheet: BalanceSheet = field(default_factory=BalanceSheet)
    cash_flow_statement: CashFlowStatement = field(default_factory=CashFlowStatement)

@dataclass
class BaseYearData:
    """Initial financial data for Year 0."""
    pnl: PnL
    balance_sheet: BalanceSheet
    cash: float # Explicitly carry over cash for first calculation

@dataclass
class Assumptions:
    """Core forecasting assumptions (minimum inputs)."""
    RevenueGrowthRate: float
    GrossProfitMargin: float # COGS = Revenue * (1 - GrossProfitMargin)
    OperatingExpenseAsPctRevenue: float # Excludes Depreciation
    CapExAsPctRevenue: float # PP&E Purchases
    DepreciationRate: float # As % of Gross PP&E
    AR_Days: int # Accounts Receivable in days
    AP_Days: int # Accounts Payable in days
    Inventory_Days: int # Inventory in days
    InterestRateOnDebt: float # Assuming existing debt for simplicity
    TaxRate: float
    DividendPayoutRatio: float # As % of Net Income

def generate_basic_financials(
    base_year_data: BaseYearData,
    assumptions: Assumptions,
    num_forecast_years: int
) -> List[FinancialStatements]:
    """
    Generates integrated P&L, Balance Sheet, and Cash Flow Statements
    for multiple years based on minimum inputs.

    Args:
        base_year_data (BaseYearData): Initial financial data for Year 0.
        assumptions (Assumptions): Core forecasting assumptions.
        num_forecast_years (int): Number of years to forecast.

    Returns:
        List[FinancialStatements]: A list of FinancialStatements objects, one for each forecast year.
    """
    if num_forecast_years <= 0:
        raise ValueError("Number of forecast years must be positive.")

    # Initialize list to store results
    all_statements: List[FinancialStatements] = []

    # Prepare for the loop: current_pnl and current_bs will hold previous year's values
    # For Year 1, these will be the base_year_data values.
    # Note: We create mutable copies to avoid modifying the original base_year_data directly
    current_pnl = base_year_data.pnl
    current_bs = base_year_data.balance_sheet
    current_cash = base_year_data.cash # Track cash separately for easier CF linking

    for year_idx in range(1, num_forecast_years + 1):
        # Create new instances for the current year's statements
        new_pnl = PnL()
        new_bs = BalanceSheet()
        new_cfs = CashFlowStatement()
        
        # --- 1. P&L Calculations ---
        new_pnl.Revenue = current_pnl.Revenue * (1 + assumptions.RevenueGrowthRate)
        new_pnl.COGS = new_pnl.Revenue * (1 - assumptions.GrossProfitMargin)
        new_pnl.GrossProfit = new_pnl.Revenue - new_pnl.COGS

        new_pnl.OperatingExpenses = new_pnl.Revenue * assumptions.OperatingExpenseAsPctRevenue
        
        # Depreciation
        # For the 'basics' model, we simplify depreciation as a rate on previous gross PP&E.
        # This avoids needing detailed asset lists for individual straight-line calculations.
        new_pnl.Depreciation = current_bs.GrossPPE * assumptions.DepreciationRate
        
        new_pnl.EBIT = new_pnl.GrossProfit - new_pnl.OperatingExpenses - new_pnl.Depreciation

        # Interest Expense (assumes debt balance is from prior year's BS for simplicity)
        new_pnl.InterestExpense = current_bs.Debt * assumptions.InterestRateOnDebt

        new_pnl.EBT = new_pnl.EBIT - new_pnl.InterestExpense
        new_pnl.Taxes = new_pnl.EBT * assumptions.TaxRate if new_pnl.EBT > 0 else 0.0 # No tax benefit from losses
        new_pnl.NetIncome = new_pnl.EBT - new_pnl.Taxes

        # --- 2. Balance Sheet Calculations (Pre-Cash Plug) ---
        
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
        
        # Debt: For the basic model, let's assume debt remains constant unless explicitly raised/repaid
        # Or, we can make it a plug for simplicity if cash is targeted.
        # For minimum inputs, let's assume it rolls over for now, unless cash forces new debt.
        # The most basic way is to assume current_bs.Debt is carried forward,
        # and allow Cash to be the ultimate plug.
        new_bs.Debt = current_bs.Debt # Simplification for 'basics'

        # Equity
        new_bs.ShareCapital = current_bs.ShareCapital # Assumed static for basic model
        # Retained Earnings = Previous Retained Earnings + Net Income - Dividends
        dividends_paid = new_pnl.NetIncome * assumptions.DividendPayoutRatio
        
        # --- 3. Cash Flow Statement Calculations ---
        new_cfs.BeginningCash = current_cash # Cash from the end of the previous year

        # CFO
        new_cfs.NetIncome = new_pnl.NetIncome
        new_cfs.Depreciation = new_pnl.Depreciation # Non-cash add-back
        
        new_cfs.ChangeInAR = new_bs.AccountsReceivable - current_bs.AccountsReceivable # Increase in AR is a cash outflow
        new_cfs.ChangeInInventory = new_bs.Inventory - current_bs.Inventory # Increase in Inventory is a cash outflow
        new_cfs.ChangeInAP = new_bs.AccountsPayable - current_bs.AccountsPayable # Increase in AP is a cash inflow

        new_cfs.NetCashFromOperations = (
            new_cfs.NetIncome
            + new_cfs.Depreciation
            - new_cfs.ChangeInAR
            - new_cfs.ChangeInInventory
            + new_cfs.ChangeInAP
        )

        # CFI
        new_cfs.CapitalExpenditures = new_pnl.Revenue * assumptions.CapExAsPctRevenue
        new_cfs.NetCashFromInvesting = -new_cfs.CapitalExpenditures # CapEx is a cash outflow

        # CFF
        new_cfs.DividendsPaid = dividends_paid
        new_cfs.NetCashFromFinancing = -new_cfs.DividendsPaid # Dividends are a cash outflow

        # Net Change in Cash
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
        
        new_bs.RetainedEarnings = current_bs.RetainedEarnings + new_pnl.NetIncome - new_cfs.DividendsPaid
        new_bs.TotalEquity = new_bs.ShareCapital + new_bs.RetainedEarnings
        
        new_bs.TotalLiabilitiesAndEquity = new_bs.TotalLiabilities + new_bs.TotalEquity

        # --- Critical Balance Check ---
        # Add a tolerance for floating point inaccuracies
        balance_check_tolerance = 1e-6
        if abs(new_bs.TotalAssets - new_bs.TotalLiabilitiesAndEquity) > balance_check_tolerance:
             print(f"Warning: Balance Sheet does not balance in Year {year_idx}!")
             print(f"Total Assets: {new_bs.TotalAssets}, Total L&E: {new_bs.TotalLiabilitiesAndEquity}")
             # You might raise an error here in a production system
        
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

# --- Example Usage ---
if __name__ == "__main__":
    # Define Base Year (Year 0) Data
    # For a real scenario, these would come from actual historical financial statements
    base_pnl = PnL(
        Revenue=1000.0,
        COGS=600.0,
        GrossProfit=400.0,
        OperatingExpenses=250.0,
        Depreciation=50.0, # This depreciation is just for the base year's P&L
        InterestExpense=10.0,
        NetIncome=80.0 # This should actually balance based on the above numbers
    )
    # Correcting base_pnl NetIncome for consistency based on other base P&L items
    base_pnl.EBIT = base_pnl.GrossProfit - base_pnl.OperatingExpenses - base_pnl.Depreciation
    base_pnl.EBT = base_pnl.EBIT - base_pnl.InterestExpense
    # Assuming base year tax rate was 25% for Net Income calculation
    base_pnl.Taxes = base_pnl.EBT * 0.25 # Adjust based on actual base year tax
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
        RetainedEarnings=160.0 # Needs to balance BS: Assets = 100+50+70+300 = 520; L&E = 60+150+200+160 = 570 (oops, adjust)
    )
    # Adjusting base_bs Retained Earnings to make it balance:
    # Total Assets (Base) = 100 + 50 + 70 + (500 - 200) = 520
    # Total Liabilities (Base) = 60 + 150 = 210
    # Total Equity (Base) = Share Capital + Retained Earnings => 520 - 210 = 310
    # Retained Earnings = 310 - Share Capital (200) = 110
    base_bs.RetainedEarnings = 110.0
    base_bs.TotalAssets = base_bs.Cash + base_bs.AccountsReceivable + base_bs.Inventory + base_bs.NetPPE
    base_bs.TotalLiabilities = base_bs.AccountsPayable + base_bs.Debt
    base_bs.TotalEquity = base_bs.ShareCapital + base_bs.RetainedEarnings
    base_bs.TotalLiabilitiesAndEquity = base_bs.TotalLiabilities + base_bs.TotalEquity
    
    base_year_cash_balance = base_bs.Cash

    base_data = BaseYearData(pnl=base_pnl, balance_sheet=base_bs, cash=base_year_cash_balance)

    # Define Assumptions for Forecasting
    forecast_assumptions = Assumptions(
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

    num_years_to_forecast = 3

    # Generate the financial statements
    forecasted_statements = generate_basic_financials(
        base_year_data=base_data,
        assumptions=forecast_assumptions,
        num_forecast_years=num_years_to_forecast
    )

    # --- Print Results (Basic Display) ---
    print("--- Base Year (Year 0) Data ---")
    print(f"P&L: Revenue={base_data.pnl.Revenue}, Net Income={base_data.pnl.NetIncome}")
    print(f"BS: Cash={base_data.balance_sheet.Cash}, Total Assets={base_data.balance_sheet.TotalAssets}, Total L&E={base_data.balance_sheet.TotalLiabilitiesAndEquity}")
    print("\n--- Forecasted Financial Statements ---")

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
        print("  Net Income: {fs.cash_flow_statement.NetIncome:,.2f}")
        print("  Depreciation: {fs.cash_flow_statement.Depreciation:,.2f}")
        print("  Change in AR: {fs.cash_flow_statement.ChangeInAR:,.2f}")
        print("  Change in Inventory: {fs.cash_flow_statement.ChangeInInventory:,.2f}")
        print("  Change in AP: {fs.cash_flow_statement.ChangeInAP:,.2f}")
        print("  Net Cash From Operations: {fs.cash_flow_statement.NetCashFromOperations:,.2f}")
        print("  Capital Expenditures: {fs.cash_flow_statement.CapitalExpenditures:,.2f}")
        print("  Net Cash From Investing: {fs.cash_flow_statement.NetCashFromInvesting:,.2f}")
        print("  Dividends Paid: {fs.cash_flow_statement.DividendsPaid:,.2f}")
        print("  Net Cash From Financing: {fs.cash_flow_statement.NetCashFromFinancing:,.2f}")
        print(f"  Net Change in Cash: {fs.cash_flow_statement.NetChangeInCash:,.2f}")
        print(f"  Ending Cash: {fs.cash_flow_statement.EndingCash:,.2f}")