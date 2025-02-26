import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# File Paths
TRADE_LOG = "results/logs/arbitrage_trades.csv"
BACKTESTING_LOG = "results/logs/backtesting_results.csv"
OUTPUT_PDF = "results/reports/arbitrage_report.pdf"

# Plots to Include
PLOTS = {
    "Arbitrage Opportunities": "results/plots/arbitrage_opportunities.png",
    "Trade Execution": "results/plots/arbitrage_execution.png",
    "Profitability Distribution": "results/plots/profitability_distribution.png",
    "Execution Times": "results/plots/execution_times_histogram.png",
    "Backtesting Profit": "results/plots/backtesting_profit.png",
    "Backtesting Sharpe Ratio": "results/plots/backtesting_sharpe.png"
}

# Load Data
def load_data():
    trade_df = pd.read_csv(TRADE_LOG) if os.path.exists(TRADE_LOG) else None
    backtest_df = pd.read_csv(BACKTESTING_LOG) if os.path.exists(BACKTESTING_LOG) else None
    return trade_df, backtest_df

# Generate PDF Report
def generate_pdf(trade_df, backtest_df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(200, 10, "Quantum-Driven Arbitrage Strategies in DeFi", ln=True, align="C")
    pdf.ln(10)
    
    # Section 1: Trade Execution Summary
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, "1. Arbitrage Trade Execution", ln=True)
    
    if trade_df is not None:
        pdf.set_font("Arial", size=10)
        latest_trade = trade_df.iloc[-1]
        trade_summary = f"- Best Trade: {latest_trade['best_trade']}\n- Profit: {latest_trade['profit']}\n- Execution Time: {latest_trade['execution_time']}s\n"
        pdf.multi_cell(0, 10, trade_summary)
    else:
        pdf.cell(200, 10, "No trade execution data available.", ln=True)
    
    pdf.ln(5)

    # Section 2: Backtesting Summary
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, "2. Backtesting Performance", ln=True)
    
    if backtest_df is not None:
        latest_backtest = backtest_df.iloc[-1]
        backtest_summary = f"- Classical Profit: {latest_backtest['classical_avg_profit']}\n- Quantum Profit: {latest_backtest['quantum_avg_profit']}\n- Sharpe Ratio (Quantum): {latest_backtest['quantum_sharpe']}\n"
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, backtest_summary)
    else:
        pdf.cell(200, 10, "No backtesting data available.", ln=True)
    
    pdf.ln(5)

    # Section 3: Graphs
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, "3. Performance Visualizations", ln=True)
    pdf.ln(5)
    
    for title, img_path in PLOTS.items():
        if os.path.exists(img_path):
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, title, ln=True)
            pdf.image(img_path, x=10, w=180)
            pdf.ln(5)
    
    # Save PDF
    pdf.output(OUTPUT_PDF)
    print(f"[SUCCESS] Report saved to {OUTPUT_PDF}")

# Run Report Generation
if __name__ == "__main__":
    trade_data, backtest_data = load_data()
    generate_pdf(trade_data, backtest_data)
