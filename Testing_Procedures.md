# Functional Test Procedure — AI Sorting Matrix

**Project:** AI-Driven Edge Vision Integration
**Document type:** Factory Acceptance Test (FAT) — simulated / desktop validation,
**with a genuinely executed end-to-end integration test** (see Test 11 and Test 12)
**Author:** Sipho Lucky Sibanda

## PLC logic test cases (simulated I/O forcing)

| # | Test Case | Precondition | Action | Expected Result | Pass/Fail |
|---|------------|----------------|---------|--------------------|-------------|
| 1 | New item enters tracking queue | Queue empty | Pulse `DI_ItemPresent_InspectionPoint` | `HR0_ItemTriggerCounter` increments; a queue slot activates with a running transit timer | |
| 2 | High-confidence PASS | Item in queue, AI result: no defect, 95% confidence | Wait for transit timer to expire | `DO_DiverterArm_Position = 0`; `ItemsSorted_Pass` increments | |
| 3 | High-confidence REJECT | Item in queue, AI result: defect, 95% confidence | Wait for transit timer to expire | `DO_DiverterArm_Position = 1`; `ItemsSorted_Reject` increments | |
| 4 | Uncertain-band confidence routes to manual | Item in queue, AI result: defect, 75% confidence | Wait for transit timer to expire | `DO_DiverterArm_Position = 2` (manual), despite a "defect" verdict | |
| 5 | Low confidence routes to manual | Item in queue, AI result: no defect, 40% confidence | Wait for transit timer to expire | `DO_DiverterArm_Position = 2` (manual), despite a "no defect" verdict | |
| 6 | No result received in time | Item in queue, no AI response before transit timer expires | Wait for transit timer to expire | Routes to manual review; does not wait indefinitely | |
| 7 | AI heartbeat watchdog trips | `HR5_AIHeartbeat` frozen | Wait >2s | `Alarm_AI_Offline = TRUE`; all subsequent items route to manual regardless of any stale result data | |
| 8 | Watchdog recovers | Continuing from Test 7 | `HR5_AIHeartbeat` resumes incrementing | `Alarm_AI_Offline` clears; normal routing resumes | |
| 9 | Result matched by Item ID, not arrival order | Two items in queue simultaneously | AI responds for the second item first | Result is correctly matched to its own queue slot by `Item_ID_Ack`, not by position | |
| 10 | Queue full | 6 items detected within one transit-time window (queue depth 5) | Observe | `Alarm_QueueFull = TRUE`; a real installation would stop infeed on this alarm | |

## Genuinely executed end-to-end integration test

Unlike the PLC-only projects earlier in this portfolio, this project's Python side
can actually run. `python/plc_simulator.py` (a minimal hand-written Modbus TCP
server standing in for the PLC's register map) and `python/ai_sorting_service.py`
(the real Modbus TCP client, calling the actually-trained model) were run as two
independent processes talking real Modbus TCP over localhost.

### Test 11 — Normal operation, genuinely executed

```
[AI  ] Loaded trained model_weights.npz
[AI  ] Connected to PLC Modbus TCP server at 127.0.0.1:5020
[AI  ] Item #001 inferred: PASS  confidence=66.9%  class=None
[AI  ] Item #002 inferred: PASS  confidence=92.4%  class=None
[AI  ] Item #004 inferred: FAIL  confidence=79.0%  class=Dent
[AI  ] Item #005 inferred: FAIL  confidence=100.0%  class=Discoloration

[PLC ] Item #001 detected at inspection point (HR0 Item_Trigger_Counter -> 1)
[PLC ] Result for item #001: PASS  (confidence 66.9%, class=None) - consuming and clearing HR6
[PLC ] Item #004 detected at inspection point (HR0 Item_Trigger_Counter -> 4)
[PLC ] Result for item #004: FAIL  (confidence 79.0%, class=Dent) - consuming and clearing HR6
```

Note item #001 and #004 both landed in the 60-90% "uncertain band" (66.9% and 79.0%
respectively) — in the real PLC logic (not modelled in this simplified consumer
thread, which just logs whatever it receives) these specific results are exactly the
case Test 4 and Test 5 above are designed to catch and route to manual review rather
than act on directly.

### Test 12 — Watchdog fail-safe, genuinely executed

The AI service was killed (`SIGKILL`) mid-run to simulate a real crash, while the
PLC simulator kept running:

```
[AI  ] Item #001 inferred: FAIL  confidence=53.4%  class=Dent
[AI  ] Item #002 inferred: FAIL  confidence=87.0%  class=Dent
                                    <-- process killed here -->

[PLC ] Item #003 detected at inspection point (HR0 Item_Trigger_Counter -> 3)
[PLC ] *** AI_Heartbeat stale for >2.0s - declaring AI OFFLINE, routing all items to MANUAL REVIEW ***
[PLC ] Item #004 detected at inspection point (HR0 Item_Trigger_Counter -> 4)
[PLC ] Item #005 detected at inspection point (HR0 Item_Trigger_Counter -> 5)
```

Items #003, #004, and #005 arrived after the AI service died and correctly received
no result — exactly the scenario Test 7 validates, now demonstrated against a real
dead process rather than only a forced input value.

## How to reproduce this test yourself

```bash
cd python
python3 train_model.py                    # trains and saves model_weights.npz
python3 plc_simulator.py 30 &              # starts the Modbus TCP server for 30s
python3 ai_sorting_service.py 10           # runs the AI client for 10 items
```

## Sign-off

| Role | Name | Date |
|------|------|------|
| Test performed by | Sipho Lucky Sibanda | |
| Reviewed by | | |
