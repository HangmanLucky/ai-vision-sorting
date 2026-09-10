# I/O List — AI-Driven Edge Vision Integration

**Project:** PLC-Controlled Neural Network Sorting Matrix
**Author:** Sipho Lucky Sibanda
**Target platform:** Siemens S7-1500 (TIA Portal / SCL) — portable to a CODESYS-based
industrial controller

This project has two I/O surfaces: conventional physical field I/O, and a Modbus TCP
holding-register map shared with the Python edge AI service.

## Physical I/O

| Tag Name                          | Description                                | Signal Type      |
|----------------------------------------|---------------------------------------------|--------------------|
| `DI_ItemPresent_InspectionPoint`         | Photoeye at the camera/inspection station       | Digital (24VDC)      |
| `DI_ItemPresent_DiverterPoint`             | Photoeye just before the sorting diverter          | Digital (24VDC)        |
| `DO_DiverterArm_Position`                    | Diverter arm position: 0=PASS, 1=REJECT, 2=MANUAL     | Digital/analogue (3-position) |
| `DI_System_Enable`                              | Master enable                                             | Digital (24VDC)                 |

## Modbus TCP Register Map (holding registers, 0-based)

| Address | Name                   | Written By    | Description                                      |
|-----------|--------------------------|-----------------|-----------------------------------------------------|
| HR0         | `Item_Trigger_Counter`     | PLC               | Increments on each new item detected at the inspection point |
| HR1           | `Item_ID_Ack`                | AI service          | Echoes which Item_Trigger_Counter value this result belongs to |
| HR2             | `Defect_Detected`              | AI service             | 0 = no defect, 1 = defect detected |
| HR3               | `Confidence_Pct_x10`             | AI service                | Model confidence, scaled 0-1000 (0.0-100.0%) |
| HR4                 | `Defect_Class_ID`                  | AI service                   | 0=None, 1=Scratch, 2=Dent, 3=Discoloration |
| HR5                   | `AI_Heartbeat`                        | AI service                      | Incremented every inference-loop cycle; watched by the PLC watchdog |
| HR6                     | `AI_Result_Ready`                       | AI service (set) / PLC (cleared)  | Handshake flag: AI sets 1 when HR1-4 are valid; PLC clears after consuming |

## Notes for reviewers

- In a real TIA Portal project, this register block would be a Data Block associated
  with an **MB_SERVER** instance (the S7-1500's native Modbus TCP server
  functionality) — the PLC-side Structured Text in `AI_SortingMatrix.st` reads and
  writes that DB's members directly; it never touches the Modbus wire protocol
  itself. The wire protocol only exists between the PLC's MB_SERVER instance and the
  Python client in `python/ai_sorting_service.py`.
- The **conservative confidence thresholds** applied in the PLC logic
  (`HighConfidence_Pct = 90.0`, `LowConfidence_Pct = 60.0`) are separate from, and
  stricter than, the AI model's own 50% decision boundary — see
  `docs/Testing_Procedures.md` and the project manual, Chapter 5, for why that
  second layer of scepticism exists on the PLC side specifically.
- `python/plc_simulator.py` implements a minimal hand-written Modbus TCP **server**
  standing in for the real PLC's register map during development — see its module
  docstring for why a custom implementation was used instead of a third-party
  server library for this specific role.
