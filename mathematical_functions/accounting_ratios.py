# mathematical_functions/accounting_ratios.py

from typing import List, Dict, Any, Optional
from mathematical_functions.accounting_basics import FinancialStatements, PnL, BalanceSheet, CashFlowStatement # Import data structures

def calculate_ratios_for_year(fs: FinancialStatements, prev_fs: Optional[FinancialStatements] = None) -> Dict[str, Any]:
    """
    Calculates a set of financial ratios for a single year's financial statements.

    Args:
        fs (FinancialStatements): The FinancialStatements object for the current year.
        prev_fs (Optional[FinancialStatements]): The FinancialStatements object for the previous year,
                                                required for some growth and turnover ratios.

    Returns:
        Dict[str, Any]: A dictionary where keys are ratio names and values are their calculated figures.
    """
    pnl = fs.pnl
    bs = fs.balance_sheet
    cfs = fs.cash_flow_statement
    
    ratios: Dict[str, Any] = {"Year": fs.year}

    # --- Profitability Ratios ---
    # Gross Profit Margin
    ratios["Gross Profit Margin"] = (pnl.GrossProfit / pnl.Revenue) if pnl.Revenue != 0 else None

    # Operating Profit Margin (EBIT Margin)
    ratios["Operating Profit Margin"] = (pnl.EBIT / pnl.Revenue) if pnl.Revenue != 0 else None

    # Net Profit Margin
    ratios["Net Profit Margin"] = (pnl.NetIncome / pnl.Revenue) if pnl.Revenue != 0 else None

    # Return on Assets (ROA)
    # Using average assets if previous year data is available, otherwise current year assets
    if prev_fs and prev_fs.balance_sheet.TotalAssets != 0:
        avg_assets = (bs.TotalAssets + prev_fs.balance_sheet.TotalAssets) / 2
        ratios["Return on Assets (ROA)"] = (pnl.NetIncome / avg_assets) if avg_assets != 0 else None
    else:
        ratios["Return on Assets (ROA)"] = (pnl.NetIncome / bs.TotalAssets) if bs.TotalAssets != 0 else None

    # Return on Equity (ROE)
    # Using average equity if previous year data is available, otherwise current year equity
    if prev_fs and prev_fs.balance_sheet.TotalEquity != 0:
        avg_equity = (bs.TotalEquity + prev_fs.balance_sheet.TotalEquity) / 2
        ratios["Return on Equity (ROE)"] = (pnl.NetIncome / avg_equity) if avg_equity != 0 else None
    else:
        ratios["Return on Equity (ROE)"] = (pnl.NetIncome / bs.TotalEquity) if bs.TotalEquity != 0 else None
        
    # --- Liquidity Ratios ---
    # Current Ratio
    ratios["Current Ratio"] = (
        (bs.Cash + bs.AccountsReceivable + bs.Inventory) / bs.AccountsPayable
    ) if bs.AccountsPayable != 0 else float('inf') # If no current liabilities, ratio is infinite

    # Quick Ratio (Acid-Test Ratio) - excludes Inventory
    ratios["Quick Ratio"] = (
        (bs.Cash + bs.AccountsReceivable) / bs.AccountsPayable
    ) if bs.AccountsPayable != 0 else float('inf')

    # Cash Ratio
    ratios["Cash Ratio"] = (
        bs.Cash / bs.AccountsPayable
    ) if bs.AccountsPayable != 0 else float('inf')

    # --- Solvency/Leverage Ratios ---
    # Debt-to-Equity Ratio
    ratios["Debt-to-Equity Ratio"] = (bs.Debt / bs.TotalEquity) if bs.TotalEquity != 0 else float('inf')

    # Debt-to-Assets Ratio
    ratios["Debt-to-Assets Ratio"] = (bs.Debt / bs.TotalAssets) if bs.TotalAssets != 0 else None

    # Interest Coverage Ratio (Times Interest Earned)
    ratios["Interest Coverage Ratio"] = (pnl.EBIT / pnl.InterestExpense) if pnl.InterestExpense != 0 else float('inf')
    
    # --- Efficiency/Activity Ratios ---
    # Inventory Turnover
    # Using average inventory if previous year data available
    if prev_fs and prev_fs.balance_sheet.Inventory != 0:
        avg_inventory = (bs.Inventory + prev_fs.balance_sheet.Inventory) / 2
        ratios["Inventory Turnover"] = (pnl.COGS / avg_inventory) if avg_inventory != 0 else None
    else:
        ratios["Inventory Turnover"] = (pnl.COGS / bs.Inventory) if bs.Inventory != 0 else None

    # Days Inventory Outstanding (DIO)
    ratios["Days Inventory Outstanding"] = (365 / ratios["Inventory Turnover"]) if isinstance(ratios["Inventory Turnover"], (int, float)) and ratios["Inventory Turnover"] != 0 else None

    # Accounts Receivable Turnover
    # Using average AR if previous year data available
    if prev_fs and prev_fs.balance_sheet.AccountsReceivable != 0:
        avg_ar = (bs.AccountsReceivable + prev_fs.balance_sheet.AccountsReceivable) / 2
        ratios["Accounts Receivable Turnover"] = (pnl.Revenue / avg_ar) if avg_ar != 0 else None
    else:
        ratios["Accounts Receivable Turnover"] = (pnl.Revenue / bs.AccountsReceivable) if bs.AccountsReceivable != 0 else None

    # Days Sales Outstanding (DSO)
    ratios["Days Sales Outstanding"] = (365 / ratios["Accounts Receivable Turnover"]) if isinstance(ratios["Accounts Receivable Turnover"], (int, float)) and ratios["Accounts Receivable Turnover"] != 0 else None

    # Accounts Payable Turnover
    # Using average AP if previous year data available
    if prev_fs and prev_fs.balance_sheet.AccountsPayable != 0:
        avg_ap = (bs.AccountsPayable + prev_fs.balance_sheet.AccountsPayable) / 2
        ratios["Accounts Payable Turnover"] = (pnl.COGS / avg_ap) if avg_ap != 0 else None
    else:
        ratios["Accounts Payable Turnover"] = (pnl.COGS / bs.AccountsPayable) if bs.AccountsPayable != 0 else None

    # Days Payables Outstanding (DPO)
    ratios["Days Payables Outstanding"] = (365 / ratios["Accounts Payable Turnover"]) if isinstance(ratios["Accounts Payable Turnover"], (int, float)) and ratios["Accounts Payable Turnover"] != 0 else None

    # Asset Turnover
    # Using average assets if previous year data available
    if prev_fs and prev_fs.balance_sheet.TotalAssets != 0:
        avg_assets_turnover = (bs.TotalAssets + prev_fs.balance_sheet.TotalAssets) / 2
        ratios["Asset Turnover"] = (pnl.Revenue / avg_assets_turnover) if avg_assets_turnover != 0 else None
    else:
        ratios["Asset Turnover"] = (pnl.Revenue / bs.TotalAssets) if bs.TotalAssets != 0 else None

    return ratios

