"""
1_🔧_Pipe_Flow_Analyzer.py
===========================
Module A — Pipe Flow Analyzer.

Lets the user pick a fluid (preset or user-defined), set pipe geometry and
flow rate, and see velocity / Reynolds number / friction factor / pressure
drop, an interactive pressure-drop-vs-flow-rate curve, and a CSV export.
"""

import os
import sys

import pandas as pd
import streamlit as st

# Make sure engineering.py (in the project root) is importable regardless of
# the working directory Streamlit is launched from.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engineering import Fluid, Pipe  # noqa: E402

st.set_page_config(page_title="Pipe Flow Analyzer", page_icon="🔧", layout="wide")

st.markdown(
    """
<div style="background-color:#0b1c33; padding:1.8rem 2.2rem 2.1rem 2.2rem; border-radius:10px; margin-bottom:1.6rem;">
<h1 style="color:white; font-size:2.1rem; font-weight:800; margin:0 0 0.6rem 0; line-height:1.2;">🔧 Pipe Flow Analyzer</h1>
<p style="color:#a9b7c9; font-size:0.95rem; margin:0;">Circular pipe, single fluid, steady incompressible flow. Friction factor uses the exact laminar solution below Re = 2300 and the Swamee-Jain approximation to Colebrook-White above it.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- Sidebar --
st.sidebar.header("Fluid")

fluid_choice = st.sidebar.selectbox(
    "Fluid",
    list(Fluid.PRESET_FLUIDS.keys()) + ["User-defined"],
    help="Pick a preset fluid (properties auto-fill below) or define your own.",
)

if fluid_choice == "User-defined":
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.0001, value=1000.0, step=10.0,
        help="Mass per unit volume of the fluid.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", min_value=1e-7, value=1.0e-3,
        step=1e-4, format="%.6f",
        help="Resistance of the fluid to shear/flow. Water ≈ 0.001 Pa·s.",
    )
else:
    preset = Fluid.PRESET_FLUIDS[fluid_choice]
    density = st.sidebar.number_input(
        "Density (kg/m³)", value=float(preset["density"]),
        help="Auto-filled from the preset. Edit to override.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", value=float(preset["viscosity"]),
        format="%.6f",
        help="Auto-filled from the preset. Edit to override.",
    )

st.sidebar.header("Pipe geometry")
diameter_mm = st.sidebar.number_input(
    "Internal diameter D (mm)", min_value=0.1, value=52.5, step=1.0,
    help="Internal (bore) diameter of the pipe, in millimetres.",
)
length_m = st.sidebar.number_input(
    "Pipe length L (m)", min_value=0.01, value=50.0, step=1.0,
    help="Total straight-line length of pipe the fluid travels through.",
)
roughness_mm = st.sidebar.number_input(
    "Absolute roughness ε (mm)", min_value=0.0, value=0.045, step=0.001,
    format="%.4f",
    help="Height of surface irregularities on the pipe's inner wall. "
         "Commercial steel ≈ 0.045 mm, PVC ≈ 0.0015 mm.",
)

st.sidebar.header("Flow")
flow_rate_lpm = st.sidebar.number_input(
    "Flow rate Q (L/min)", min_value=0.0, value=300.0, step=10.0,
    help="Volumetric flow rate through the pipe, in litres per minute.",
)

# ------------------------------------------------------------- Calculate --
try:
    fluid = Fluid(fluid_choice, density, viscosity)
    pipe = Pipe(
        diameter=diameter_mm / 1000.0,
        length=length_m,
        roughness=roughness_mm / 1000.0,
        fluid=fluid,
        flow_rate=flow_rate_lpm / 1000.0 / 60.0,  # L/min -> m^3/s
    )

    velocity = pipe.velocity()
    re = pipe.reynolds_number()
    f = pipe.friction_factor()
    dp_pa = pipe.pressure_drop()

    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{velocity:.3f} m/s")
    c2.metric("Reynolds number", f"{re:,.0f}", pipe.flow_regime())
    c3.metric("Friction factor (Darcy)", f"{f:.4f}")
    c4.metric("Pressure drop", f"{dp_pa/1000:.2f} kPa", f"{dp_pa:.0f} Pa")

    st.divider()

    # ------------------------------------------------------- dP vs Q plot --
    st.subheader("Pressure drop vs. flow rate")
    max_q_lpm = max(flow_rate_lpm * 2, 10.0)
    q_range_lpm = [max_q_lpm * i / 100 for i in range(1, 101)]
    dp_values_kpa = []
    for q in q_range_lpm:
        trial_pipe = Pipe(
            diameter=diameter_mm / 1000.0,
            length=length_m,
            roughness=roughness_mm / 1000.0,
            fluid=fluid,
            flow_rate=q / 1000.0 / 60.0,
        )
        dp_values_kpa.append(trial_pipe.pressure_drop() / 1000.0)

    curve_df = pd.DataFrame({"Flow rate (L/min)": q_range_lpm, "Pressure drop (kPa)": dp_values_kpa})
    st.line_chart(curve_df, x="Flow rate (L/min)", y="Pressure drop (kPa)")

    st.divider()

    # ------------------------------------------------------------ Export --
    st.subheader("Export")
    export_df = pd.DataFrame({
        "Flow rate (L/min)": q_range_lpm,
        "Pressure drop (kPa)": dp_values_kpa,
    })
    export_df.loc[len(export_df)] = ["--- current operating point ---", ""]
    export_df.loc[len(export_df)] = [flow_rate_lpm, dp_pa / 1000.0]

    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download curve + operating point as CSV",
        data=csv_bytes,
        file_name="pipe_flow_results.csv",
        mime="text/csv",
    )

except ValueError as e:
    st.error(f"Input error: {e}")
except ZeroDivisionError:
    st.error("Calculation error: check that diameter and length are non-zero.")
