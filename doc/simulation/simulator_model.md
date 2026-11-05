# Simplified water-pump model

This simulator represents a variable-speed centrifugal water pump in a closed
loop, driven by an air-cooled electric motor. Parameters are illustrative: this
is a physically motivated demonstrator, not a calibrated industrial machine.

## Measurements and configuration

| JSONL field | Meaning | Unit |
| --- | --- | --- |
| `temperature` | Lumped motor/casing temperature | °C |
| `rotational_speed` | Measured motor/pump speed | rpm |
| `power_consumption` | Electrical input power | kW |
| `pressure` | Discharge-minus-suction differential pressure | bar |
| `flow_rate` | Circulating water flow | m³/h |

`config/pump.py` contains the physical parameters, scenario settings and sensor
noise amplitudes. `config/settings.py` contains the detection thresholds and
agent settings. No physical parameters or secrets need to be added to `.env`.

The nominal operating point is 2,900 rpm, 12 m³/h and 20 m of water head
(1.962 bar). Hydraulic power is 654 W, shaft power is 972 W and electrical
input is approximately 1.105 kW. At constant nominal speed and healthy
ventilation, the thermal equilibrium is approximately 58.1 °C at 25 °C ambient.
These are references for this model, not universal normal ranges.

The former vibration and normalized machine-activity fields are removed. Legacy
simulation outputs have been deleted. No migration is provided: files missing
the current sensor fields are rejected explicitly. New runs create their own
five-sensor history.

## Equations

`data/simulation/dynamics.py` implements the following model. Here `r = n/n_nom`
is relative speed, `Q` is in m³/h and head `H` is in metres of water.

### Flow and pressure

The pump and circuit curves are:

```text
H_pump = H_shutoff * r² - A * Q²
H_circuit = R * Q²
A = (H_shutoff - H_nom) / Q_nom²
R = (H_nom / Q_nom²) * resistance_factor
```

There is no static lift in the closed loop. Their intersection gives:

```text
Q = sqrt(H_shutoff * r² / (A + R))
H = R * Q²
pressure_Pa = density * gravity * H
pressure_bar = pressure_Pa / 100000
```

Increasing circuit resistance reduces flow and increases differential pressure
at the same speed. In the healthy circuit, flow scales with speed and pressure
with speed squared. Low flow alone is therefore not evidence of a fault when
speed is also low.

### Power

```text
hydraulic_power_W = pressure_Pa * Q / 3600
shaft_power_W = hydraulic_power_W / 0.75 + 100 * r³
electrical_power_W = shaft_power_W / 0.88
motor_loss_W = electrical_power_W - shaft_power_W
```

The coefficients are configurable. The additional shaft-power term represents
parasitic pump losses and avoids zero shaft power at near-zero flow with the
motor turning. The hydraulic conversion coefficient is not the overall pump
efficiency, because these additional losses also consume power.

A restriction does not necessarily increase electrical demand. In this chosen
model it decreases it at fixed speed; high pressure is not equivalent to high
hydraulic power when flow falls.

### Temperature and speed response

```text
C * dT/dt = motor_loss_W - G * (T - ambient_temperature)
G = healthy_thermal_conductance * ventilation_factor
dn/dt = (speed_setpoint - n) / speed_time_constant
```

Temperature changes gradually. Only motor losses heat this thermal mass; pump
losses are not incorrectly counted as motor heating. Ventilation loss reduces
heat removal without directly altering the hydraulic circuit.

Speed uses the exact first-order exponential update for each integration step.
The thermal update uses an exponential solution with motor losses evaluated at
the midpoint speed. Integration substeps are at most 0.25 simulated seconds,
independently of the output sampling period. This is a numerical approximation
when controls vary over time.

## Scenarios and time

`data/scenarios/scenario.py` supplies controls using elapsed simulated seconds.
The normal speed command cycles between 80% and 100% of nominal speed over
1,200 seconds. The machine starts at rest and ambient temperature.

Available modes:

- `normal`: healthy circuit and ventilation.
- `restriction`: circuit resistance rises from 1 to 4 times its initial value.
- `ventilation_loss` (default): ventilation falls from 1 to 0.25.

A fault starts after 900 seconds and develops over 600 seconds. These values
are demonstration choices, configurable in `config/pump.py`.

`Factory.create(scenario=Scenario("normal"), seed=42)` selects a scenario and
reproducible measurement noise. `noise=False` disables noise for physics checks.
The first measurement describes the initial state at time zero; subsequent
measurements correspond to their UTC timestamps. Simulated seconds do not
require waiting for wall-clock seconds. Changing the sample period does not
rescale fault timing or the thermal equations.

## Detection and LLM context

`detection/rules.py` compares flow and pressure against references derived from
measured speed. Monitoring these two quantities starts above 600 rpm. Low flow
(below 75% of reference) and high pressure (above 120%) together reach the
configured alert score. Motor temperature above 80 °C also triggers an alert.
All thresholds are demonstration criteria, not equipment safety limits.

`investigation/prompts/pump_description.py` gives the agent measurement units,
nominal references, important relationships and interpretation limits. It does
not reveal the active scenario, fault onset or internal fault factors. History
and statistics tools use the new sensor list through the shared configuration.
No additional investigation tools are introduced.

## Scope and limitations

- Hydraulics are quasi-steady: no water hammer, cavitation or fluid inertia.
- Speed response is empirical; shaft inertia, acceleration power and motor
  electrical transients are not modeled.
- Efficiency coefficients are constant, rather than a manufacturer's complete
  performance map. Near shutoff is not a validated operating regime.
- Motor/casing temperature is one lumped thermal mass. Winding temperature,
  water heating, pump-body heating and changing ambient conditions are omitted.
- Sensor noise is bounded uniform noise, without calibration drift.
- There are no bearing, vibration or generic wear equations. A diagnosis of
  a specific component fault would go beyond the observations supported here.

The scenario creates plausible signatures for investigation; tests establish
consistency of this implementation, not validation against a real pump.

## Offline checks and visualization

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover
PYTHONPATH=. .venv/bin/python scripts/experiments/simulation_data.py
```

The visualization script runs 6,000 samples without a LLM call. It writes a new
JSONL and two plot files under `experiments/outputs`, using physical units and
elapsed seconds. Internal-state plots are for simulator inspection only, not
inputs to the investigation agent. Matplotlib and pandas must already be installed.

## Physical references

The references support the modeling principles, not the chosen numerical
parameters:

- [KSB: operating point](https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/operating-point-1117036): intersection of pump and system curves.
- [KSB: pump affinity laws](https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/pump-affinity-laws-1117584): speed similarity and hydraulic power.
- [MathWorks: motor drive](https://www.mathworks.com/help/sdl/ref/motordrive.html): electrical/mechanical power balance and heat generation from motor losses.
