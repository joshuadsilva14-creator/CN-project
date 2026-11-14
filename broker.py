import socket
import json
import time

HOST = "0.0.0.0"
PORT = 5000
TIMEOUT = 15

# This is the host-side IP assigned to the Mininet switch bridge by topology.py.
CONTROLLER_IP = "10.0.0.100"
CONTROLLER_PORT = 8080

services = {}

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
server.settimeout(1)

print("UDP Broker Running on port", PORT)


def notify_controller(action, ip, port):
    message = {
        "action": action,
        "ip": ip,
        "port": port
    }

    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    controller_socket.settimeout(1)

    try:
        controller_socket.sendto(
            json.dumps(message).encode(),
            (CONTROLLER_IP, CONTROLLER_PORT)
        )
        data, _ = controller_socket.recvfrom(4096)
        response = json.loads(data.decode())
        print("SDN controller:", response.get("status", "No status"), ip, port)
        return response.get("status") in ("BLOCKED", "UNBLOCKED")

    except (socket.timeout, OSError, ValueError) as error:
        print("Controller notification failed:", error)
        return False

    finally:
        controller_socket.close()


def remove_expired_services():
    current_time = time.monotonic()

    for name, worker in list(services.items()):
        if current_time - worker["last_seen"] > TIMEOUT:
            print("Service expired:", name)
            notify_controller("block", worker["ip"], worker["port"])
            del services[name]


while True:
    try:
        data, address = server.recvfrom(4096)
        message = json.loads(data.decode())
        action = message.get("action")

        if action in ("REGISTER", "HEARTBEAT"):
            name = message["service"]
            worker_port = int(message["port"])

            if not name or not 1 <= worker_port <= 65535:
                raise ValueError("Invalid service or port")

            old_worker = services.get(name)
            needs_unblock = (
                action == "REGISTER"
                or old_worker is None
                or old_worker["ip"] != address[0]
                or old_worker["port"] != worker_port
            )

            services[name] = {
                "ip": address[0],
                "port": worker_port,
                "last_seen": time.monotonic()
            }

            if action == "REGISTER":
                print("Registered:", name, "at", address[0], worker_port)

            if needs_unblock:
                notify_controller("unblock", address[0], worker_port)

            response = {"status": "REGISTERED", "service": name}

        elif action == "DISCOVER":
            name = message["service"]
            worker = services.get(name)

            if worker and time.monotonic() - worker["last_seen"] <= TIMEOUT:
                response = {
                    "status": "FOUND",
                    "service": name,
                    "ip": worker["ip"],
                    "port": worker["port"]
                }
            else:
                services.pop(name, None)
                response = {"status": "NOT_FOUND"}

            print("Discovery:", name, response["status"])

        elif action == "LIST":
            active = [
                name for name, worker in services.items()
                if time.monotonic() - worker["last_seen"] <= TIMEOUT
            ]
            response = {"status": "SUCCESS", "services": active}

        else:
            response = {"status": "INVALID_REQUEST"}

        server.sendto(json.dumps(response).encode(), address)

    except socket.timeout:
        pass

    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        try:
            server.sendto(json.dumps({"status": "ERROR"}).encode(), address)
        except (UnboundLocalError, OSError):
            pass

    remove_expired_services()
