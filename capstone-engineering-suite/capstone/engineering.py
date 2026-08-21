"""
engineering.py
================
Core engineering classes for the Fluid Flow & Heat Transfer Engineering Suite.

This module contains no Streamlit code — it is pure Python/engineering logic,
kept separate from the UI so it can be unit-tested and reused across pages
(satisfies the "OOP in a separate module" requirement of the capstone).

Classes
-------
Fluid         - a fluid's density/viscosity properties, with presets
Pipe          - circular pipe flow calculations (velocity, Re, friction, dP)
FlatWall      - steady-state 1D conduction through a single-layer wall
CoolingBody   - lumped-capacitance Newton's Law of Cooling model
"""

import math


class Fluid:
    """Represents a fluid with density and dynamic viscosity properties.

    Attributes:
        name (str): Descriptive name of the fluid.
        density (float): Density in kg/m^3.
        viscosity (float): Dynamic viscosity in Pa*s.
    """

    # Approximate properties at ~20 C, 1 atm. Good enough for a teaching tool;
    # real design work should pull from a proper fluid property table.
    PRESET_FLUIDS = {
        "Water (20°C)": {"density": 998.2, "viscosity": 1.002e-3},
        "Air (20°C, 1 atm)": {"density": 1.204, "viscosity": 1.825e-5},
        "Crude Oil (medium, 20°C)": {"density": 870.0, "viscosity": 8.0e-3},
    }

    def __init__(self, name: str, density: float, viscosity: float):
        """Create a Fluid.

        Args:
            name: Descriptive label for the fluid.
            density: Density in kg/m^3. Must be positive.
            viscosity: Dynamic viscosity in Pa*s. Must be positive.

        Raises:
            ValueError: If density or viscosity is not positive.
        """
        if density <= 0:
            raise ValueError("Density must be a positive number (kg/m^3).")
        if viscosity <= 0:
            raise ValueError("Viscosity must be a positive number (Pa*s).")
        self.name = name
        self.density = density
        self.viscosity = viscosity

    @classmethod
    def from_preset(cls, preset_name: str) -> "Fluid":
        """Build a Fluid from one of the built-in presets.

        Args:
            preset_name: A key in Fluid.PRESET_FLUIDS.

        Returns:
            A Fluid instance with the preset's properties.

        Raises:
            ValueError: If preset_name is not a known preset.
        """
        if preset_name not in cls.PRESET_FLUIDS:
            raise ValueError(f"Unknown preset fluid: '{preset_name}'.")
        props = cls.PRESET_FLUIDS[preset_name]
        return cls(preset_name, props["density"], props["viscosity"])

    def __repr__(self):
        return f"Fluid({self.name}, ρ={self.density} kg/m^3, μ={self.viscosity} Pa·s)"


