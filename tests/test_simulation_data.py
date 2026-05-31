from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from data.scenarios.factory_machine import Factory


N_STEPS = 1000

CSV_DIR = Path("experiments/outputs/csv")
PLOTS_DIR = Path("experiments/outputs/plots")

CSV_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


machine = Factory.create()

external_df = pd.DataFrame(
    machine.run(N_STEPS)
)

external_df.to_csv(
    CSV_DIR / "simulation.csv",
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


def normalize(df, columns):
    return (
        df[columns] - df[columns].min()
    ) / (
        df[columns].max() - df[columns].min()
    )


def plot_signals(df, columns, title, output_file):
    plt.figure(figsize=(16, 8))

    for column in columns:
        plt.plot(df[column], label=column)

    plt.legend()
    plt.title(title)

    plt.savefig(output_file)
    plt.close()


external_normalized = normalize(
    external_df,
    external_columns
)

plot_signals(
    external_normalized,
    external_columns,
    "External normalized signals",
    PLOTS_DIR / "external_normalized_signals.png"
)


internal_df = pd.DataFrame(
    machine.internal_history
)

internal_normalized = normalize(
    internal_df,
    internal_columns
)

plot_signals(
    internal_normalized,
    internal_columns,
    "Internal normalized signals",
    PLOTS_DIR / "internal_normalized_signals.png"
)