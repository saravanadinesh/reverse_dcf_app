import streamlit as st
from calculations import (
    calc_op_equity_value,
    calc_net_inc,
    calc_roe,
    calc_rir,
    calc_coe,
    calc_n_exog,
    calc_g_steady,
)

st.set_page_config(layout="wide")
#color: rgba(255,255,255,0.85);

# --- Global CSS to control spacing (Option 1) ---
st.markdown(
    """
    <style>
      /* Label above each input */
      .input-label {
        margin-top: 6px;     /* space from previous input */
        margin-bottom: 2px;   /* tight label -> input */
        font-size: 0.85rem;
      }

      /* Reduce extra whitespace around Streamlit text inputs */
      div[data-testid="stTextInput"] {
        margin-top: 0px;
        margin-bottom: 0px;
      }

      /* Optional: tighten radio/button spacing a bit */
      div[data-testid="stRadio"] {
        margin-bottom: 8px;
      }
      div[data-testid="stButton"] {
        margin-top: 12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar (collapsible) ----------------
with st.sidebar:
    st.header("Input Panel")

    options = [
        "Op Equity Value ($ Billions)",
        "Net Inc. ($ millions)",
        "Return on equity (%)",
        "Reinvestment rate (%)",
        "Cost of equity (%)",
        "Extraordinary growth years",
        "Steady state growth rate (%)",
    ]
    infos = [
        "Operating equity value",
        "Latest annual net income",
        "Return on equity",
        "Reinvestment rate",
        "Cost of equity",
        "Extraordinary growth years",
        "Terminal phase growth rate",
    ]
    defaults = ["15", "1000", "12", "40", "10", "5", "5"]

    calc_option = st.radio("Calc", options)

    inputs = []
    for i, (opt, info, default) in enumerate(zip(options, infos, defaults)):
        # Structural improvement: container per (label + input) pair
        with st.container():
            st.markdown(
                f"<div class='input-label' title='{info}'>{opt}</div>",
                unsafe_allow_html=True,
            )
            inp = st.text_input(
                label="",
                value=default,
                disabled=(calc_option == opt),
                key=f"input_{i}",
                label_visibility="collapsed",
            )
            inputs.append(inp)

    if st.button("Go", type="primary"):
        try:
            values = [float(inp) for inp in inputs]
            func_map = {
                "Op Equity Value ($ Billions)": calc_op_equity_value,
                "Net Inc. ($ millions)": calc_net_inc,
                "Return on equity (%)": calc_roe,
                "Reinvestment rate (%)": calc_rir,
                "Cost of equity (%)": calc_coe,
                "Extraordinary growth years": calc_n_exog,
                "Steady state growth rate (%)": calc_g_steady,
            }
            st.session_state["fig"] = func_map[calc_option](*values)
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

# ---------------- Main page output ----------------
tab_main, tab_help = st.tabs(["Reverse DCF", "Help"])

with tab_main:
    # put everything currently in your main-page output panel here
    #st.header("Output Panel")
    col_left, col_plot, col_right = st.columns([0.1, 0.8, 0.1])
    with col_plot:
        if "fig" in st.session_state:
            st.pyplot(st.session_state["fig"], use_container_width=True)

with tab_help:
    st.markdown("""
                *If you have questions or comments, please reach out to me, [Dinesh Thogulua](https://www.linkedin.com/in/dinesh-thogulua/), 
                on LinkedIn (Just connect with me if you can't message directly. Thanks).*
                """)
    st.header("Description")
    st.markdown(
        """
        Discounted Cash Flow (DCF) models are used to estimate the intrinsic value of the equity in a firm. 
        The idea is to identify if the market is pricing the equity higher or lower than the intrinsic value estimated by the model 
        and make investing decisions accordingly. But what if you want to find out what assumptions the market is using to price the equity 
        (assuming they are all using intrinsic valuation)? Reverse DCF essentially revense engineers the market's assumption about one of the 
        key parameters in the DCF model given other input parameters that the user thinks are reasonable.

        ### DCF Equation
        The DCF model used here has two phases: extraordinary growth phase and steady state phase. The idea is that most companies have these
        two phases. The first phase is when the company is growing rapidly due to competitive advantages, new products, market expansion, etc.
        The second phase is when the company has matured, and the market itself has matured. The growth rate in this steady state phase is expected 
        to be much more modest, because, by then, competition would have emerged and market penetration would have increased significantly.  

        DCF simply takes the projected cash flows from these two phases and discounts them back to present value using the cost of equity. Free
        cash flows to the equity owner (FCFE) are nothing but the net income less the reinvestment needs of the company. Although FCFE doesn't 
        represent the actual cash flow to equity holders, it is a useful proxy for valuation purposes as a "could-be dividend", if you will

        One can picture DCF in the same way as valuing a bond with coupon payments (cash flows during the growth phase) and a face value 
        (terminal value, a.k.a. steady state value of the company). 

        $$
            \\text{Op Equity Value} = \dfrac{FCFE \\times (1+g)}{(1+COE)^1} + \dfrac{FCFE \\times (1+g)^2}{(1+COE)^2} + ... + \dfrac{FCFE \\times (1+g)^n}{(1+COE)^{n}} + \dfrac{TV}{(1+COE)^{n}}
        $$

        where TV is the terminal value calculated as:
        $$
            TV = \dfrac{FCFE \\times (1+g)^n \\times(1+g_{steady})}{COE - g_{steady}}
        $$

        Here, the variables are defined as:
        - Op Equity Value: Operating equity value of the firm (in $ billions)
        - FCFE: Free cash flow to equity in year t (in $ millions)
        - g: Growth rate during extraordinary growth phase = ROE × RIR (ROE: return on equity, RIR: reinvestment rate)
        - g_steady: Growth rate during steady state phase (terminal growth rate)
        - COE: Cost of equity (%)
        - n: Number of years in extraordinary growth phase

        The reason I call it "operating" equity value is that this valuation model does not consider cash on the balance sheet. The actual equity
        value would be operating equity value plus cash. So if you are comparing the model output to market cap, make sure to adjust for cash.

        ### Workflow
        1. Select the parameter to compute (Calc).
        2. Enter values for all other parameters.
        3. Click Go to solve for the selected parameter. It won't work if you just press enter after inputting values.
        
        ### Output
        - Bar chart: projected FCFE (undiscounted vs discounted) for growth + first few steady-state years
        - Text box: solved value and PV(Terminal) relative to PV(Growth). If your inputs are unreasonable, you will see an error message instead.
        """
    )
