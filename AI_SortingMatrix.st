(*
====================================================================================
  PROJECT   : AI-Driven Edge Vision Integration
              PLC-Controlled Neural Network Sorting Matrix
  MODULE    : FB_AI_SortingMatrix
  PLATFORM  : IEC 61131-3 Structured Text
              Written against Siemens SCL (TIA Portal, S7-1500) syntax,
              portable to CODESYS-based industrial controllers.
  AUTHOR    : Sipho Lucky Sibanda
  CONTEXT   : A PLC cannot run a neural network - but it doesn't need to.
              A separate edge PC runs the trained model (see python/ in
              this repository) and hands its verdict to the PLC over
              Modbus TCP. This function block is the PLC-side half of
              that handshake: it tracks each item physically travelling
              along the conveyor, decides whether the AI's verdict is
              trustworthy enough to act on, and drives the sorting
              diverter - while never assuming the AI service is healthy
              just because it was healthy a moment ago.

  MODBUS REGISTER MAP (holding registers - see docs/IO_List.md):
    HR0  Item_Trigger_Counter   Written BY this PLC, read by the AI service
    HR1  Item_ID_Ack             Written by the AI service
    HR2  Defect_Detected           Written by the AI service
    HR3  Confidence_Pct_x10          Written by the AI service (0-1000)
    HR4  Defect_Class_ID               Written by the AI service
    HR5  AI_Heartbeat                    Written by the AI service
    HR6  AI_Result_Ready                   Written by the AI service, cleared here

  In a real TIA Portal project this register block would live in a DB
  associated with an MB_SERVER instance; this function block's inputs
  and outputs below map directly onto that DB's members.

  WHY THE PLC DOESN'T JUST TRUST THE AI'S OWN CONFIDENCE THRESHOLD:
    The Python service already applies its own 50% decision boundary to
    call something a defect at all (see vision_model.py). This function
    block applies a SECOND, more conservative pair of thresholds on top
    of that: anything below HighConfidence_Pct is routed to a human
    reviewer regardless of the raw verdict, because a PLC blindly acting
    on a 51%-confidence classification is not meaningfully different
    from acting on a coin flip.
====================================================================================
*)

TYPE E_SortRoute :
(
    ROUTE_NONE,
    ROUTE_PASS,
    ROUTE_REJECT,
    ROUTE_MANUAL_REVIEW
);
END_TYPE

TYPE ST_TrackedItem :
STRUCT
    Active           : BOOL;
    ItemID            : INT;
    ResultReceived     : BOOL;
    Defect_Detected      : BOOL;
    Confidence_Pct         : REAL;
    Defect_Class_ID          : INT;
    TransitTimer               : TON;
END_STRUCT
END_TYPE

FUNCTION_BLOCK FB_AI_SortingMatrix
VAR_INPUT
    DI_ItemPresent_InspectionPoint : BOOL;   // Photoeye at the camera station
    DI_ItemPresent_DiverterPoint    : BOOL;   // Photoeye just before the diverter
    HR1_ItemIDAck                    : INT;    // From AI service (Modbus)
    HR2_DefectDetected                 : BOOL;   // From AI service
    HR3_ConfidencePctX10                 : INT;    // From AI service, 0-1000
    HR4_DefectClassID                      : INT;    // From AI service
    HR5_AIHeartbeat                          : INT;    // From AI service
    HR6_AIResultReady                          : BOOL;   // From AI service
    DI_System_Enable                             : BOOL;
END_VAR

VAR_OUTPUT
    HR0_ItemTriggerCounter  : INT := 0;      // To AI service (Modbus)
    HR6_Clear_Ack             : BOOL := FALSE;  // Pulses to acknowledge/clear HR6
    DO_DiverterArm_Position     : INT := 0;      // 0=PASS, 1=REJECT, 2=MANUAL_REVIEW
    Alarm_AI_Offline               : BOOL := FALSE;
    Alarm_TrackingMismatch           : BOOL := FALSE;
    Alarm_QueueFull                    : BOOL := FALSE;
    ItemsSorted_Pass                     : DINT := 0;
    ItemsSorted_Reject                     : DINT := 0;
    ItemsSorted_ManualReview                 : DINT := 0;
    SystemStatus                               : STRING[24] := 'STANDBY';
END_VAR

VAR
    HighConfidence_Pct     : REAL := 90.0;   // Trust the AI verdict outright above this
    LowConfidence_Pct      : REAL := 60.0;   // Below this, effectively a non-answer
    TransitDelay_PT         : TIME := T#8S;   // Inspection point -> diverter travel time
    HeartbeatTimeout_PT      : TIME := T#2S;

    Queue                      : ARRAY[0..4] OF ST_TrackedItem;
    QueueDepth                   : INT := 5;
    i                               : INT;
    FreeSlotFound                    : BOOL;

    Prev_InspectionSensor               : BOOL;
    Prev_AIHeartbeat                      : INT;
    T_HeartbeatWatch                        : TON;

    HeadIdx                                   : INT;
    CurrentRoute                                : E_SortRoute;
END_VAR

