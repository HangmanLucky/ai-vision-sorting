# -*- coding: utf-8 -*-
"""
plc_simulator.py
------------------
A minimal, hand-written Modbus TCP SERVER standing in for the PLC's
holding-register map during development and testing - the same role
PLCSIM plays for the Structured Text projects elsewhere in this
portfolio: a stand-in for real hardware that lets the rest of the system
be genuinely exercised end-to-end.

Rather than depend on a third-party Modbus server implementation (whose
API changes significantly across versions), this implements just enough
of the Modbus TCP wire protocol - the MBAP header plus function codes 3
(Read Holding Registers), 6 (Write Single Register), and 16 (Write
Multiple Registers) - to stand in for the real PLC's Modbus TCP server
role. This is the same register map documented in docs/IO_List.md and
implemented for real in src/AI_SortingMatrix.st.

REGISTER MAP (holding registers, 0-based addressing):
  HR0  Item_Trigger_Counter   PLC increments on each new item detected
  HR1  Item_ID_Ack            Python echoes which item its result is for
  HR2  Defect_Detected        0/1, written by Python
  HR3  Confidence_x10         0-1000 (0.0-100.0%), written by Python
  HR4  Defect_Class_ID        0=None,1=Scratch,2=Dent,3=Discoloration
  HR5  AI_Heartbeat           Python increments every inference loop
  HR6  AI_Result_Ready        Python sets 1; this simulator clears it
                               after "consuming" the result, exactly as
                               the real PLC logic does in Section 4 of
                               AI_SortingMatrix.st

Author: Sipho Lucky Sibanda
"""

import socket
import struct
import threading
import time
import random
import sys

HOST = "127.0.0.1"
PORT = 5020
NUM_REGISTERS = 16

DEFECT_CLASS_NAMES = ["None", "Scratch", "Dent", "Discoloration"]


class PLCRegisterMap:
    def __init__(self):
        self.lock = threading.Lock()
        self.registers = [0] * NUM_REGISTERS
        self.item_counter = 0

    def read(self, address, count):
        with self.lock:
            return list(self.registers[address:address + count])

    def write_single(self, address, value):
        with self.lock:
            self.registers[address] = value & 0xFFFF

    def write_multiple(self, address, values):
        with self.lock:
            for i, v in enumerate(values):
                self.registers[address + i] = v & 0xFFFF


def handle_client(conn, regmap):
    with conn:
        while True:
            header = _recvall(conn, 7)
            if not header:
                return
            txn_id, proto_id, length, unit_id = struct.unpack(">HHHB", header)
            pdu = _recvall(conn, length - 1)
            if pdu is None:
                return
            fc = pdu[0]

            if fc == 3:  # Read Holding Registers
                start, qty = struct.unpack(">HH", pdu[1:5])
                values = regmap.read(start, qty)
                byte_count = qty * 2
                resp_pdu = struct.pack(">BB", 3, byte_count)
                for v in values:
                    resp_pdu += struct.pack(">H", v)

            elif fc == 6:  # Write Single Register
                addr, value = struct.unpack(">HH", pdu[1:5])
                regmap.write_single(addr, value)
                resp_pdu = pdu  # Echo request per spec

            elif fc == 16:  # Write Multiple Registers
                addr, qty, byte_count = struct.unpack(">HHB", pdu[1:6])
                data = pdu[6:6 + byte_count]
                values = list(struct.unpack(">" + "H" * qty, data))
                regmap.write_multiple(addr, values)
                resp_pdu = struct.pack(">HH", addr, qty)
                resp_pdu = struct.pack(">B", 16) + resp_pdu

            else:
                # Illegal function - exception response
                resp_pdu = struct.pack(">BB", fc | 0x80, 0x01)

            resp_header = struct.pack(">HHHB", txn_id, 0, len(resp_pdu) + 1, unit_id)
            conn.sendall(resp_header + resp_pdu)


def _recvall(conn, n):
    data = b""
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def item_trigger_thread(regmap, stop_event, interval_range=(1.2, 2.6)):
    """Simulates a photoeye at the inspection point firing at irregular
    intervals - a new item arrives, the trigger counter increments."""
    while not stop_event.is_set():
        time.sleep(random.uniform(*interval_range))
        with regmap.lock:
            regmap.item_counter += 1
            regmap.registers[0] = regmap.item_counter
            item_id = regmap.item_counter
        print(f"[PLC ] Item #{item_id:03d} detected at inspection point "
              f"(HR0 Item_Trigger_Counter -> {item_id})")


def result_consumer_thread(regmap, stop_event):
    """Simulates the PLC's own logic consuming a completed AI result:
    watches AI_Result_Ready (HR6), logs the verdict, then clears the
    flag - exactly Section 4 of AI_SortingMatrix.st."""
    last_seen_id = -1
    while not stop_event.is_set():
        time.sleep(0.1)
        with regmap.lock:
            ready = regmap.registers[6]
            item_id = regmap.registers[1]
            defect = regmap.registers[2]
            conf = regmap.registers[3]
            cls_id = regmap.registers[4]
        if ready == 1 and item_id != last_seen_id:
            verdict = "FAIL" if defect else "PASS"
            cls_name = DEFECT_CLASS_NAMES[cls_id] if 0 <= cls_id < len(DEFECT_CLASS_NAMES) else "?"
            print(f"[PLC ] Result for item #{item_id:03d}: {verdict}  "
                  f"(confidence {conf/10:.1f}%, class={cls_name}) - consuming and clearing HR6")
            with regmap.lock:
                regmap.registers[6] = 0
            last_seen_id = item_id


def heartbeat_watchdog_thread(regmap, stop_event, timeout_s=2.0):
    """Mirrors AI_SortingMatrix.st Section 5: if AI_Heartbeat (HR5) stops
    incrementing, the PLC declares the AI service offline."""
    last_hb = -1
    last_change = time.time()
    offline_declared = False
    while not stop_event.is_set():
        time.sleep(0.2)
        with regmap.lock:
            hb = regmap.registers[5]
        if hb != last_hb:
            last_hb = hb
            last_change = time.time()
            if offline_declared:
                print("[PLC ] AI_Heartbeat resumed - AI service back online")
                offline_declared = False
        elif (time.time() - last_change) > timeout_s and not offline_declared:
            print(f"[PLC ] *** AI_Heartbeat stale for >{timeout_s}s - "
                  f"declaring AI OFFLINE, routing all items to MANUAL REVIEW ***")
            offline_declared = True


def main(run_seconds=None):
    regmap = PLCRegisterMap()
    stop_event = threading.Event()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    server_sock.settimeout(0.5)
    print(f"[PLC ] Modbus TCP server (simulated PLC register map) listening on {HOST}:{PORT}")

    threading.Thread(target=item_trigger_thread, args=(regmap, stop_event), daemon=True).start()
    threading.Thread(target=result_consumer_thread, args=(regmap, stop_event), daemon=True).start()
    threading.Thread(target=heartbeat_watchdog_thread, args=(regmap, stop_event), daemon=True).start()

    start_time = time.time()
    try:
        while True:
            if run_seconds and (time.time() - start_time) > run_seconds:
                break
            try:
                conn, addr = server_sock.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_client, args=(conn, regmap), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server_sock.close()
        print("[PLC ] Server stopped.")


if __name__ == "__main__":
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else None
    main(run_seconds=seconds)
