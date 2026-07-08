# Equity Data Analysis Solution

This repository contains my solution to a coding exercise involving equity price analysis over a fixed date window.

## Objective

The task was to:
- identify the top 5 performing stocks between two fixed dates
- compute 30-day average trading volume
- visualize the price history of the selected stocks
- document assumptions and observations about data quality

## Approach

I used Python with pandas and matplotlib to:
- load and inspect the dataset
- compute close-to-close return from `2021-06-01` to `2021-10-13`
- rank stocks by performance
- calculate 30-day average volume using a 30-calendar-day lookback ending on `Y`
- flag unusually large one-day moves as potential anomalies for review
- generate a chart and PDF summary

## Files

- `analysis.py` - main analysis script
- `make_pdf.py` - generates the PDF summary
- `notes.md` - explanation of approach, assumptions, and data-quality observations
- `top5_naive.csv` - literal top 5 ranking
- `top5_clean.csv` - review-adjusted top 5 ranking
- `top5_price_history.png` - price history chart
- `output/equity_analysis_himanshi_agrawal.pdf` - final PDF deliverable

## Assumptions

- Performance was measured using simple close-to-close return between the two fixed dates.
- If the endpoint row existed but the OHLCV values were null, I used the nearest prior valid close.
- 30-day average volume was interpreted as a 30-calendar-day lookback window ending on `Y`.
- A one-day move greater than 50% was treated as a heuristic flag for further review, not as definitive proof of bad data.

## How to Run

Install dependencies:

```bash
pip install pandas matplotlib reportlab