// ------------------------------------------------------------------
// 1. NEW ITEM DETECTION - push into the tracking queue
// ------------------------------------------------------------------
IF DI_System_Enable AND DI_ItemPresent_InspectionPoint AND (NOT Prev_InspectionSensor) THEN
    HR0_ItemTriggerCounter := HR0_ItemTriggerCounter + 1;

    FreeSlotFound := FALSE;
    FOR i := 0 TO QueueDepth - 1 DO
        IF (NOT Queue[i].Active) AND (NOT FreeSlotFound) THEN
            Queue[i].Active := TRUE;
            Queue[i].ItemID := HR0_ItemTriggerCounter;
            Queue[i].ResultReceived := FALSE;
            Queue[i].TransitTimer(IN := TRUE, PT := TransitDelay_PT);
            FreeSlotFound := TRUE;
        END_IF
    END_FOR

    IF NOT FreeSlotFound THEN
        Alarm_QueueFull := TRUE;   // More items in transit than the queue can track -
    END_IF                          // a real line would stop infeed on this alarm.
END_IF
Prev_InspectionSensor := DI_ItemPresent_InspectionPoint;

// ------------------------------------------------------------------
// 2. MATCH INCOMING AI RESULTS TO A TRACKED ITEM
// ------------------------------------------------------------------
HR6_Clear_Ack := FALSE;
IF HR6_AIResultReady THEN
    FOR i := 0 TO QueueDepth - 1 DO
        IF Queue[i].Active AND (Queue[i].ItemID = HR1_ItemIDAck) AND (NOT Queue[i].ResultReceived) THEN
            Queue[i].ResultReceived := TRUE;
            Queue[i].Defect_Detected := HR2_DefectDetected;
            Queue[i].Confidence_Pct := INT_TO_REAL(HR3_ConfidencePctX10) / 10.0;
            Queue[i].Defect_Class_ID := HR4_DefectClassID;
        END_IF
    END_FOR
    HR6_Clear_Ack := TRUE;   // Tell the AI service its result has been consumed
END_IF

// ------------------------------------------------------------------
// 3. AI HEARTBEAT WATCHDOG
// ------------------------------------------------------------------
IF HR5_AIHeartbeat <> Prev_AIHeartbeat THEN
    T_HeartbeatWatch(IN := FALSE);
    Alarm_AI_Offline := FALSE;
ELSE
    T_HeartbeatWatch(IN := TRUE, PT := HeartbeatTimeout_PT);
    IF T_HeartbeatWatch.Q THEN
        Alarm_AI_Offline := TRUE;
    END_IF
END_IF
Prev_AIHeartbeat := HR5_AIHeartbeat;

// ------------------------------------------------------------------
// 4. QUEUE HEAD ARRIVAL AND ROUTING DECISION
//    Fail-safe priority: no result / AI offline / low confidence /
//    uncertain-band confidence ALL route to a human, before the AI's
//    actual verdict is even considered.
// ------------------------------------------------------------------
FOR i := 0 TO QueueDepth - 1 DO
    Queue[i].TransitTimer(IN := Queue[i].Active, PT := TransitDelay_PT);

    IF Queue[i].Active AND Queue[i].TransitTimer.Q THEN
        IF (NOT Queue[i].ResultReceived) OR Alarm_AI_Offline THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Confidence_Pct < LowConfidence_Pct THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Confidence_Pct < HighConfidence_Pct THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Defect_Detected THEN
            CurrentRoute := ROUTE_REJECT;
        ELSE
            CurrentRoute := ROUTE_PASS;
        END_IF

        CASE CurrentRoute OF
            ROUTE_PASS:           DO_DiverterArm_Position := 0; ItemsSorted_Pass := ItemsSorted_Pass + 1;
            ROUTE_REJECT:         DO_DiverterArm_Position := 1; ItemsSorted_Reject := ItemsSorted_Reject + 1;
            ROUTE_MANUAL_REVIEW:  DO_DiverterArm_Position := 2; ItemsSorted_ManualReview := ItemsSorted_ManualReview + 1;
            ELSE                  ;
        END_CASE

        // Cross-check: did the item physically arrive when the timer
        // said it should? A large mismatch suggests conveyor slip or a
        // miscounted item - worth flagging even though the sort itself
        // still proceeds on the timer-based decision.
        Alarm_TrackingMismatch := Alarm_TrackingMismatch
                                    OR (Queue[i].TransitTimer.Q AND (NOT DI_ItemPresent_DiverterPoint));

        Queue[i].Active := FALSE;
        Queue[i].TransitTimer(IN := FALSE);
    END_IF
END_FOR

// ------------------------------------------------------------------
// 5. STATUS TEXT
// ------------------------------------------------------------------
IF NOT DI_System_Enable THEN
    SystemStatus := 'STANDBY';
ELSIF Alarm_AI_Offline THEN
    SystemStatus := 'AI OFFLINE - MANUAL ONLY';
ELSIF Alarm_QueueFull THEN
    SystemStatus := 'QUEUE FULL';
ELSE
    SystemStatus := 'SORTING ACTIVE';
END_IF

END_FUNCTION_BLOCK
