import json
import ipaddress
import socket
import subprocess

SWITCH = "s1"
LISTEN_IP = "0.0.0.0"
PORT = 8080


def apply_flow(command, flow):
    return subprocess.run(
        ["ovs-ofctl", "-O", "OpenFlow13", command, SWITCH, flow],
        check=True,
        capture_output=True,
        text=True
    )


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, PORT))
print(f"Python SDN controller running on UDP {PORT}")

while True:
    data, address = sock.recvfrom(4096)

    try:
        message = json.loads(data.decode())
        action = message["action"].lower()
        ip = str(ipaddress.ip_address(message["ip"]))
        port = int(message["port"])

        if action not in ("block", "unblock"):
            raise ValueError("Unknown action")
        if not 1 <= port <= 65535:
            raise ValueError("Invalid UDP port")

        match = f"priority=100,udp,nw_dst={ip},tp_dst={port}"

        if action == "block":
            apply_flow("add-flow", match + ",actions=drop")
            status = "BLOCKED"
        else:
            apply_flow("del-flows", match)
            status = "UNBLOCKED"

        print(status, f"{ip}:{port}")
        response = {"status": status, "ip": ip, "port": port}

    except (ValueError, KeyError, TypeError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print("Controller error:", error)
        response = {"status": "ERROR", "message": str(error)}

    sock.sendto(json.dumps(response).encode(), address)
