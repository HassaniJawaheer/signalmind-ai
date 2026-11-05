def main():
    from pathlib import Path

    import matplotlib.pyplot as plt
    import pandas as pd

    from data.scenarios.factory_machine import Factory
    from data.measurement_history import MeasurementHistory

    N_STEPS = 6000
    history = MeasurementHistory.create()
    plots_dir = Path("experiments/outputs/plots")
    plots_dir.mkdir(parents=True, exist_ok=True)
    machine = Factory.create()

    measurements = []
    for _ in range(N_STEPS):
        snapshot = machine.step()
        history.append(snapshot)
        measurements.append(snapshot)
    external_df = pd.DataFrame(measurements)
    print(f"Measurement history: {history.path}")

    external_columns = [
        ("temperature", "Motor casing (°C)"),
        ("rotational_speed", "Speed (rpm)"),
        ("power_consumption", "Electrical power (kW)"),
        ("pressure", "Differential pressure (bar)"),
        ("flow_rate", "Water flow (m³/h)"),
    ]
    internal_columns = [
        ("hydraulic_power_w", "Hydraulic power (W)"),
        ("shaft_power_w", "Shaft power (W)"),
        ("motor_loss_w", "Motor losses (W)"),
        ("resistance_factor", "Circuit resistance factor"),
        ("ventilation_factor", "Ventilation factor"),
    ]

    def plot_signals(df, columns, title, output_file):
        figure, axes = plt.subplots(len(columns), 1, figsize=(12, 12), sharex=True)
        for axis, (column, label) in zip(axes, columns):
            axis.plot(df['elapsed_seconds'], df[column])
            axis.set_ylabel(label)
            axis.grid(alpha=0.3)
        axes[-1].set_xlabel("Simulated time (s)")
        figure.suptitle(title)
        figure.tight_layout()
        figure.savefig(output_file)
        plt.close(figure)

    timestamps = pd.to_datetime(external_df['timestamp'])
    external_df['elapsed_seconds'] = (timestamps - timestamps.iloc[0]).dt.total_seconds()
    plot_signals(external_df, external_columns, "Pump measurements",
                 plots_dir / f"{history.path.stem}_measurements.png")

    internal_df = pd.DataFrame(machine.internal_history)
    plot_signals(internal_df, internal_columns, "Simulator internal state (not sent to the agent)",
                 plots_dir / f"{history.path.stem}_internal.png")


if __name__ == "__main__":
    main()