class Pipe:
    """Represents a circular pipe carrying a fluid, with flow calculations.

    All calculations use SI units internally (metres, m^3/s, Pa) even though
    the Streamlit UI layer may accept and display other units.
    """

    def __init__(self, diameter: float, length: float, roughness: float,
                 fluid: Fluid, flow_rate: float):
        """Create a Pipe.

        Args:
            diameter: Internal diameter in metres. Must be positive.
            length: Pipe length in metres. Must be positive.
            roughness: Absolute (internal wall) roughness in metres. Must be >= 0.
            fluid: A Fluid instance carried by the pipe.
            flow_rate: Volumetric flow rate in m^3/s. Must be >= 0.

        Raises:
            ValueError: If any dimension is invalid.
        """
        if diameter <= 0:
            raise ValueError("Pipe diameter must be positive (m).")
        if length <= 0:
            raise ValueError("Pipe length must be positive (m).")
        if roughness < 0:
            raise ValueError("Roughness cannot be negative (m).")
        if flow_rate < 0:
            raise ValueError("Flow rate cannot be negative (m^3/s).")
        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.fluid = fluid
        self.flow_rate = flow_rate

    def area(self) -> float:
        """Cross-sectional flow area in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    def velocity(self) -> float:
        """Average flow velocity in m/s."""
        a = self.area()
        return self.flow_rate / a if a > 0 else 0.0

    def reynolds_number(self) -> float:
        """Reynolds number (dimensionless): Re = rho*v*D/mu."""
        v = self.velocity()
        return (self.fluid.density * v * self.diameter) / self.fluid.viscosity

    def friction_factor(self) -> float:
        """Darcy friction factor.

        Uses the exact laminar solution (f = 64/Re) below Re = 2300, and the
        Swamee-Jain explicit approximation to the Colebrook-White equation
        for turbulent flow (accurate to within ~1-2% of Colebrook over the
        normal engineering range).

        Returns:
            Dimensionless Darcy friction factor. 0.0 if there is no flow.
        """
        re = self.reynolds_number()
        if re <= 0:
            return 0.0
        if re < 2300:
            return 64.0 / re
        rel_rough = self.roughness / self.diameter
        denom = math.log10((rel_rough / 3.7) + (5.74 / (re ** 0.9)))
        return 0.25 / (denom ** 2)

    def pressure_drop(self) -> float:
        """Pressure drop along the pipe in Pa (Darcy-Weisbach equation).

        dP = f * (L/D) * (rho * v^2 / 2)
        """
        f = self.friction_factor()
        v = self.velocity()
        return f * (self.length / self.diameter) * (self.fluid.density * v ** 2) / 2.0

    def flow_regime(self) -> str:
        """Human-readable flow regime based on Reynolds number."""
        re = self.reynolds_number()
        if re < 2300:
            return "Laminar"
        if re < 4000:
            return "Transitional"
        return "Turbulent"

    def __repr__(self):
        return (f"Pipe(D={self.diameter} m, L={self.length} m, "
                f"fluid={self.fluid.name}, Q={self.flow_rate} m^3/s)")


class FlatWall:
    """Steady-state 1D conduction through a single-layer flat wall (Fourier's Law)."""

    def __init__(self, k: float, area: float, thickness: float,
                 t_hot: float, t_cold: float):
        """Create a FlatWall.

        Args:
            k: Thermal conductivity of the wall material, W/(m*K). Must be positive.
            area: Cross-sectional area normal to heat flow, m^2. Must be positive.
            thickness: Wall thickness, m. Must be positive.
            t_hot: Hot-face temperature (deg C or K, consistent with t_cold).
            t_cold: Cold-face temperature (same units as t_hot).

        Raises:
            ValueError: If k, area, or thickness is not positive.
        """
        if k <= 0:
            raise ValueError("Thermal conductivity k must be positive (W/m·K).")
        if area <= 0:
            raise ValueError("Area must be positive (m^2).")
        if thickness <= 0:
            raise ValueError("Thickness must be positive (m).")
        self.k = k
        self.area = area
        self.thickness = thickness
        self.t_hot = t_hot
        self.t_cold = t_cold

    def heat_flux(self) -> float:
        """Heat flux through the wall, W/m^2 (Fourier's Law: q = k*dT/L)."""
        return self.k * (self.t_hot - self.t_cold) / self.thickness

    def heat_rate(self) -> float:
        """Total heat transfer rate through the wall, W (Q = q * A)."""
        return self.heat_flux() * self.area

    def __repr__(self):
        return f"FlatWall(k={self.k}, A={self.area}, L={self.thickness})"


class CoolingBody:
    """Lumped-capacitance model of a body cooling per Newton's Law of Cooling.

    Governing ODE:  m*cp*(dT/dt) = -h*A*(T - T_ambient)
    Solution:       T(t) = T_ambient + (T0 - T_ambient) * exp(-t / tau)
                    where tau = m*cp / (h*A)
    """

    def __init__(self, h: float, area: float, mass: float,
                 specific_heat: float, t_ambient: float):
        """Create a CoolingBody.

        Args:
            h: Convective heat transfer coefficient, W/(m^2*K). Must be positive.
            area: Surface area exposed to the ambient fluid, m^2. Must be positive.
            mass: Mass of the body, kg. Must be positive.
            specific_heat: Specific heat capacity, J/(kg*K). Must be positive.
            t_ambient: Ambient (surrounding fluid) temperature.

        Raises:
            ValueError: If h, area, mass, or specific_heat is not positive.
        """
        if h <= 0:
            raise ValueError("Convective coefficient h must be positive (W/m^2·K).")
        if area <= 0:
            raise ValueError("Surface area must be positive (m^2).")
        if mass <= 0:
            raise ValueError("Mass must be positive (kg).")
        if specific_heat <= 0:
            raise ValueError("Specific heat must be positive (J/kg·K).")
        self.h = h
        self.area = area
        self.mass = mass
        self.cp = specific_heat
        self.t_ambient = t_ambient

    def time_constant(self) -> float:
        """Thermal time constant tau, in seconds."""
        return (self.mass * self.cp) / (self.h * self.area)

    def temperature_at(self, t: float, t0: float) -> float:
        """Body temperature at time t (seconds) given initial temperature t0."""
        tau = self.time_constant()
        return self.t_ambient + (t0 - self.t_ambient) * math.exp(-t / tau)

    def time_to_reach(self, t0: float, t_target: float) -> float:
        """Time (seconds) required to cool/heat from t0 to t_target.

        Raises:
            ValueError: If t_target is unreachable (equals ambient, equals t0,
                or is on the wrong side of ambient relative to t0).
        """
        if t0 == self.t_ambient:
            raise ValueError("Initial temperature equals ambient; body is already at equilibrium.")
        if t_target == self.t_ambient:
            raise ValueError("Target temperature equals ambient; this is only reached as t -> infinity.")
        ratio = (t_target - self.t_ambient) / (t0 - self.t_ambient)
        if ratio <= 0:
            raise ValueError(
                "Target temperature is not reachable: it lies on the wrong side "
                "of the ambient temperature relative to the starting temperature."
            )
        if ratio >= 1:
            raise ValueError(
                "Target temperature is not further from ambient-approach than the "
                "starting temperature; check T0 and Ttarget."
            )
        tau = self.time_constant()
        return -tau * math.log(ratio)

    def __repr__(self):
        return f"CoolingBody(h={self.h}, A={self.area}, m={self.mass}, cp={self.cp})"
