# C:\Users\Nirmalya\Downloads\AI Work\Financial Calculator\gui\acc_output_gui.py

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import logging
from typing import List, Dict, Any
import csv # Import the csv module

from mathematical_functions.accounting_basics import FinancialStatements, PnL, BalanceSheet, CashFlowStatement # Import necessary data classes

logger = logging.getLogger(__name__)

class AccountingOutputGUI(ttk.Frame):
    """
    GUI for displaying the results of financial statement generation.
    It expects a list of FinancialStatements objects and displays them
    in a structured, year-by-year format within a scrollable frame.
    Includes an option to export results to CSV.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.output_frames = {} # To hold frames for each year's output
        self.current_financial_statements: List[FinancialStatements] = [] # Store the data for export
        self._create_widgets()
        logger.info("AccountingOutputGUI initialized.")

    def _create_widgets(self):
        """Creates the widgets for the Accounting Output GUI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Export button row
        self.grid_rowconfigure(2, weight=1) # Scrolled frame row

        ttk.Label(self, text="Financial Accounting Output", font=('Arial', 14, 'bold')) \
            .grid(row=0, column=0, pady=10, sticky="ew")

        # Export Button
        self.export_button = ttk.Button(self, text="Export to CSV", command=self._export_to_csv, style='TButton')
        self.export_button.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="ew")
        self.export_button.config(state=tk.DISABLED) # Disable initially, enable when data is present

        # Use a Frame inside a Canvas to allow for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, background=self.winfo_toplevel().cget('bg'))
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        self.scrollable_frame = ttk.Frame(self.canvas)
        # Configure the scrollable frame to expand to the width of the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Make content inside scrollable_frame expand

        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # Bind canvas resize to update the embedded frame width
        self.canvas.bind('<Configure>', self._on_canvas_resize)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

    def _on_canvas_resize(self, event):
        """Adjusts the width of the scrollable frame when the canvas resizes."""
        # Update the width of the window embedded in the canvas to match the canvas width
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
        # Also update the scroll region, though it's typically handled by the scrollable_frame's bind
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def clear_results(self):
        """Clears all previously displayed financial statement results."""
        for frame_name, frame in self.output_frames.items():
            frame.destroy()
        self.output_frames.clear()
        self.current_financial_statements = [] # Clear stored data
        self.export_button.config(state=tk.DISABLED) # Disable export button
        logger.info("Cleared previous financial statement results.")
        # Reset scroll position
        self.canvas.yview_moveto(0)


    def display_results(self, data: List[FinancialStatements]):
        """
        Displays the calculated financial statements.
        This method now expects a list of FinancialStatements objects.

        Args:
            data (List[FinancialStatements]): A list containing FinancialStatements objects,
                                              one for each forecasted year.
        """
        self.clear_results() # Clear previous results before displaying new ones

        # Robustness check: Ensure 'data' is always treated as a list
        if not isinstance(data, list):
            logger.error(f"Expected a list of FinancialStatements, but received type: {type(data)}. Wrapping in a list.")
            data = [data] # Wrap it in a list if it's somehow not already

        if not data:
            messagebox.showinfo("No Results", "No financial statements generated. Please check input and calculation logic.")
            logger.warning("Attempted to display empty financial statement results.")
            return

        # Store the data for potential export
        self.current_financial_statements = sorted(data, key=lambda fs: fs.year) # Sort and store

        # Enable the export button now that there's data
        self.export_button.config(state=tk.NORMAL)

        current_row = 0
        for fs in self.current_financial_statements: # Iterate through the list of FinancialStatements objects
            year_frame = ttk.LabelFrame(self.scrollable_frame, text=f"Year {fs.year} Financials", padding=(10, 5))
            year_frame.grid(row=current_row, column=0, sticky="ew", pady=10, padx=5)
            year_frame.grid_columnconfigure(0, weight=1) # Make content inside year_frame expand
            self.output_frames[f"year_{fs.year}"] = year_frame # Store for clearing

            self._display_pnl(year_frame, fs.pnl)
            self._display_balance_sheet(year_frame, fs.balance_sheet)
            self._display_cash_flow_statement(year_frame, fs.cash_flow_statement)

            current_row += 1
        logger.info(f"Displayed financial statements for {len(data)} years.")
        # Update scroll region after all widgets are added
        self.scrollable_frame.update_idletasks() # Ensure all widgets have their final sizes
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def _display_pnl(self, parent_frame: ttk.LabelFrame, pnl: PnL):
        """Displays the Profit & Loss statement in the given parent frame."""
        pnl_frame = ttk.LabelFrame(parent_frame, text="Profit & Loss Statement", padding=(5, 2))
        pnl_frame.pack(fill="x", expand=True, pady=(5,0), padx=5)
        pnl_frame.grid_columnconfigure(0, weight=1)
        pnl_frame.grid_columnconfigure(1, weight=1)

        row = 0
        self._add_pnl_row(pnl_frame, "Revenue:", pnl.Revenue, row); row += 1
        self._add_pnl_row(pnl_frame, "COGS:", pnl.COGS, row); row += 1
        self._add_pnl_row(pnl_frame, "Gross Profit:", pnl.GrossProfit, row, is_bold=True); row += 1
        self._add_pnl_row(pnl_frame, "Operating Expenses:", pnl.OperatingExpenses, row); row += 1
        self._add_pnl_row(pnl_frame, "Depreciation:", pnl.Depreciation, row); row += 1
        self._add_pnl_row(pnl_frame, "EBIT:", pnl.EBIT, row, is_bold=True); row += 1
        self._add_pnl_row(pnl_frame, "Interest Expense:", pnl.InterestExpense, row); row += 1
        self._add_pnl_row(pnl_frame, "Interest Income:", pnl.InterestIncome, row); row += 1
        self._add_pnl_row(pnl_frame, "EBT:", pnl.EBT, row, is_bold=True); row += 1
        self._add_pnl_row(pnl_frame, "Taxes:", pnl.Taxes, row); row += 1
        self._add_pnl_row(pnl_frame, "Net Income:", pnl.NetIncome, row, is_bold=True); row += 1

    def _add_pnl_row(self, parent_frame, label_text, value, row_num, is_bold=False):
        """Helper to add a row to the P&L display."""
        font_style = ('Arial', 10, 'bold') if is_bold else ('Arial', 10)
        ttk.Label(parent_frame, text=label_text, font=font_style, anchor="w") \
            .grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(parent_frame, text=f"{value:,.2f}", font=font_style, anchor="e") \
            .grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)

    def _display_balance_sheet(self, parent_frame: ttk.LabelFrame, bs: BalanceSheet):
        """Displays the Balance Sheet in the given parent frame."""
        bs_frame = ttk.LabelFrame(parent_frame, text="Balance Sheet", padding=(5, 2))
        bs_frame.pack(fill="x", expand=True, pady=(5,0), padx=5)
        bs_frame.grid_columnconfigure(0, weight=1)
        bs_frame.grid_columnconfigure(1, weight=1)

        row = 0
        ttk.Label(bs_frame, text="--- Assets ---", font=('Arial', 10, 'underline'), anchor="w") \
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5,2)); row += 1
        self._add_bs_row(bs_frame, "Cash:", bs.Cash, row); row += 1
        self._add_bs_row(bs_frame, "Accounts Receivable:", bs.AccountsReceivable, row); row += 1
        self._add_bs_row(bs_frame, "Inventory:", bs.Inventory, row); row += 1
        self._add_bs_row(bs_frame, "Gross PPE:", bs.GrossPPE, row); row += 1
        self._add_bs_row(bs_frame, "Accumulated Depreciation:", bs.AccumulatedDepreciation, row); row += 1
        self._add_bs_row(bs_frame, "Net PPE:", bs.NetPPE, row); row += 1
        self._add_bs_row(bs_frame, "Total Assets:", bs.TotalAssets, row, is_bold=True); row += 1

        ttk.Label(bs_frame, text="--- Liabilities & Equity ---", font=('Arial', 10, 'underline'), anchor="w") \
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5,2)); row += 1
        self._add_bs_row(bs_frame, "Accounts Payable:", bs.AccountsPayable, row); row += 1
        self._add_bs_row(bs_frame, "Debt:", bs.Debt, row); row += 1
        self._add_bs_row(bs_frame, "Total Liabilities:", bs.TotalLiabilities, row, is_bold=True); row += 1
        self._add_bs_row(bs_frame, "Share Capital:", bs.ShareCapital, row); row += 1
        self._add_bs_row(bs_frame, "Retained Earnings:", bs.RetainedEarnings, row); row += 1
        self._add_bs_row(bs_frame, "Total Equity:", bs.TotalEquity, row, is_bold=True); row += 1
        self._add_bs_row(bs_frame, "Total Liabilities & Equity:", bs.TotalLiabilitiesAndEquity, row, is_bold=True); row += 1
        
        # Balance Check
        balance_diff = bs.TotalAssets - bs.TotalLiabilitiesAndEquity
        balance_check_color = "red" if abs(balance_diff) > 0.01 else "green" # Small tolerance for floating point errors
        
        ttk.Label(bs_frame, text="Balance Check (Assets - L&E):", font=('Arial', 10, 'bold'), anchor="w") \
            .grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(bs_frame, text=f"{balance_diff:,.2f}", font=('Arial', 10, 'bold'), foreground=balance_check_color, anchor="e") \
            .grid(row=row, column=1, sticky="ew", padx=5, pady=2); row += 1


    def _add_bs_row(self, parent_frame, label_text, value, row_num, is_bold=False):
        """Helper to add a row to the Balance Sheet display."""
        font_style = ('Arial', 10, 'bold') if is_bold else ('Arial', 10)
        ttk.Label(parent_frame, text=label_text, font=font_style, anchor="w") \
            .grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(parent_frame, text=f"{value:,.2f}", font=font_style, anchor="e") \
            .grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)

    def _display_cash_flow_statement(self, parent_frame: ttk.LabelFrame, cfs: CashFlowStatement):
        """Displays the Cash Flow Statement in the given parent frame."""
        cfs_frame = ttk.LabelFrame(parent_frame, text="Cash Flow Statement", padding=(5, 2))
        cfs_frame.pack(fill="x", expand=True, pady=(5,0), padx=5)
        cfs_frame.grid_columnconfigure(0, weight=1)
        cfs_frame.grid_columnconfigure(1, weight=1)

        row = 0
        self._add_cfs_row(cfs_frame, "Beginning Cash:", cfs.BeginningCash, row); row += 1
        ttk.Label(cfs_frame, text="--- Cash Flow from Operations ---", font=('Arial', 10, 'underline'), anchor="w") \
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5,2)); row += 1
        self._add_cfs_row(cfs_frame, "Net Income:", cfs.NetIncome, row); row += 1
        self._add_cfs_row(cfs_frame, "Depreciation:", cfs.Depreciation, row); row += 1
        # Invert for display logic: increase in AR is cash outflow (-), decrease is inflow (+)
        self._add_cfs_row(cfs_frame, "Change in Accounts Receivable:", -cfs.ChangeInAR, row); row += 1 
        # Invert for display logic: increase in Inventory is cash outflow (-), decrease is inflow (+)
        self._add_cfs_row(cfs_frame, "Change in Inventory:", -cfs.ChangeInInventory, row); row += 1 
        # Accounts Payable: increase in AP is cash inflow (+), decrease is outflow (-)
        self._add_cfs_row(cfs_frame, "Change in Accounts Payable:", cfs.ChangeInAP, row); row += 1
        self._add_cfs_row(cfs_frame, "Net Cash From Operations:", cfs.NetCashFromOperations, row, is_bold=True); row += 1

        ttk.Label(cfs_frame, text="--- Cash Flow from Investing ---", font=('Arial', 10, 'underline'), anchor="w") \
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5,2)); row += 1
        # CapEx is typically shown as a positive number in inputs, but a negative cash flow
        self._add_cfs_row(cfs_frame, "Capital Expenditures:", cfs.CapitalExpenditures, row); row += 1
        self._add_cfs_row(cfs_frame, "Net Cash From Investing:", cfs.NetCashFromInvesting, row, is_bold=True); row += 1

        ttk.Label(cfs_frame, text="--- Cash Flow from Financing ---", font=('Arial', 10, 'underline'), anchor="w") \
            .grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5,2)); row += 1
        self._add_cfs_row(cfs_frame, "Dividends Paid:", cfs.DividendsPaid, row); row += 1
        self._add_cfs_row(cfs_frame, "New Debt Issued:", cfs.NewDebtIssued, row); row += 1
        self._add_cfs_row(cfs_frame, "Debt Repaid:", cfs.DebtRepaid, row); row += 1
        self._add_cfs_row(cfs_frame, "New Equity Issued:", cfs.NewEquityIssued, row); row += 1
        self._add_cfs_row(cfs_frame, "Share Buybacks:", cfs.ShareBuybacks, row); row += 1
        self._add_cfs_row(cfs_frame, "Net Cash From Financing:", cfs.NetCashFromFinancing, row, is_bold=True); row += 1
        
        self._add_cfs_row(cfs_frame, "Net Change in Cash:", cfs.NetChangeInCash, row); row += 1
        self._add_cfs_row(cfs_frame, "Ending Cash:", cfs.EndingCash, row, is_bold=True); row += 1


    def _add_cfs_row(self, parent_frame, label_text, value, row_num, is_bold=False):
        """Helper to add a row to the Cash Flow Statement display."""
        font_style = ('Arial', 10, 'bold') if is_bold else ('Arial', 10)
        ttk.Label(parent_frame, text=label_text, font=font_style, anchor="w") \
            .grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(parent_frame, text=f"{value:,.2f}", font=font_style, anchor="e") \
            .grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)

    def _export_to_csv(self):
        """Exports the current financial statements data to a CSV file."""
        if not self.current_financial_statements:
            messagebox.showinfo("No Data", "No financial statements available to export.")
            logger.warning("Attempted to export CSV with no data.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Financial Statements as CSV"
        )
        if not file_path: # User cancelled the dialog
            logger.info("CSV export cancelled by user.")
            return

        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Collect all unique headers first from all statements
                headers_pnl = list(PnL.__annotations__.keys())
                headers_bs = list(BalanceSheet.__annotations__.keys())
                headers_cfs = list(CashFlowStatement.__annotations__.keys())

                # Create a comprehensive list of all data points for each year
                all_data_for_csv: List[Dict[str, Any]] = []

                for fs in self.current_financial_statements:
                    year_data = {"Year": fs.year}
                    # PnL data
                    for key in headers_pnl:
                        year_data[f"P&L: {key}"] = getattr(fs.pnl, key)
                    # BS data
                    for key in headers_bs:
                        year_data[f"BS: {key}"] = getattr(fs.balance_sheet, key)
                    # CFS data
                    for key in headers_cfs:
                        # Special handling for CFS items that are inverted for display
                        if key == "ChangeInAR":
                            year_data[f"CFS: {key}"] = -fs.cash_flow_statement.ChangeInAR
                        elif key == "ChangeInInventory":
                            year_data[f"CFS: {key}"] = -fs.cash_flow_statement.ChangeInInventory
                        else:
                            year_data[f"CFS: {key}"] = getattr(fs.cash_flow_statement, key)
                    all_data_for_csv.append(year_data)

                # Determine all unique column headers for the CSV
                # This ensures that even if a future model adds/removes fields, the CSV header is comprehensive
                all_csv_headers = ["Year"]
                for item in all_data_for_csv:
                    for key in item.keys():
                        if key not in all_csv_headers:
                            all_csv_headers.append(key)
                
                writer.writerow(all_csv_headers) # Write header row

                # Write data rows
                for row_data in all_data_for_csv:
                    row_values = [row_data.get(header, '') for header in all_csv_headers] # Use .get to handle missing keys gracefully
                    writer.writerow(row_values)

            messagebox.showinfo("Export Successful", f"Financial statements exported successfully to:\n{file_path}")
            logger.info(f"Financial statements exported to CSV: {file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")
            logger.error(f"Error exporting CSV: {e}", exc_info=True)