import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pid_controller import PIDController


# -------------------------------
# Simulation Parameters and Result Data Classes
# -------------------------------

@dataclass
class SimulationParameters:
    kg: float
    water: float  # Fraction (0-1)
    MJ: float
    Tair: float
    Tbeans: float
    TFC: float
    Toffset: float
    TDry: float
    PostFC: float
    tmax: float  # Total time in minutes
    Speed: float
    Respv: float
    P0: float
    TP: List[str]  # Power settings as strings, e.g., ["50,10:30,80", ...]
    D: float  # Diameter in mm
    rho: float
    Cp: float
    RPM: float
    Ddrum: float  # Diameter in mm
    Ldrum: float  # Length in mm
    Deta: float
    Beta: float

@dataclass
class SimulationResult:
    plots: List[Dict[str, Any]]
    Info: str
    NB: int
    SA: float
    kJb: str
    kJr: str
    Froude: float
    kJRad: str

# -------------------------------
# Main Simulation Function
# -------------------------------

def calc_it(params: SimulationParameters, pid: PIDController, target_profile=None) -> SimulationResult:
    # Constants
    MAX_TEMPERATURE = 1000  # Maximum temperature to prevent overflow (°C)
    MIN_TEMPERATURE = -50    # Minimum temperature (°C) to prevent negative values
    MAX_POWER = 100          # Maximum power (%)
    MIN_POWER = 0            # Minimum power (%)

    # Unit conversions
    kg = params.kg / 1000  # g to kg

    # Adjust Speed
    Speed = params.Speed if params.Speed <= 3 else 6 - params.Speed

    # Initialization
    nsteps = 500  # Increased for smaller time steps
    RoRCorrection = 0.5
    Wfact = 0.0012 * kg / 10
    WEV = 750
    Resp = 10 + (3 - params.Respv) * 3
    PostFCfact = 600
    PostFCJfact = 50

    kgCoffee = kg * (1 - params.water)
    Pnow = 1
    Toven = params.Toffset
    Toveneq = Toven
    MJnow = params.MJ
    MJeq = params.MJ
    DeltaT = 0
    DeltaTM = 0
    Wnow = params.water * kgCoffee
    Wloss = 0
    WMJ = 0
    PostFCloss = 0
    PostFCJ = 0
    tnow = 0
    tstep = params.tmax / nsteps
    TbMeasure = Toven

    # Data storage for plotting
    ITPts = [{'x': 0, 'y': params.Tair}]
    OPts = [{'x': 0, 'y': Toven}]
    BPts = [{'x': 0, 'y': TbMeasure}]
    TBPts = [{'x': 0, 'y': params.Tbeans}]
    KPts = []
    WPts = []
    ROR = []
    PPts = [{'x': 0, 'y': params.P0}]

    # Radiative Heat Loss Parameters
    Stefan = 5.6703e-8
    Ddrum_m = params.Ddrum / 1000  # mm to m
    Ldrum_m = params.Ldrum / 1000  # mm to m
    DrumArea = np.pi * Ddrum_m * Ldrum_m
    BeanArea = 2 * np.pi * np.sqrt(2 * kg / 1000 / (np.pi * Ldrum_m)) * Ldrum_m  # Crude density of 0.5

    Froude = ((params.RPM / 60 * 2 * np.pi) ** 2) * Ddrum_m / (2 * 9.8)

    # Process Variables
    Tbnow = params.Tbeans
    Toven_initial = Toven
    Toveneqold = 0
    PastTFC = False
    tFC = 0
    tDry = 0
    AmDry = False
    MJTot = 0
    Radiative = 0
    Tprev = 999
    tTurn = 0

    # Parsing Power Settings
    T = []
    tv = []
    P = []

    def sort_out(TtP):
        TempP = TtP.strip().replace(" ", "").replace(";", ",").replace(" ,", ",").replace(", ", ",")
        tmp = TempP.split(",")
        if len(tmp) > 2:
            ttmp = tmp[1].split(":")
            try:
                thet = float(ttmp[0])
                if len(ttmp) > 1:
                    thet += float(ttmp[1]) / 60
                theT = float(tmp[0])
                if theT > 0 or thet > 0:
                    T.append(float(tmp[0]))
                    tv.append(thet)
                    P.append(float(tmp[2]))
            except ValueError:
                pass  # Handle non-numeric entries gracefully

    for tp in params.TP:
        sort_out(tp)

    # Sorting the temperature and power settings
    sorted_indices = np.argsort(T)
    T = [T[i] for i in sorted_indices]
    tv = [tv[i] for i in sorted_indices]
    P = [P[i] for i in sorted_indices]

    # Initialize PPts
    # Interpolate target profile for visualization
    if target_profile is None:
        target_profile = [
            (0, 20),      # Initial temperature
            (300, 149),   # Drying Phase: 5 minutes to 149°C
            (600, 204),   # Maillard Reaction: next 5 minutes to 204°C
            (900, 210),   # First Crack: next 5 minutes to 210°C
            (1200, 227)   # Development Phase: next 5 minutes to 227°C
        ]

    target_x, target_y = zip(*target_profile)
    total_seconds = params.tmax * 60
    time_steps = np.linspace(0, total_seconds, nsteps + 1)
    target_interp = np.interp(time_steps, target_x, target_y)
    TargetPts = [{'x': t / 60, 'y': temp} for t, temp in zip(time_steps, target_interp)]  # Convert to minutes
    PPts = [{'x': 0, 'y': P[0]}]
    Pold = P[0]
    Pnow = 1

    # Simulation Loop with PID Control
    for step in range(nsteps + 1):
        tnow += tstep

        # Get current setpoint from the interpolated target profile
        current_setpoint = target_interp[step]

        # PID Controller to adjust power based on Tbnow
        control_output = pid.update(Tbnow, current_setpoint, tstep)
        # Determine power based on PID output
        # Here, we map control_output to a suitable power range.
        # This might need to be adjusted based on system characteristics.
        P_current = np.clip(control_output, MIN_POWER, MAX_POWER)

        PPts.append({'x': tnow, 'y': P_current})

        # Update Toveneq based on power
        # Assuming higher power increases Toveneq; adjust the relationship as needed
        Toveneq = params.Tair * (1 - (1 - P_current / params.P0) * 0.2)

        # Clamp Toveneq to prevent unrealistic values
        Toveneq = np.clip(Toveneq, MIN_TEMPERATURE, MAX_TEMPERATURE)

        if Toveneqold == 0:
            Toveneqold = Toveneq

        # Update Toven
        Toven_change = (Tbnow - (Toven - 40 + (params.Tair - Toveneq))) / (Resp * 5)
        Toven += Toven_change

        # Clamp Toven
        Toven = np.clip(Toven, MIN_TEMPERATURE, MAX_TEMPERATURE)

        ITPts.append({'x': tnow, 'y': Toveneq})
        OPts.append({'x': tnow, 'y': Toven})

        # Update MJnow
        MJeq = params.MJ * P_current / 100
        MJnow += (MJeq - MJnow) / Resp
        MJTot += MJnow

        # Calculate Wloss
        Wloss = max(0, (Tbnow - 100) * Wfact * tstep)

        # Check for First Crack (TFC)
        if Tbnow >= params.TFC:
            if tFC == 0:
                tFC = tnow
            PastTFC = True

        # Check for Drying (TDry)
        if Tbnow >= params.TDry:
            if tDry == 0:
                tDry = tnow
            AmDry = True

        # Update Water Loss and WMJ
        if PastTFC:
            Wloss = (Wnow - 0.01 * kgCoffee) / 10
            Wnow = max(Wnow - Wloss, 0)
            WMJ = WEV * Wloss
        else:
            if Wnow > 0 and Wloss > 0:
                Wloss = min(Wloss, Wnow - 0.01 * kgCoffee)
                Wnow -= Wloss
                WMJ = WEV * Wloss
            else:
                WMJ = 0

        # Update WPts
        WPts.append({'x': tnow, 'y': (Wnow * 100 / kgCoffee) if kgCoffee > 0 else 0})

        # Post First Crack adjustments
        if params.PostFC > 0 and PastTFC:
            PostFCloss = kgCoffee * params.PostFC / PostFCfact
            kgCoffee = max(kgCoffee - PostFCloss, 0)
            PostFCJ = ((Tbnow + 1 - params.TFC) ** 2) * PostFCloss * PostFCJfact
        else:
            PostFCJ = 0

        # Current weight
        kgnow = kgCoffee + Wnow
        KPts.append({'x': tnow, 'y': (100 * kgnow / kg) if kg > 0 else 0})

        # DeltaT Calculation
        try:
            DeltaT = ((Toveneqold) - Tbnow) * (MJnow - WMJ + PostFCJ) / kgnow * (0.019 + (Speed - 3) * 0.0005) * tstep
            # Prevent DeltaT from causing unrealistic temperatures
            DeltaT = np.clip(DeltaT, -MAX_TEMPERATURE, MAX_TEMPERATURE)
        except ZeroDivisionError:
            DeltaT = 0

        Toveneqold += (Toveneq - Toveneqold) / 100
        Tbnow += DeltaT

        # Clamp Tbnow
        Tbnow = np.clip(Tbnow, MIN_TEMPERATURE, MAX_TEMPERATURE)

        # DeltaTM Calculation
        DeltaTM = (Tbnow - TbMeasure) / Resp
        TbMeasure += DeltaTM

        # Prevent TbMeasure from becoming NaN or inf
        if not np.isfinite(TbMeasure):
            TbMeasure = Tbnow  # Reset to current bean temperature

        BPts.append({'x': tnow, 'y': TbMeasure})
        TBPts.append({'x': tnow, 'y': Tbnow})

        if TbMeasure > Tprev and tTurn == 0:
            tTurn = tnow
        Tprev = TbMeasure

        # Rate of Rise (ROR)
        ROR_value = (DeltaTM / tstep) * RoRCorrection
        # Clamp ROR to prevent unrealistic values
        ROR_value = np.clip(ROR_value, -50, 50)  # Example limits
        ROR.append({'x': tnow, 'y': ROR_value})

        # Radiative Heat Loss
        try:
            radiative_loss = Stefan * ((Toveneq + 273) ** 4 - (Tbnow + 273) ** 4)
            Radiative += radiative_loss
        except OverflowError:
            radiative_loss = 0
            Radiative += radiative_loss

        # Prevent Radiative from becoming too large
        Radiative = np.clip(Radiative, -1e12, 1e12)

    # Final Calculations
    Radiative *= BeanArea / (1 / params.Beta + (BeanArea / DrumArea) * (1 / params.Deta - 1)) * tstep * 60  # Convert to seconds
    MJTot *= params.tmax / 60 / nsteps

    TFinal = TbMeasure
    tTurnm = int(np.floor(tTurn)) if tTurn > 0 else 0
    tTurnms = f"t_Turn: {tTurnm}m:{int((tTurn - tTurnm) * 60)}s"
    tFCm = int(np.floor(tFC)) if tFC > 0 else 0
    tDrop = int(np.floor(params.tmax))
    tDryms = int(np.floor(tDry)) if tDry > 0 else 0

    tFCms = f" t_Yellow: {int(tDry)}m:{int((tDry - tDryms) * 60)}s" if tDry > 0 else " t_Yellow: -"
    if tFC > 0:
        tFCms += f", t_FC: {tFCm}m:{int((tFC - tFCm) * 60)}s"
    tFCms += f" , t_Drop: {tDrop}m:{int((params.tmax - tDrop) * 60)}s"
    TDrop = f"T_Drop: {int(TbMeasure)}°C" if np.isfinite(TbMeasure) else "T_Drop: NaN°C"

    Ratios = "-"
    if tFC > 0 and tDry > 0:
        Brown = tFC - tDry
        Dev = tDrop - tFC
        Ratios = f"Yellow: {tDry * 100 / tDrop:.1f}%, Brown: {Brown * 100 / tDrop:.1f}%, Dev: {Dev * 100 / tDrop:.1f}%"

    # Bean Calculations
    BMass = (4 / 3) * np.pi * (params.D / 2) ** 3 * params.rho  # Mass of single bean
    NBeans = int(kg / BMass) if BMass > 0 else 0
    SA = NBeans * 4 * np.pi * (params.D / 2) ** 2
    kJb = kg * params.Cp * (TFinal - params.Tbeans)
    Jb = f"{int(kJb)} kJ" if kJb <= 1000 else f"{kJb / 1000:.3f} MJ"
    Jr = f"{MJTot:.3f} MJ" if MJTot >= 1 else f"{MJTot * 1000:.3f} kJ"
    kJRad = f"{int(Radiative / 1000)} kJ" if np.isfinite(Radiative) else "Radiative: NaN kJ"

    # Information String
    Power = f"Power: {params.MJ * 948 / 1000:.1f} kBTU, {params.MJ * 1e3 / 3600:.1f} kW"
    StepText = "2-Step match not implemented in this version."

    Info = f"{tTurnms}, {tFCms}, {TDrop}, {Ratios}, {Power}\n{StepText}"

    # Plot Configuration (simplified for Python)
    prmap = {
        'plotData': [BPts, TBPts, ROR, TargetPts],
        'lineLabels': [ "Bean Temp", "True Bean Temp", "Rate Of Rise", "Target Temp"],
        'colors': ["purple", "red", "skyblue", "black"],
        'xLabel': 'Time (min)',
        'yLabel': 'Temperature (°C)',
        'y2Label': "ROR (°C/min)",
    }

    # prmap1 = {
    #     'plotData': [PPts, KPts, WPts],
    #     'lineLabels': ["Power (%)", "Weight (%)", "Water (%)"],
    #     'colors': ["orange", "brown", "skyblue"],
    #     'xLabel': 'Time (min)',
    #     'yLabel': 'Power, Weight, Water',
    # }

    return SimulationResult(
        plots=[prmap],
        Info=Info,
        NB=NBeans,
        SA=SA,
        kJb=Jb,
        kJr=Jr,
        Froude=Froude,
        kJRad=kJRad
    )

