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

tabs = st.tabs(["📈 Yield Curve", "⏱ Duration", "💵 Price Sensitivity"])


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
