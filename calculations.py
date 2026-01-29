import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.optimize as opt

# Generates the difference between the provided op_equity_value and the one computed via DCF
def compute_op_value(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # roe, rir, g_steady in %
    k = 1 - rir / 100
    g_exog = roe * rir / 10000
    r_growth = (1 + g_exog) / (1 + coe / 100)
    sum_growth = sum(r_growth ** (t + 1) for t in range(int(n_exog)))
    factor_terminal = ((1 + g_exog) ** n_exog * (1 + g_steady / 100) / 
                       (coe / 100 - g_steady / 100) / (1 + coe / 100) ** n_exog)
    total_factor = sum_growth + factor_terminal
    computed = net_inc * k * total_factor / 1000
    return op_equity_value - computed

# Has similar claculation structure as compute_op_value, but also generates the plot
def plot_cash_flows(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady, calc_param_name=None, calc_param_value=None):
    FCFE = net_inc * (1 - rir / 100)
    g_exog = (roe / 100) * (rir / 100)

    undiscounted_cf = []
    discounted_cf = []

    if n_exog == 0:
        undiscounted_cf = np.array([FCFE*(1+g_steady/100)**t for t in range(1, 6)])
        growth_value = 0
        terminal_value = FCFE * (1 + g_steady / 100) / (coe / 100 - g_steady / 100)
        pv_terminal_value = terminal_value
    else:
        FCFE_growth_phase = np.array([FCFE * (1 + g_exog) ** t for t in range(1,int(n_exog)+1)])
        steady_cf = np.array([FCFE_growth_phase[-1]*(1+g_steady/100)**t for t in range(1, 6)])
        undiscounted_cf = np.concatenate([FCFE_growth_phase, steady_cf])
        growth_value = np.sum(FCFE_growth_phase)
        steady_state_FCFE = FCFE_growth_phase[-1] * (1 + g_steady / 100)
        terminal_value = steady_state_FCFE / (coe / 100 - g_steady / 100)
        pv_terminal_value = terminal_value / ((1 + coe / 100) ** n_exog)

    discount_factors = np.array([(1 + coe / 100) ** t for t in range(1, int(n_exog) + 6)])
    discounted_cf = undiscounted_cf / discount_factors

    op_equity_value = (growth_value + pv_terminal_value) / 1000  # in billions
    ratio = pv_terminal_value / growth_value if growth_value != 0 else 0
    
    years = [i for i in range(1, int(n_exog) + 6)]
    df = pd.DataFrame({
        'Year': years,
        'Undiscounted CF': undiscounted_cf,
        'Discounted CF': discounted_cf
    })

    #
    # Add an ellipsis row (no bars)
    df_ellipsis = pd.DataFrame({
        'Year': ['…'],
        'Undiscounted CF': [np.nan],
        'Discounted CF': [np.nan]
    })

    df_plot = pd.concat([df, df_ellipsis], ignore_index=True)

    #
    fig, ax1 = plt.subplots(1, 1, figsize=(8, 5))
    
    df_plot.plot(x='Year', y=['Undiscounted CF', 'Discounted CF'], kind='bar', ax=ax1, rot=0)
    ax1.set_xlabel('Years from now')
    ax1.set_ylabel('Cash Flow ($ millions)')
    ax1.set_title('Cash Flow Projections (Extraordinary Growth years & 5 Steady State Years)')
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

    if calc_param_name:
        text_str = f"Calculated {calc_param_name} = {calc_param_value:.2f}\n\n PV of Terminal Phase = {ratio:.1f} x PV of Growth Phase"
        ax1.text(0.5, 0.95, text_str, ha='center', va='top', transform=ax1.transAxes, fontsize=8, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0))
    else:
        text_str =  f"PV of Terminal Phase = {ratio:.1f} x PV of Growth Phase"
        ax1.text(0.5, 0.95, text_str, ha='center', va='top', transform=ax1.transAxes, fontsize=8, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0))
    
    ax1.text(0.95, 0.5, ". . . ", ha='center', va='top', transform=ax1.transAxes, fontsize=28, bbox=dict(boxstyle=None, facecolor=None, alpha=0))

    plt.tight_layout()
    return fig