# -------------------------------
# Plotting Function
# -------------------------------

def plot_simulation(result: SimulationResult):
    fig, axs = plt.subplots(1, 1, figsize=(14, 12))

    # First Plot: Temperature and ROR
    ax1 = axs
    for idx, data in enumerate(result.plots[0]['plotData']):
        label = result.plots[0]['lineLabels'][idx]
        color = result.plots[0]['colors'][idx]
        if isinstance(data, dict) and 'y' in data:
            x = [data['x']]
            y = [data['y']]
        else:
            x = [point['x'] for point in data]
            y = [point['y'] for point in data]
        if label == "TargetPts":
            ax1.plot(x, y, label=label, color=color, linestyle=':')
        else:
            ax1.plot(x, y, label=label, color=color)
    ax1.set_xlabel(result.plots[0]['xLabel'])
    ax1.set_ylabel(result.plots[0]['yLabel'])
    ax1.legend()
    ax1.grid(True)

    # # Second Plot: Power, Weight, Water
    # ax2 = axs[1]
    # for idx, data in enumerate(result.plots[1]['plotData']):
    #     label = result.plots[1]['lineLabels'][idx]
    #     color = result.plots[1]['colors'][idx]
    #     if isinstance(data, dict) and 'y' in data:
    #         x = [data['x']]
    #         y = [data['y']]
    #     else:
    #         x = [point['x'] for point in data]
    #         y = [point['y'] for point in data]
    #     ax2.plot(x, y, label=label, color=color)
    # ax2.set_xlabel(result.plots[1]['xLabel'])
    # ax2.set_ylabel(result.plots[1]['yLabel'])
    # ax2.legend()
    # ax2.grid(True)

    plt.tight_layout()
    plt.show()

