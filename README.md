# Auctions and Mechanism Design Assignment

This folder contains the implementation and report for Assignment 4. The assignment asks for simulations of second-price and first-price auctions, plus a VCG mechanism for procuring a cheapest path.

## Requirements and implementation

### Part 1: Second-price sealed-bid auction

- Bidder 1's value is fixed at 0.2, 0.5, or 0.8, and its bid is evaluated from 0.00 through 1.00 in increments of 0.01.
- Each rival independently draws a value uniformly from [0, 1] and bids truthfully, half its value, or a fresh uniform random amount.
- The code simulates 100,000 auctions for each bid/strategy/value combination, averages bidder 1's utility, and saves a 3-by-3 plot for one rival and another for two rivals using the same strategy.
- Fixed rival bids 0.1, 0.4, and 0.9 are also checked against all three values. With two rivals, the code checks the fixed bid pairs listed in the report.
- The assignment text says “Repeat parts A and C” for the two-rival case. This implementation repeats the stochastic experiment in A and the fixed-bid verification in B, which is the meaningful interpretation of the apparent typo.

### Part 2: First-price auction

- For 2, 3, and 4 bidders, bidder 1 bids `k * v` for `k` from 0.1 to 2.0 in increments of 0.1. The other bidders use the equilibrium bid `(n-1)/n * v`.
- The code estimates bidder 1's expected utility, the fraction of auctions where the winning bid exceeds the runner-up bid, and the average difference between those bids.

### Part 3: VCG cheapest path

- The code uses the directed edges and costs shown in Figure 7.3: AB=3, AC=2, BD=2, BE=1, CE=3, CF=5, DF=2, and EF=1. It enumerates simple paths from A to F, selects the least-cost path, computes VCG payments, and plots utility for BE (on the chosen path) and CE (off the chosen path) as their reported costs vary from 0 to 10 in increments of 0.5.
- The resulting chosen path is ABEF with total cost 5, and the payments are AB=4, BE=2, EF=3, and 0 for all other edges, as requested.

## Files

- `auctions.py` — simulation, VCG calculations, console output, and plot generation.
- `report.tex` — written report with methodology, result tables, plots, and conclusions.
- `Auction_Project.pdf` — compiled report.
- `plots/` — generated figures for Parts 1A, 1C, 2, and 3.

## Run

From this folder, install Python 3 with NumPy and Matplotlib available, then run:

```bash
python3 auctions.py
```

The script uses a fixed random seed (`42`) and writes the figures into `plots/`. The current results were checked by running the complete script; the printed summaries and regenerated plots agree with the report's result tables and conclusions. Small differences in stochastic results can occur if the code, seed, or simulation count is changed.

To compile the report, use a LaTeX installation with `pdflatex`:

```bash
pdflatex report.tex
```

The current environment does not have `pdflatex`, so after the Figure 7.3 correction the source `report.tex` is up to date but the existing `Auction_Project.pdf` has not been rebuilt yet. Recompile it with the command above to refresh the PDF and embed the updated Part 3 figure and results.
