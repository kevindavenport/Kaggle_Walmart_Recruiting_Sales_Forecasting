# Fixed Income Explorer

An interactive Streamlit app for learning the fundamentals of fixed income — yield curves, bond duration, and price/yield relationships — with live sliders and charts.

## Features

| Tab | What you can do |
|---|---|
| **Yield Curve** | Shape a yield curve with per-maturity sliders, see normal / flat / inverted classifications, and watch key spreads update in real time |
| **Duration** | Input any bond's coupon, maturity, and yield; get back price, Macaulay duration, modified duration, and DV01 instantly |
| **Price Sensitivity** | Visualise the full price/yield curve, mark your bond, and shock rates by any number of basis points to see the P&L impact |

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

- **Yield curve** shapes and what they signal (normal, flat, inverted)
- **2Y/10Y and 3M/10Y spreads** as recession indicators
- **Bond pricing** from discounted cash flows
- **Macaulay duration** — weighted average time to cash flows
- **Modified duration** — % price sensitivity per 1% yield move
- **DV01** — dollar value of a basis point
- **Convexity** — why price gains exceed price losses for equal yield moves
