"""
Home.py
=======
Landing page for the Fluid Flow & Heat Transfer Engineering Suite.
Run with:  streamlit run Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="Engineering Suite | Home",
    page_icon="🛠️",
    layout="wide",
)

st.markdown(
    """
<div style="background-color:#0b1c33; padding:2rem 2.2rem 2.4rem 2.2rem; border-radius:10px; margin-bottom:1.6rem;">
<h1 style="color:white; font-size:2.4rem; font-weight:800; margin:0 0 0.6rem 0; line-height:1.2;">🛠️ Fluid Flow &amp; Heat Transfer Engineering Suite</h1>
<p style="color:#a9b7c9; font-size:1rem; margin:0;">A complete, deployed engineering toolkit built for PE 262's capstone project.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    Welcome! This is a small toolkit of three engineering calculators, built
    for PE 262's capstone project. Use the sidebar to navigate between them.

    ### Modules

    - **🔧 Pipe Flow Analyzer** — pick a fluid, size a pipe, and see velocity,
      Reynolds number, friction factor, and pressure drop. Includes a
      pressure-drop-vs-flow-rate curve and CSV export.
    - **🌡️ Heat Transfer Calculator** — steady-state conduction through a flat
      wall (Fourier's Law), plus Newton's Law of Cooling with an interactive
      cooling curve.
    - **📊 Rock & Fluid Data Dashboard** — upload a CSV of rock/fluid
      properties, filter it, and explore it with a histogram and a
      porosity-permeability crossplot.

    ### Notes on this build
    - All engineering calculations live in `engineering.py`, kept separate
      from the Streamlit UI code, and are built around a small set of
      classes (`Fluid`, `Pipe`, `FlatWall`, `CoolingBody`).
    - Every function/method has a docstring, and user inputs are validated
      with clear error messages rather than letting the app crash.
    """
)

st.info(
    "Start with **Pipe Flow Analyzer** in the sidebar, or jump straight to "
    "the module you need."
)