# -------------------------------
# Example Usage
# -------------------------------

def main():
    # Define simulation parameters
    params = SimulationParameters(
        kg=300,                # Bean weight in grams
        water=0.10,            # Bean moisture percentage (converted to fraction)
        MJ=4.0,                # MJ/hour at 100%
        Tair=240,              # Inlet-start temperature in °C
        Tbeans=20,             # TBean-start temperature in °C
        TFC=193,               # First Crack temperature in °C
        Toffset=215,           # Charge temperature in °C
        TDry=160,              # Yellow temperature in °C
        PostFC=2.0,            # Post FC Factor
        tmax=12.0,             # Drop time in minutes
        Speed=3.0,             # Relative Drum/Air factor
        Respv=3.0,             # Relative Response
        P0=90,                 # Initial Power setting (%)
        TP=["140,4:50,80", "160,6:00,70", "170,6:45,60", "180,7:45,40", "190,9:30,20"],  # Power settings
        D=6.0,                 # Bean diameter in mm
        rho=1000,              # Bean density in kg/m^3
        Cp=1.2,                # Specific heat capacity (kJ/kgK)
        RPM=50,                # Drum rpm
        Ddrum=150,             # Drum diameter in mm
        Ldrum=150,             # Drum length in mm
        Deta=0.25,             # Drum ε
        Beta=0.95              # Bean ε
    )
### EDIT YOUR PID VALUES HERE ###
    '''
    You need to tune the PID values to get the desired temperature profile. 
    So that the true bean temp plot is as close as possible to the target temp plot.
    '''
    pid = PIDController(
        Kp=0.0,    # Increased Proportional gain for better responsiveness
        Ki=0.0,   # Decreased Integral gain to reduce overshoot
        Kd=0.0     # Increased Derivative gain to dampen oscillations
    )
### EDIT YOUR PID VALUES HERE ###
    # Run simulation
    result = calc_it(params, pid)

    # Plotting
    plot_simulation(result)

# -------------------------------
# Run the Simulation
# -------------------------------

if __name__ == "__main__":
    main()
