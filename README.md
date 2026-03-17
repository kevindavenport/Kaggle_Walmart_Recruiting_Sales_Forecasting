# Fixed Income Explorer

An interactive Streamlit app for learning the fundamentals of fixed income and portfolio construction — yield curves, bond duration, price/yield relationships, and the Black-Litterman model — with live sliders and charts. Designed for anyone with up to CFA Level 1 knowledge.

## Features

| Tab | What you can do |
|---|---|
| **Yield Curve** | Shape a yield curve with per-maturity sliders, see normal / flat / inverted classifications, and watch key spreads update in real time |
| **Duration** | Input any bond's coupon, maturity, and yield; get back price, Macaulay duration, modified duration, and DV01 instantly |
| **Price Sensitivity** | Visualise the full price/yield curve, mark your bond, and shock rates by any number of basis points to see the P&L impact |
| **Black-Litterman** | Set market cap weights to generate equilibrium returns, express per-asset views with confidence levels, and see how the BL model blends them into posterior returns and portfolio weights |

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Concepts Covered

**Fixed Income**
- **Yield curve** shapes and what they signal (normal, flat, inverted)
- **2Y/10Y and 3M/10Y spreads** as recession indicators
- **Bond pricing** from discounted cash flows
- **Macaulay duration** — weighted average time to cash flows
- **Modified duration** — % price sensitivity per 1% yield move
- **DV01** — dollar value of a basis point
- **Convexity** — why price gains exceed price losses for equal yield moves

**Portfolio Construction**
- **Market-implied equilibrium returns** — reverse-optimising from market cap weights
- **Black-Litterman blending** — combining equilibrium returns with investor views
- **Confidence-weighted views** — how conviction level shifts posterior returns
- **Mean-variance optimal weights** — how expected returns translate to allocations