# --------------------------------------------------------------------------------------------------------------------       
# Calculation functions for each parameter

# This is just DCF. Yes the app has DCF just in case someone wants to use it that way.
def calc_op_equity_value(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    calculated_op_equity_value = -compute_op_value(0, net_inc, roe, rir, coe, n_exog, g_steady)
    return plot_cash_flows(calculated_op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady, "Op Equity Value ($ Billions)", calculated_op_equity_value)

# Although net income can be calculated directly, we use root-finding using numerical methods for consistency
def calc_net_inc(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate net_inc
    calculated_net_inc = opt.brentq(lambda ni: compute_op_value(op_equity_value, ni, roe, rir, coe, n_exog, g_steady), 0, 100000)
    
    return plot_cash_flows(op_equity_value, calculated_net_inc, roe, rir, coe, n_exog, g_steady, "Net Inc. ($ millions)", calculated_net_inc)

# All functions are implemented using root-finding using numerical methods
def calc_roe(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate roe
    try:
        calculated_roe = opt.brentq(lambda r: compute_op_value(op_equity_value, net_inc, r, rir, coe, n_exog, g_steady), 0.01, 100)
    except ValueError:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        ax1.text(0.5, 0.5, "No valid ROE solution found within reasonable bounds (0.01% to 100%).\nPlease check your input values.", 
                 ha='center', va='center', fontsize=14, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
        return fig
     
    return plot_cash_flows(op_equity_value, net_inc, calculated_roe, rir, coe, n_exog, g_steady, "Return on equity (%)", calculated_roe)


def calc_rir(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate rir
    try:
        calculated_rir = opt.brentq(lambda r: compute_op_value(op_equity_value, net_inc, roe, r, coe, n_exog, g_steady), 0.01, 99.99)
    except ValueError:
        raise ValueError("No valid RIR solution found within reasonable bounds (0.01% to 99.99%). Please check your input values.")
    
    return plot_cash_flows(op_equity_value, net_inc, roe, calculated_rir, coe, n_exog, g_steady, "Reinvestment rate (%)", calculated_rir)

def calc_coe(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate coe
    try:
        calculated_coe = opt.brentq(lambda c: compute_op_value(op_equity_value, net_inc, roe, rir, c, n_exog, g_steady), 0.01, 30)
    except ValueError:
        raise ValueError("No valid COE solution found within reasonable bounds (0.01% to 100%). Please check your input values.")
    
    return plot_cash_flows(op_equity_value, net_inc, roe, rir, calculated_coe, n_exog, g_steady, "Cost of equity (%)", calculated_coe)

# The no. of extraordinary growth years is an integer, so we do a loop instead of root-finding
def calc_n_exog(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate n_exog (using loop for integer)
    best_n = 0
    min_diff = float('inf')
    for n in range(21):  # 0 to 20
        diff = abs(compute_op_value(op_equity_value, net_inc, roe, rir, coe, n, g_steady))
        if diff < min_diff:
            min_diff = diff
            best_n = n
    
    calculated_n_exog = best_n
    
    return plot_cash_flows(op_equity_value, net_inc, roe, rir, coe, calculated_n_exog, g_steady, "Extraordinary growth years", calculated_n_exog)

def calc_g_steady(op_equity_value, net_inc, roe, rir, coe, n_exog, g_steady):
    # Reverse DCF to calculate g_steady
    try:
        calculated_g_steady = opt.brentq(lambda g: compute_op_value(op_equity_value, net_inc, roe, rir, coe, n_exog, g), 0.01, 20)
    except ValueError:
        raise ValueError("No valid steady-state growth solution found within reasonable bounds (0.01% to 20%). Please check your input values.")

    return plot_cash_flows(op_equity_value, net_inc, roe, rir, coe, n_exog, calculated_g_steady, "Steady state growth rate (%)", calculated_g_steady)