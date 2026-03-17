import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.interpolate import CubicSpline

st.set_page_config(page_title="Fixed Income Explainer", layout="wide")

st.title("Fixed Income Explorer")
st.markdown(
    "An interactive guide to **yield curves**, **bond duration**, and **interest rate risk** — "
    "built for anyone new to fixed income."
)

tabs = st.tabs(["📈 Yield Curve", "⏱ Duration", "💵 Price Sensitivity", "🎯 Black-Litterman"])


# ---------------------------------------------------------------------------
# TAB 1 — YIELD CURVE
# ---------------------------------------------------------------------------
with tabs[0]:
    st.header("Yield Curve Explorer")
    st.markdown(
        """
The **yield curve** plots interest rates (yields) against time to maturity for bonds of similar credit quality.

| Shape | What it looks like | What it often signals |
|---|---|---|
| **Normal** | Long yields > Short yields | Healthy growth expectations |
| **Flat** | Long ≈ Short yields | Uncertainty / transition |
| **Inverted** | Short yields > Long yields | Recession fears |
        """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Set Yields")
        r3m  = st.slider("3-Month (%)",  0.0, 10.0, 4.5, 0.05, key="r3m")
        r2y  = st.slider("2-Year (%)",   0.0, 10.0, 4.2, 0.05, key="r2y")
        r5y  = st.slider("5-Year (%)",   0.0, 10.0, 4.0, 0.05, key="r5y")
        r10y = st.slider("10-Year (%)",  0.0, 10.0, 4.2, 0.05, key="r10y")
        r30y = st.slider("30-Year (%)",  0.0, 10.0, 4.5, 0.05, key="r30y")

    maturities = [0.25, 2, 5, 10, 30]
    yields     = [r3m, r2y, r5y, r10y, r30y]

    cs       = CubicSpline(maturities, yields)
    x_smooth = np.linspace(0.25, 30, 300)
    y_smooth = cs(x_smooth)

    spread_10_3m = r10y - r3m
    spread_10_2  = r10y - r2y
    if spread_10_3m > 0.5:
        shape, curve_color = "Normal (Upward Sloping)", "#2ecc71"
    elif spread_10_3m < -0.25:
        shape, curve_color = "Inverted (Downward Sloping)", "#e74c3c"
    else:
        shape, curve_color = "Flat", "#f39c12"

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_smooth, y=y_smooth, mode="lines", name="Yield Curve",
            line=dict(color=curve_color, width=3),
        ))
        fig.add_trace(go.Scatter(
            x=maturities, y=yields, mode="markers", name="Key Maturities",
            marker=dict(size=10, color=curve_color, line=dict(width=2, color="white")),
            text=["3M", "2Y", "5Y", "10Y", "30Y"],
            textposition="top center",
        ))
        fig.update_layout(
            title=f"Yield Curve — {shape}",
            xaxis_title="Maturity (Years)",
            yaxis_title="Yield (%)",
            yaxis=dict(ticksuffix="%"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Shape", shape.split(" ")[0])
        c2.metric("2Y / 10Y Spread", f"{spread_10_2:+.2f}%")
        c3.metric("3M / 10Y Spread", f"{spread_10_3m:+.2f}%")

    with st.expander("How to read this chart"):
        st.markdown(
            """
- **Each point** is the annualised yield an investor receives for holding a bond until that maturity.
- Drag the sliders to simulate a **rate hike cycle** (short end rises first), a **bull flattener** (long end falls), or a **bear steepener** (long end rises).
- The **2Y/10Y spread** is the most-watched recession indicator: negative spread = inverted curve.
            """
        )


# ---------------------------------------------------------------------------
# TAB 2 — DURATION
# ---------------------------------------------------------------------------
def bond_analytics(face, coupon_rate, maturity_years, market_yield, freq=2):
    """Return price, Macaulay duration, modified duration, DV01."""
    c      = face * coupon_rate / freq          # coupon per period
    y      = market_yield / freq                # yield per period
    n      = int(maturity_years * freq)         # total periods
    t_arr  = np.arange(1, n + 1)
    cf     = np.full(n, c)
    cf[-1] += face                              # add par at maturity

    pv_arr  = cf / (1 + y) ** t_arr
    price   = pv_arr.sum()
    mac_dur = (t_arr * pv_arr).sum() / price / freq   # in years
    mod_dur = mac_dur / (1 + y)
    dv01    = mod_dur * price * 0.0001          # $ change per 1 bp
    return price, mac_dur, mod_dur, dv01


with tabs[1]:
    st.header("Duration Calculator")
    st.markdown(
        """
**Duration** measures how sensitive a bond's price is to changes in interest rates.
Think of it as the bond's *interest rate risk thermometer*.

- **Macaulay Duration** — weighted average time to receive the bond's cash flows (in years).
- **Modified Duration** — percentage price change for a 1% move in yield.
- **DV01** — dollar change in price for a 1 basis-point (0.01%) move in yield.
        """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Bond Parameters")
        face        = st.number_input("Face Value ($)", 100, 1_000_000, 1000, 100)
        coupon_pct  = st.slider("Annual Coupon Rate (%)", 0.0, 15.0, 5.0, 0.25)
        maturity    = st.slider("Years to Maturity", 1, 30, 10)
        yield_pct   = st.slider("Market Yield (%)", 0.1, 15.0, 5.0, 0.1)

    coupon_rate  = coupon_pct  / 100
    market_yield = yield_pct   / 100

    price, mac_dur, mod_dur, dv01 = bond_analytics(face, coupon_rate, maturity, market_yield)

    price_up,   *_ = bond_analytics(face, coupon_rate, maturity, market_yield + 0.01)
    price_down, *_ = bond_analytics(face, coupon_rate, maturity, market_yield - 0.01)

    with col2:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price", f"${price:,.2f}", help="Present value of all future cash flows")
        m2.metric("Macaulay Duration", f"{mac_dur:.2f} yrs")
        m3.metric("Modified Duration", f"{mod_dur:.2f}")
        m4.metric("DV01", f"${dv01:,.2f}", help="Dollar change per 1 basis-point rise in yield")

        st.divider()
        st.subheader("What happens if rates move by 1%?")

        col_up, col_dn = st.columns(2)
        col_up.metric(
            "Rates rise +1%",
            f"${price_up:,.2f}",
            f"{price_up - price:+,.2f} ({(price_up/price - 1)*100:+.2f}%)",
            delta_color="inverse",
        )
        col_dn.metric(
            "Rates fall −1%",
            f"${price_down:,.2f}",
            f"{price_down - price:+,.2f} ({(price_down/price - 1)*100:+.2f}%)",
        )

        st.markdown(
            f"> **Rule of thumb:** Modified Duration ≈ % price change per 1% yield move.  \n"
            f"> This bond has modified duration **{mod_dur:.2f}**, so a 1% rate rise "
            f"→ roughly **−{mod_dur:.1f}%** price change."
        )

    with st.expander("Key concepts explained"):
        st.markdown(
            """
**Why does price move opposite to yield?**
Bond cash flows are fixed. When yields rise, investors can get better returns elsewhere, so
they pay *less* for your bond's fixed cash flows — price falls.

**Why do longer bonds lose more?**
More cash flows lie far in the future, so discounting has a bigger effect. Duration captures this.

**Zero-coupon bonds have the highest duration** (= maturity), because all the cash flow
arrives at the end — maximum interest rate sensitivity.
            """
        )


# ---------------------------------------------------------------------------
# TAB 3 — PRICE / YIELD RELATIONSHIP
# ---------------------------------------------------------------------------
with tabs[2]:
    st.header("Price–Yield Relationship")
    st.markdown(
        """
The price/yield curve is **convex** — it curves outward. This is good news for bondholders:
prices rise *more* when yields fall than they fall when yields rise by the same amount.
        """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Bond Parameters")
        face2       = st.number_input("Face Value ($)", 100, 1_000_000, 1000, 100, key="f2")
        coupon2_pct = st.slider("Annual Coupon (%)", 0.0, 15.0, 5.0, 0.25, key="c2")
        maturity2   = st.slider("Years to Maturity", 1, 30, 10, key="m2")
        current_y   = st.slider("Current Market Yield (%)", 0.5, 15.0, 5.0, 0.1, key="cy")
        shock_bps   = st.slider("Rate Shock (basis points)", -300, 300, 100, 10)

    y_range = np.linspace(0.005, 0.15, 300)
    prices  = [bond_analytics(face2, coupon2_pct / 100, maturity2, y)[0] for y in y_range]

    current_price = bond_analytics(face2, coupon2_pct / 100, maturity2, current_y / 100)[0]
    shocked_y     = current_y / 100 + shock_bps / 10000
    shocked_y     = max(shocked_y, 0.001)
    shocked_price = bond_analytics(face2, coupon2_pct / 100, maturity2, shocked_y)[0]

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=y_range * 100, y=prices, mode="lines", name="Price/Yield Curve",
            line=dict(color="#3498db", width=3),
        ))
        fig2.add_trace(go.Scatter(
            x=[current_y], y=[current_price], mode="markers", name="Current",
            marker=dict(size=14, color="#2ecc71", symbol="circle"),
        ))
        fig2.add_trace(go.Scatter(
            x=[shocked_y * 100], y=[shocked_price], mode="markers", name=f"After {shock_bps:+}bp shock",
            marker=dict(size=14, color="#e74c3c", symbol="x"),
        ))
        fig2.add_shape(
            type="line",
            x0=current_y, y0=min(prices), x1=current_y, y1=current_price,
            line=dict(color="#2ecc71", dash="dot"),
        )
        fig2.add_shape(
            type="line",
            x0=shocked_y * 100, y0=min(prices), x1=shocked_y * 100, y1=shocked_price,
            line=dict(color="#e74c3c", dash="dot"),
        )
        fig2.update_layout(
            title="Bond Price vs. Yield",
            xaxis_title="Yield (%)",
            yaxis_title=f"Price ($)",
            xaxis=dict(ticksuffix="%"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig2, use_container_width=True)

        pnl   = shocked_price - current_price
        pnl_p = (shocked_price / current_price - 1) * 100
        st.metric(
            f"P&L from {shock_bps:+}bp rate move",
            f"${pnl:+,.2f}  ({pnl_p:+.2f}%)",
            delta_color="normal" if pnl >= 0 else "inverse",
        )

    with st.expander("What is convexity?"):
        st.markdown(
            """
**Convexity** is the curvature of the price/yield relationship.

- The *duration* approximation assumes a straight line — it underestimates price gains and
  overestimates price losses.
- Convexity corrects for this: the actual price curve bends *favourably* compared to the
  duration-only estimate.
- All else equal, **higher convexity is better** for the bondholder.
            """
        )


# ---------------------------------------------------------------------------
# TAB 4 — BLACK-LITTERMAN
# ---------------------------------------------------------------------------

def bl_posterior(w_mkt, sigma, delta, views_returns, confidences, tau=0.05):
    """
    Simplified Black-Litterman posterior mean returns.
    Assumes one absolute view per asset (P = I).
    Returns equilibrium returns (pi) and BL posterior returns (mu_bl).
    """
    n = len(w_mkt)
    # Step 1: reverse-optimise to get market-implied equilibrium returns
    pi = delta * sigma @ w_mkt

    # Step 2: build uncertainty matrix Omega — low confidence = high uncertainty
    # Confidence is 0-1; map to uncertainty: 0% confidence => huge omega, 100% => tiny
    epsilon = 1e-6
    omega = np.diag([(1.0 - c + epsilon) * tau * sigma[i, i]
                     for i, c in enumerate(confidences)])

    # Step 3: P = identity (one absolute view per asset), Q = view returns
    P = np.eye(n)
    Q = np.array(views_returns)

    # Step 4: posterior mean (He & Litterman formula)
    tau_sigma = tau * sigma
    M = np.linalg.inv(tau_sigma) + P.T @ np.linalg.inv(omega) @ P
    mu_bl = np.linalg.inv(M) @ (np.linalg.inv(tau_sigma) @ pi + P.T @ np.linalg.inv(omega) @ Q)

    return pi, mu_bl


def bl_weights(mu, sigma, delta):
    """Unconstrained mean-variance optimal weights given expected returns."""
    w = np.linalg.inv(delta * sigma) @ mu
    w = w / w.sum()          # re-scale to sum to 1 for readability
    return w


with tabs[3]:
    st.header("Black-Litterman Model — Plain English Edition")

    st.info(
        "**What problem does this solve?**  \n"
        "Standard portfolio optimisation (Markowitz) is famously unstable — tiny changes in expected "
        "return assumptions cause wild swings in portfolio weights. Black-Litterman fixes this by "
        "anchoring to a sensible starting point: **what the market itself is already pricing in**."
    )

    with st.expander("Start here — the core idea in plain English", expanded=True):
        st.markdown(
            """
### The two ingredients

**1. The Market's Implied View (the anchor)**

Imagine the entire market as one giant, well-diversified investor.
All of the buying and selling that happens every day produces *prices* — and those prices imply
an expected return for every asset.

> Example: if global investors hold 60% stocks / 40% bonds, the market is
> "saying" that stocks should earn enough extra return to justify that 60% weight.

We call this the **equilibrium return**. It is *not* a prediction — it is simply what the
current market prices imply, working backwards.

**2. Your Views (the personal tweak)**

You might disagree with the market on one or more assets.
Maybe you think tech stocks are overvalued, or that emerging market bonds look cheap.
Black-Litterman lets you express those views as *expected return numbers*, and — crucially —
lets you say **how confident** you are in each view on a scale of 0 to 100%.

### How they are blended

Think of it like a weighted average:

| Confidence in your view | Result |
|---|---|
| 0% | Final return = pure market equilibrium (you ignored your view) |
| 50% | Halfway blend between market and your view |
| 100% | Final return = your view (you completely overrode the market) |

The blended number is called the **posterior return** — it feeds into the portfolio
optimisation to produce the final weights.
            """
        )

    st.divider()

    # ── Asset setup ──────────────────────────────────────────────────────────
    ASSETS = ["Global Stocks", "Government Bonds", "Real Assets"]
    # Approximate long-run annual volatilities
    VOLS   = [0.16, 0.07, 0.12]
    # Approximate pairwise correlations
    CORR   = np.array([
        [1.00,  -0.20,  0.30],
        [-0.20,  1.00, -0.05],
        [0.30,  -0.05,  1.00],
    ])
    SIGMA  = np.outer(VOLS, VOLS) * CORR   # covariance matrix
    DELTA  = 2.5                            # typical risk aversion coefficient

    st.subheader("Step 1 — Market Starting Point")
    st.markdown(
        "Below are the **market cap weights** — roughly how a global passive investor "
        "is split across three broad asset classes today. These are pre-filled with "
        "realistic numbers but you can adjust them."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        w_stocks = st.slider("Stocks weight (%)", 10, 80, 55, 5,
                             help="Share of total portfolio in global equities")
    with col2:
        w_bonds  = st.slider("Bonds weight (%)",  10, 70, 35, 5,
                             help="Share of total portfolio in government bonds")
    with col3:
        w_real   = st.slider("Real Assets weight (%)", 0, 30, 10, 5,
                             help="Share in real assets (REITs, commodities, infrastructure)")

    raw_w = np.array([w_stocks, w_bonds, w_real], dtype=float)
    w_mkt = raw_w / raw_w.sum()

    st.caption(
        f"Normalised weights: {ASSETS[0]} {w_mkt[0]*100:.1f}% | "
        f"{ASSETS[1]} {w_mkt[1]*100:.1f}% | {ASSETS[2]} {w_mkt[2]*100:.1f}%  "
        f"*(weights always sum to 100%)*"
    )

    # Compute equilibrium returns from market weights
    pi, _ = bl_posterior(w_mkt, SIGMA, DELTA, [0, 0, 0], [0, 0, 0])

    eq_fig = go.Figure(go.Bar(
        x=ASSETS,
        y=pi * 100,
        marker_color=["#3498db", "#2ecc71", "#e67e22"],
        text=[f"{v*100:.1f}%" for v in pi],
        textposition="outside",
    ))
    eq_fig.update_layout(
        title="Market-Implied Equilibrium Returns",
        yaxis_title="Expected Annual Return (%)",
        yaxis=dict(ticksuffix="%", range=[0, max(pi * 100) * 1.5]),
        showlegend=False,
        height=350,
    )
    st.plotly_chart(eq_fig, use_container_width=True)

    st.caption(
        "These are *not* forecasts. They are the returns the market would need to deliver "
        "to justify the current price levels and weights — calculated by working backwards "
        "from prices using a standard risk/return model."
    )

    st.divider()

    # ── Views ─────────────────────────────────────────────────────────────────
    st.subheader("Step 2 — Enter Your Views")
    st.markdown(
        "For each asset, you can express a **view** (your expected annual return) and a "
        "**confidence level**. If you have no strong opinion, keep confidence near 0% — "
        "the model will effectively ignore your input and stick close to the market."
    )

    views = []
    confs = []
    with st.expander("What should I put here?"):
        st.markdown(
            """
- **View return**: your best guess at what this asset class will return over the next year.
  It does *not* have to be precise. A range in your head is fine — enter the midpoint.
- **Confidence**: how strongly you believe your view vs. the market.
  - 10–20% = "slight tilt, I'm not very sure"
  - 40–60% = "moderate conviction"
  - 80–100% = "very high conviction" — use sparingly, this overrides the market almost entirely
            """
        )

    for i, asset in enumerate(ASSETS):
        st.markdown(f"**{asset}**")
        c1, c2 = st.columns(2)
        eq_pct = pi[i] * 100
        view_ret = c1.slider(
            f"Your expected return (%)",
            -5.0, 20.0, round(eq_pct, 1), 0.5,
            key=f"view_{i}",
            help=f"Market equilibrium is {eq_pct:.1f}%. Move above/below to express a bullish/bearish view.",
        )
        conf = c2.slider(
            f"Your confidence in this view (%)",
            0, 100, 0, 5,
            key=f"conf_{i}",
            help="0% = ignore my view, 100% = override the market completely",
        )
        views.append(view_ret / 100)
        confs.append(conf / 100)
        direction = "above" if view_ret > eq_pct else ("below" if view_ret < eq_pct else "equal to")
        st.caption(
            f"Your view ({view_ret:.1f}%) is {direction} the market equilibrium ({eq_pct:.1f}%), "
            f"with {conf}% confidence."
        )
        st.write("")

    st.divider()

    # ── Posterior ─────────────────────────────────────────────────────────────
    st.subheader("Step 3 — The Blended Result")
    st.markdown(
        "The Black-Litterman model now combines the market equilibrium and your views. "
        "The chart below shows what changes — and by how much."
    )

    pi_out, mu_bl = bl_posterior(w_mkt, SIGMA, DELTA, views, confs)

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        name="Market Equilibrium",
        x=ASSETS,
        y=pi_out * 100,
        marker_color="#95a5a6",
        text=[f"{v*100:.1f}%" for v in pi_out],
        textposition="outside",
    ))
    fig_compare.add_trace(go.Bar(
        name="BL Posterior (your blend)",
        x=ASSETS,
        y=mu_bl * 100,
        marker_color=["#3498db", "#2ecc71", "#e67e22"],
        text=[f"{v*100:.1f}%" for v in mu_bl],
        textposition="outside",
    ))
    fig_compare.update_layout(
        barmode="group",
        title="Equilibrium vs. Black-Litterman Posterior Returns",
        yaxis_title="Expected Annual Return (%)",
        yaxis=dict(ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=380,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # Plain-English deltas
    for i, asset in enumerate(ASSETS):
        delta_ret = (mu_bl[i] - pi_out[i]) * 100
        if abs(delta_ret) < 0.05:
            st.caption(f"**{asset}**: unchanged from market equilibrium ({mu_bl[i]*100:.1f}%)")
        else:
            arrow = "up" if delta_ret > 0 else "down"
            st.caption(
                f"**{asset}**: nudged {arrow} by {abs(delta_ret):.2f} percentage points "
                f"→ {mu_bl[i]*100:.1f}% (was {pi_out[i]*100:.1f}%)"
            )

    st.divider()

    # ── Portfolio weights ──────────────────────────────────────────────────────
    st.subheader("Step 4 — How Does This Change the Portfolio?")
    st.markdown(
        "Higher expected returns attract more allocation. "
        "The chart below shows how the optimal weights shift once your views are blended in. "
        "*(Weights are re-scaled to sum to 100% for easy comparison.)*"
    )

    w_eq = bl_weights(pi_out, SIGMA, DELTA)
    w_bl = bl_weights(mu_bl, SIGMA, DELTA)

    # Clip negatives for display (explain short-selling is outside scope)
    w_eq_disp = np.clip(w_eq, 0, None); w_eq_disp /= w_eq_disp.sum()
    w_bl_disp = np.clip(w_bl, 0, None); w_bl_disp /= w_bl_disp.sum()

    fig_wts = go.Figure()
    fig_wts.add_trace(go.Bar(
        name="Market Starting Weights",
        x=ASSETS,
        y=w_mkt * 100,
        marker_color="#95a5a6",
        text=[f"{v*100:.1f}%" for v in w_mkt],
        textposition="outside",
    ))
    fig_wts.add_trace(go.Bar(
        name="Optimal Weights (Equilibrium)",
        x=ASSETS,
        y=w_eq_disp * 100,
        marker_color="#bdc3c7",
        text=[f"{v*100:.1f}%" for v in w_eq_disp],
        textposition="outside",
    ))
    fig_wts.add_trace(go.Bar(
        name="Optimal Weights (BL — Your Views)",
        x=ASSETS,
        y=w_bl_disp * 100,
        marker_color=["#3498db", "#2ecc71", "#e67e22"],
        text=[f"{v*100:.1f}%" for v in w_bl_disp],
        textposition="outside",
    ))
    fig_wts.update_layout(
        barmode="group",
        title="Portfolio Weights: Market vs. Equilibrium Optimal vs. Your BL Blend",
        yaxis_title="Weight (%)",
        yaxis=dict(ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
    )
    st.plotly_chart(fig_wts, use_container_width=True)

    st.divider()

    # ── FAQ / extra context ───────────────────────────────────────────────────
    with st.expander("Frequently asked questions"):
        st.markdown(
            """
**Q: Why not just use my own expected returns directly?**

You can — but raw mean-variance optimisation is notoriously sensitive.
A 0.1% change in a single expected return can flip a 10% allocation to 60%.
BL damps this by pulling everything back toward the market equilibrium, so small
changes in views produce small, sensible changes in weights.

**Q: What is "risk aversion" (delta)?**

It measures how much extra return an investor demands per unit of risk.
A delta of ~2.5 is typical for a diversified institutional portfolio.
Higher delta = more conservative, lower allocation to risky assets.

**Q: What does "tau" mean?**

Tau (τ) controls how much weight to give the equilibrium vs. the views overall.
A common choice is 0.05 (5%). It is a model-level dial, not an asset-level one.
In practice, the exact value matters less than the relative confidences you assign.

**Q: Can I have a view on *relative* performance (e.g. stocks will beat bonds)?**

Yes — the full BL model supports relative views (called "tilt views") via the P matrix.
This simplified version only supports absolute views (one per asset) to keep the
interface intuitive. Most real implementations support both.

**Q: This doesn't look like the formula I saw in a textbook.**

The formula — μ_BL = [(τΣ)⁻¹ + P'Ω⁻¹P]⁻¹ [(τΣ)⁻¹π + P'Ω⁻¹Q] — is used here exactly,
with P set to the identity matrix (one absolute view per asset) for clarity.
            """
        )

    with st.expander("The one-sentence summary"):
        st.markdown(
            "> **Black-Litterman = market common sense + your personal views, "
            "blended in proportion to how confident you are in each.**"
        )
