def main():
    from data.scenarios.factory_machine import Factory
    from detection.detector import AnomalyDetector
    from detection.detection_history import DetectionHistory
    from data.measurement_history import MeasurementHistory


    machine = Factory.create()

    detector = AnomalyDetector()

    history = DetectionHistory()
    measurements = MeasurementHistory.create()


    for _ in range(10000):

        sensors = machine.step()
        measurements.append(sensors)

        signal = detector.detect(
            sensor_values=sensors
        )

        history.save(signal)


if __name__ == "__main__":
    main()
