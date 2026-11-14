import socket
import json
import time
import sys
import threading
import os
import platform
from datetime import datetime

BROKER_IP = "10.0.0.1"
BROKER_PORT = 5000

HEARTBEAT_INTERVAL = 5

if len(sys.argv) != 3:
    print("Usage: python3 worker.py SERVICE_NAME PORT")
    sys.exit(1)

SERVICE_NAME = sys.argv[1]
SERVICE_PORT = int(sys.argv[2])

VALID_SERVICES = [
    "calculator",
    "messaging",
    "file_info",
    "network_monitor",
    "time_service"
]

if SERVICE_NAME not in VALID_SERVICES:
    print("Invalid service name")
    sys.exit(1)

if not 1 <= SERVICE_PORT <= 65535:
    print("Invalid port")
    sys.exit(1)


def send_heartbeats():

    heartbeat_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    first = True

    while True:

        action = "REGISTER" if first else "HEARTBEAT"
        first = False

        message = {
            "action": action,
            "service": SERVICE_NAME,
            "port": SERVICE_PORT
        }

        try:
            heartbeat_socket.sendto(
                json.dumps(message).encode(),
                (BROKER_IP, BROKER_PORT)
            )

        except OSError as e:
            print("Heartbeat error:", e)

        time.sleep(HEARTBEAT_INTERVAL)


def process_request(message):

    if SERVICE_NAME == "calculator":

        operation = message.get("operation")

        try:
            a = float(message["a"])
            b = float(message["b"])

            if operation == "add":
                result = a + b

            elif operation == "subtract":
                result = a - b

            elif operation == "multiply":
                result = a * b

            elif operation == "divide":

                if b == 0:
                    return {
                        "status": "ERROR",
                        "message": "Cannot divide by zero"
                    }

                result = a / b

            else:
                return {
                    "status": "ERROR",
                    "message": "Invalid operation"
                }

            return {
                "status": "SUCCESS",
                "result": result
            }

        except (ValueError, KeyError, TypeError):

            return {
                "status": "ERROR",
                "message": "Invalid calculator input"
            }

    elif SERVICE_NAME == "messaging":

        return {
            "status": "SUCCESS",
            "message": message.get("message", "")
        }

    elif SERVICE_NAME == "file_info":

        filename = message.get("filename", "")

        if not filename:
            return {"status": "ERROR", "message": "Filename required"}

        if os.path.basename(filename) != filename:
            return {"status": "ERROR", "message": "Invalid filename"}

        if not os.path.isfile(filename):
            return {"status": "NOT_FOUND", "message": "File does not exist"}

        return {
            "status": "SUCCESS",
            "filename": filename,
            "size_bytes": os.path.getsize(filename),
            "modified": datetime.fromtimestamp(
                os.path.getmtime(filename)
            ).isoformat()
        }

    elif SERVICE_NAME == "network_monitor":

        return {
            "status": "SUCCESS",
            "hostname": socket.gethostname(),
            "system": platform.system(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().isoformat()
        }

    elif SERVICE_NAME == "time_service":

        return {
            "status": "SUCCESS",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    return {"status": "ERROR"}


def main():

    threading.Thread(
        target=send_heartbeats,
        daemon=True
    ).start()

    worker_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    worker_socket.bind(("0.0.0.0", SERVICE_PORT))

    print(SERVICE_NAME, "worker running on port", SERVICE_PORT)

    while True:

        try:

            data, client_address = worker_socket.recvfrom(4096)

            message = json.loads(data.decode())

            response = process_request(message)

            worker_socket.sendto(
                json.dumps(response).encode(),
                client_address
            )

        except (ValueError, TypeError, json.JSONDecodeError):

            print("Invalid client request")

        except OSError as e:

            print("Socket error:", e)


if __name__ == "__main__":
    main()