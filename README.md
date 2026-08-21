# Fluid Flow & Heat Transfer Engineering Suite

A multi-page Streamlit application built for the PE 262 capstone project.
It bundles three engineering calculators behind a shared, unit-tested,
object-oriented core (`engineering.py`):

| Module | What it does |
|---|---|
| 🔧 **Pipe Flow Analyzer** | Fluid selection (preset or custom), pipe geometry + flow rate → velocity, Reynolds number, Darcy friction factor, pressure drop (Darcy-Weisbach). Interactive pressure-drop-vs-flow-rate curve, CSV export. |
| 🌡️ **Heat Transfer Calculator** | Steady-state 1D conduction through a flat wall (Fourier's Law), and Newton's Law of Cooling with an interactive temperature-vs-time curve and time-to-target calculation. |
| 📊 **Rock & Fluid Data Dashboard** | Upload a CSV of rock/fluid sample data, get summary statistics, filter interactively, view a histogram and a porosity-permeability crossplot, and download the filtered data. |

## Live app

https://capstone-project-kaduweq3jtby6y8us6o4rc.streamlit.app/

## Project structure

```
.
├── Home.py                              # Landing page / entry point
├── engineering.py                       # OOP engineering core (Fluid, Pipe, FlatWall, CoolingBody)
├── pages/
│   ├── 1_🔧_Pipe_Flow_Analyzer.py
│   ├── 2_🌡️_Heat_Transfer_Calculator.py
│   └── 3_📊_Rock_Fluid_Dashboard.py
├── sample_data/
│   └── rock_fluid_sample.csv            # Synthetic dataset for testing Module C
├── requirements.txt
└── README.md
```

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub (see below).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, and click
   **New app**.
3. Select this repo, branch `main`, and main file path `Home.py`.
4. Deploy. Copy the resulting URL into the **Live app** section above and
   into your submission.

## Pushing this repo to GitHub

```bash
cd capstone
git init
git add .
git commit -m "Initial commit: project scaffold"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

The grading rubric asks for **at least 5 meaningful commits** — don't just
squash everything into one. A natural sequence, made as you actually build
and test each piece:

1. `Add engineering.py core classes (Fluid, Pipe, FlatWall, CoolingBody)`
2. `Add Pipe Flow Analyzer page`
3. `Add Heat Transfer Calculator page`
4. `Add Rock & Fluid Data Dashboard page + sample dataset`
5. `Add README, requirements, and deployment config`
6. (any bug fixes / polish you make after testing on Streamlit Cloud)

## Testing notes

`engineering.py` was sanity-checked against hand/analytical calculations
before wiring it into the UI, e.g.:
- Water at ~2.3 m/s through a 52.5 mm pipe gives Re ≈ 1.2×10⁵ (turbulent), a
  Darcy friction factor ≈ 0.021, matching a Moody-chart read for that
  relative roughness.
- A 0.2 m concrete-like wall (k = 0.8 W/m·K) with a 35°C difference gives a
  heat flux of 140 W/m², matching `k·ΔT/L` by hand.
- A lumped body with h·A small relative to m·cp gives a multi-hour time
  constant, and `time_to_reach` inverts `temperature_at` correctly (checked
  by round-tripping a few values).

## AI usage disclosure

1. Prompt: "Build the full capstone app described in this brief" — Produced: the initial engineering.py core classes and all three Streamlit pages. Verified: ran the app, tested each calculator against known physics behavior (e.g. checked that pressure drop increases with flow rate, that a wall with a bigger temperature difference produces more heat flux), and read through engineering.py to understand each formula before accepting it.

2. Prompt: "Take me through deploying this step by step" — Produced: setup instructions for GitHub, Codespaces, and Streamlit Cloud. Verified/corrected: hit several real issues along the way not covered by the initial instructions — files uploaded into a nested subfolder instead of the repo root (had to move them manually), a custom theme file that silently failed to save the first time, and a stale running process that made file edits look like they weren't taking effect. Diagnosed and fixed each by checking file contents and running processes directly rather than assuming the first fix worked.

3. Prompt: "I want a light/dark theme toggle with my custom colors" — Produced: an initial two-color theme config that accidentally disabled the toggle entirely (a real Streamlit limitation), then a corrected config using [theme.light]/[theme.dark] sections after confirming that syntax actually existed for my Streamlit version.

## License / academic integrity note

Built for coursework (PE 262 capstone). Every function and method has a
docstring; make sure you can explain each calculation and each Streamlit
call before submitting — that's the actual point of the assignment.
