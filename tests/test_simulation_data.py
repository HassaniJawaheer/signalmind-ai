from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from data.scenarios.factory_machine import Factory


N_STEPS = 1000


machine = Factory.create()

data = machine.run(
    n_steps=N_STEPS
)


external_df = pd.DataFrame(
    data
)


Path(
    "experiments/outputs/csv"
).mkdir(
    parents=True,
    exist_ok=True
)

Path(
    "experiments/outputs/plots"
).mkdir(
    parents=True,
    exist_ok=True
)


external_df.to_csv(
    "experiments/outputs/csv/simulation.csv",
    index=False
)


external_columns = [
    "temperature",
    "vibration",
    "power_consumption",
    "machine_activity",
    "pressure",
    "flow_rate"
]


internal_columns = [
    "load",
    "health",
    "wear",
    "core_temperature",
    "cooling_efficiency",
    "fan_speed",
    "flow_rate",
    "pressure"
]


external_normalized = (
    external_df[external_columns]
    - external_df[external_columns].min()
) / (
    external_df[external_columns].max()
    - external_df[external_columns].min()
)


plt.figure(
    figsize=(16,8)
)

for column in external_columns:

    plt.plot(
        external_normalized[column],
        label=column
    )

plt.legend()

plt.title(
    "External normalized signals"
)

plt.savefig(
    "experiments/outputs/plots/external_normalized_signals.png"
)

plt.close()


internal_history = pd.DataFrame(
    machine.internal_history
)


internal_normalized = (
    internal_history[internal_columns]
    - internal_history[internal_columns].min()
) / (
    internal_history[internal_columns].max()
    - internal_history[internal_columns].min()
)


plt.figure(
    figsize=(16,8)
)

for column in internal_columns:

    plt.plot(
        internal_normalized[column],
        label=column
    )

plt.legend()

plt.title(
    "Internal normalized signals"
)

plt.savefig(
    "experiments/outputs/plots/internal_normalized_signals.png"
)

plt.close()