"""
2_🌡️_Heat_Transfer_Calculator.py
==================================
Module B — Heat Transfer Calculator.

Two calculations:
  1. Steady-state conduction through a flat wall (Fourier's Law).
  2. Newton's Law of Cooling: time to cool from T0 to Ttarget in an ambient
     Tinf, plus a temperature-vs-time plot.
"""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engineering import FlatWall, CoolingBody  # noqa: E402

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🌡️", layout="wide")
st.title("🌡️ Heat Transfer Calculator")

tab1, tab2 = st.tabs(["🧱 Conduction (Fourier's Law)", "❄️ Newton's Law of Cooling"])

# ============================================================ Conduction ==
with tab1:
    st.subheader("Steady-state conduction through a flat wall")
    st.caption(
        "Single homogeneous layer, 1D heat flow, steady state — "
        "no heat generation inside the wall."
    )

    col1, col2 = st.columns(2)
    with col1:
        k = st.number_input(
            "Thermal conductivity, k (W/m·K)", min_value=0.0001, value=0.8, step=0.05,
            help="How well the wall material conducts heat. "
                 "Concrete ≈ 1.0, glass wool insulation ≈ 0.04, steel ≈ 45.",
        )
        area = st.number_input(
            "Wall area, A (m²)", min_value=0.0001, value=10.0, step=0.5,
            help="Cross-sectional area of the wall, measured perpendicular to heat flow.",
        )
        thickness = st.number_input(
            "Wall thickness, L (m)", min_value=0.0001, value=0.20, step=0.01,
            help="Distance the heat travels through the wall, from hot face to cold face.",
        )
    with col2:
        t_hot = st.number_input(
            "Hot-face temperature (°C)", value=25.0, step=1.0,
            help="Temperature at the warmer surface of the wall.",
        )
        t_cold = st.number_input(
            "Cold-face temperature (°C)", value=-10.0, step=1.0,
            help="Temperature at the cooler surface of the wall.",
        )

    try:
        wall = FlatWall(k=k, area=area, thickness=thickness, t_hot=t_hot, t_cold=t_cold)
        flux = wall.heat_flux()
        rate = wall.heat_rate()

        st.subheader("Results")
        c1, c2 = st.columns(2)
        c1.metric("Heat flux, q\"", f"{flux:.2f} W/m²")
        c2.metric("Heat transfer rate, Q", f"{rate:.1f} W", f"{rate/1000:.3f} kW")

        if t_hot < t_cold:
            st.warning(
                "Hot-face temperature is lower than cold-face temperature — "
                "heat is flowing in the opposite direction to what the labels suggest. "
                "The magnitude above is still correct."
            )
    except ValueError as e:
        st.error(f"Input error: {e}")

# ================================================== Newton's Law of Cooling
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.caption(
        "Lumped-capacitance model: assumes the body's internal temperature is "
        "uniform at every instant (valid for small/well-conducting objects)."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        h = st.number_input(
            "Convective coefficient, h (W/m²·K)", min_value=0.0001, value=15.0, step=1.0,
            help="How effectively the surrounding fluid carries heat away from the "
                 "surface. Still air ≈ 5-25, forced air ≈ 25-250, water ≈ 500+.",
        )
        area_c = st.number_input(
            "Surface area, A (m²)", min_value=0.0001, value=0.5, step=0.05,
            help="Surface area of the body exposed to the ambient fluid.",
        )
    with col2:
        mass = st.number_input(
            "Mass, m (kg)", min_value=0.0001, value=2.0, step=0.1,
            help="Mass of the cooling body.",
        )
        cp = st.number_input(
            "Specific heat, cp (J/kg·K)", min_value=0.0001, value=4186.0, step=10.0,
            help="Energy needed to raise 1 kg of the body's material by 1 K. "
                 "Water ≈ 4186, aluminium ≈ 900, steel ≈ 490.",
        )
    with col3:
        t_ambient = st.number_input(
            "Ambient temperature, T∞ (°C)", value=20.0, step=1.0,
            help="Temperature of the surrounding fluid, assumed constant.",
        )
        t0 = st.slider(
            "Initial temperature, T0 (°C)", min_value=-50, max_value=200, value=90,
            help="Starting temperature of the body at t = 0.",
        )
        t_target = st.slider(
            "Target temperature, Ttarget (°C)", min_value=-50, max_value=200, value=30,
            help="Temperature you want the body to reach.",
        )

    try:
        body = CoolingBody(h=h, area=area_c, mass=mass, specific_heat=cp, t_ambient=t_ambient)
        tau = body.time_constant()

        st.subheader("Results")
        try:
            t_reach = body.time_to_reach(t0, t_target)
            c1, c2 = st.columns(2)
            c1.metric("Thermal time constant, τ", f"{tau:.1f} s", f"{tau/60:.2f} min")
            c2.metric("Time to reach target", f"{t_reach:.1f} s", f"{t_reach/60:.2f} min")

            # ---------------------------------------------------- Plot --
            st.subheader("Temperature vs. time")
            t_end = t_reach * 1.5 if t_reach > 0 else tau * 3
            n_points = 150
            times = [t_end * i / (n_points - 1) for i in range(n_points)]
            temps = [body.temperature_at(t, t0) for t in times]
            plot_df = pd.DataFrame({"Time (s)": times, "Temperature (°C)": temps})
            st.line_chart(plot_df, x="Time (s)", y="Temperature (°C)")
            st.caption(
                f"Curve shown from t = 0 to t ≈ {t_end:.0f} s "
                f"(1.5× the time needed to reach the target)."
            )
        except ValueError as e:
            st.warning(
                f"Can't compute a finite cooling time for these inputs: {e} "
                "The time constant below is still valid."
            )
            c1, c2 = st.columns(2)
            c1.metric("Thermal time constant, τ", f"{tau:.1f} s", f"{tau/60:.2f} min")

    except ValueError as e:
        st.error(f"Input error: {e}")