def calculate_all_ratios(
    all_financial_statements: List[FinancialStatements],
    base_year_fs: Optional[FinancialStatements] = None # Optional: Include base year for first forecast year's avg calculations
) -> List[Dict[str, Any]]:
    """
    Calculates financial ratios for a list of annual financial statements.

    Args:
        all_financial_statements (List[FinancialStatements]): A list of FinancialStatements objects
                                                               (e.g., from accounting_basics.py or accounting_advanced.py).
        base_year_fs (Optional[FinancialStatements]): FinancialStatements object for the base year (Year 0) if available,
                                                      to enable calculation of ratios that use average balance sheet items
                                                      for the first forecast year.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary contains the ratios for one year.
    """
    all_ratios: List[Dict[str, Any]] = []

    for i, fs in enumerate(all_financial_statements):
        # Determine previous year's statements for average balance calculations
        if i == 0 and base_year_fs:
            prev_fs = base_year_fs
        elif i > 0:
            prev_fs = all_financial_statements[i-1]
        else:
            prev_fs = None # No previous year for the first forecast year if base_year_fs is not provided

        year_ratios = calculate_ratios_for_year(fs, prev_fs)
        all_ratios.append(year_ratios)

    return all_ratios

# --- Example Usage ---
if __name__ == "__main__":
    # Import necessary components from accounting_basics or accounting_advanced
    # For this example, we'll use a simple mock-up or assume you've run basic/advanced
    # from accounting_basics import generate_basic_financials, BaseYearData, Assumptions, PnL, BalanceSheet
    from accounting_advanced import generate_advanced_financials, AdvancedAssumptions

    # Create Base Year Data (mock or actual)
    base_pnl = PnL(
        Revenue=1000.0, COGS=600.0, GrossProfit=400.0, OperatingExpenses=250.0,
        Depreciation=50.0, InterestExpense=10.0, InterestIncome=0.0,
        EBIT=100.0, EBT=90.0, Taxes=22.5, NetIncome=67.5 # Ensuring balance
    )
    base_bs = BalanceSheet(
        Cash=100.0, AccountsReceivable=50.0, Inventory=70.0, GrossPPE=500.0,
        AccumulatedDepreciation=200.0, NetPPE=300.0,
        AccountsPayable=60.0, Debt=150.0, ShareCapital=200.0, RetainedEarnings=110.0
    )
    base_bs.TotalAssets = base_bs.Cash + base_bs.AccountsReceivable + base_bs.Inventory + base_bs.NetPPE
    base_bs.TotalLiabilities = base_bs.AccountsPayable + base_bs.Debt
    base_bs.TotalEquity = base_bs.ShareCapital + base_bs.RetainedEarnings
    base_bs.TotalLiabilitiesAndEquity = base_bs.TotalLiabilities + base_bs.TotalEquity
    
    base_year_data_for_ratios = BaseYearData(pnl=base_pnl, balance_sheet=base_bs, cash=base_bs.Cash)
    
    # Create a FinancialStatements object for the base year itself, to pass to ratio calculations
    base_year_fs_object = FinancialStatements(year=0, pnl=base_pnl, balance_sheet=base_bs)

    # Use Advanced Assumptions to generate statements for forecasting
    forecast_assumptions = AdvancedAssumptions(
        RevenueGrowthRate=0.10, GrossProfitMargin=0.40, OperatingExpenseAsPctRevenue=0.25,
        CapExAsPctRevenue=0.05, DepreciationRate=0.10, AR_Days=30, AP_Days=45,
        Inventory_Days=60, InterestRateOnDebt=0.05, TaxRate=0.25, DividendPayoutRatio=0.30,
        TargetMinimumCash=50.0, InterestIncomeOnCashRate=0.01,
        NewEquityIssued=0.0, ShareBuybacks=0.0
    )

    num_years_to_forecast = 3

    # Generate the forecasted statements using the advanced model
    forecasted_statements = generate_advanced_financials(
        base_year_data=base_year_data_for_ratios, # Pass the base_year_data for the forecast model
        assumptions=forecast_assumptions,
        num_forecast_years=num_years_to_forecast
    )

    # Calculate ratios
    # Pass the base_year_fs_object to calculate_all_ratios so the first forecast year's
    # average-based ratios can be accurately calculated.
    all_calculated_ratios = calculate_all_ratios(
        all_financial_statements=forecasted_statements,
        base_year_fs=base_year_fs_object
    )

    # --- Print Ratios ---
    print("\n--- Calculated Financial Ratios ---")
    for year_ratios in all_calculated_ratios:
        print(f"\n--- Year: {year_ratios['Year']} ---")
        for ratio_name, ratio_value in year_ratios.items():
            if ratio_name == "Year":
                continue # Already printed
            if isinstance(ratio_value, (float)):
                if ratio_value == float('inf'):
                    print(f"  {ratio_name}: Infinite")
                elif ratio_value is None:
                    print(f"  {ratio_name}: N/A (Undefined)")
                else:
                    # Format as percentage if it's a margin/rate, otherwise as a number
                    if "Margin" in ratio_name or "Rate" in ratio_name or "ROA" in ratio_name or "ROE" in ratio_name or "Ratio" in ratio_name and not "Turnover" in ratio_name:
                         print(f"  {ratio_name}: {ratio_value:.2%}")
                    else:
                         print(f"  {ratio_name}: {ratio_value:,.2f}")
            else:
                print(f"  {ratio_name}: {ratio_value}")