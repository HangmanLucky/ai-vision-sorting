# -*- coding: utf-8 -*-
"""
ai_sorting_service.py
------------------------
The Python-side "edge AI" service: a Modbus TCP CLIENT that polls the
PLC's Item_Trigger_Counter register, runs inference against the trained
TinyMLP for each new item, and writes the verdict back into the PLC's
register map - the actual Python-to-PLC handshake this project is named
for.

Run against plc_simulator.py (see docs/Testing_Procedures.md for the
full end-to-end test log) or against a real PLC's Modbus TCP server on
the register map documented in docs/IO_List.md.

Author: Sipho Lucky Sibanda
"""

import time
import sys
import numpy as np
from pymodbus.client import ModbusTcpClient

from vision_model import (
    generate_synthetic_patch, extract_features, classify_defect_type, TinyMLP
)

HOST = "127.0.0.1"
PORT = 5020
POLL_INTERVAL_S = 0.15
DEFECT_CLASS_NAMES = ["None", "Scratch", "Dent", "Discoloration"]

# Register addresses - must match docs/IO_List.md and AI_SortingMatrix.st
HR_ITEM_TRIGGER = 0
HR_ITEM_ID_ACK = 1
HR_DEFECT_DETECTED = 2
HR_CONFIDENCE_X10 = 3
HR_DEFECT_CLASS_ID = 4
HR_AI_HEARTBEAT = 5
HR_AI_RESULT_READY = 6


def load_model_and_norm():
    try:
        model = TinyMLP.load("model_weights.npz")
        norm = np.load("feature_norm.npz")
        mu, sigma = norm["mu"], norm["sigma"]
        print("[AI  ] Loaded trained model_weights.npz")
        return model, mu, sigma
    except FileNotFoundError:
        print("[AI  ] No trained model found - run train_model.py first. "
              "Using an untrained model as a fallback (verdicts will be poor).")
        return TinyMLP(), np.zeros(5), np.ones(5)


def run_inference(model, mu, sigma, rng, defect_type_truth):
    """Simulate 'capturing' a frame for this item and classifying it.
    In this simulation we know the ground-truth defect_type_truth only
    to generate a plausible synthetic patch - the model itself never
    sees that label, exactly like a real trained classifier facing an
    unlabelled production item."""
    severity = rng.uniform(0.1, 1.0) if defect_type_truth != 0 else 0.0
    patch = generate_synthetic_patch(defect_type_truth, rng, severity=severity)
    features = extract_features(patch)
    features_norm = (features - mu) / sigma
    probs = model.predict_proba(features_norm.reshape(1, -1))[0]
    defect_prob = float(probs[1])
    defect_detected = defect_prob >= 0.5
    confidence = defect_prob if defect_detected else (1.0 - defect_prob)
    defect_class = classify_defect_type(patch, features) if defect_detected else "None"
    return defect_detected, confidence, defect_class


def main(max_items=None):
    model, mu, sigma = load_model_and_norm()
    rng = np.random.default_rng()

    client = ModbusTcpClient(HOST, port=PORT)
    if not client.connect():
        print(f"[AI  ] ERROR: could not connect to PLC at {HOST}:{PORT}")
        sys.exit(1)
    print(f"[AI  ] Connected to PLC Modbus TCP server at {HOST}:{PORT}")

    last_seen_counter = 0
    heartbeat = 0
    items_processed = 0

    try:
        while True:
            heartbeat = (heartbeat + 1) % 65536
            client.write_register(HR_AI_HEARTBEAT, heartbeat, device_id=1)

            rr = client.read_holding_registers(HR_ITEM_TRIGGER, count=1, device_id=1)
            if rr.isError():
                print("[AI  ] Modbus read error - retrying")
                time.sleep(POLL_INTERVAL_S)
                continue

            current_counter = rr.registers[0]
            if current_counter != last_seen_counter and current_counter != 0:
                item_id = current_counter
                last_seen_counter = current_counter

                # Ground truth is unknown to the model - only used here to
                # generate a plausible synthetic patch, mirroring how a
                # real production line's true defect state is unknown
                # until inspected.
                defect_type_truth = rng.choice([0, 0, 1, 2, 3])  # ~40% ok, 60% defective mix
                defect_detected, confidence, defect_class = run_inference(
                    model, mu, sigma, rng, defect_type_truth
                )
                class_id = DEFECT_CLASS_NAMES.index(defect_class)

                client.write_registers(
                    HR_ITEM_ID_ACK,
                    [
                        item_id,
                        1 if defect_detected else 0,
                        int(round(confidence * 1000)),
                        class_id,
                    ],
                    device_id=1,
                )
                client.write_register(HR_AI_RESULT_READY, 1, device_id=1)

                verdict = "FAIL" if defect_detected else "PASS"
                print(f"[AI  ] Item #{item_id:03d} inferred: {verdict}  "
                      f"confidence={confidence*100:.1f}%  class={defect_class}")

                items_processed += 1
                if max_items and items_processed >= max_items:
                    print(f"[AI  ] Reached max_items={max_items}, stopping.")
                    break

            time.sleep(POLL_INTERVAL_S)

    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        print("[AI  ] Disconnected.")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(max_items=n)
