import socket
import json
import time

BROKER_IP = "10.0.0.1"
BROKER_PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)


def send_request(address, message):

    start = time.perf_counter()

    client.sendto(
        json.dumps(message).encode(),
        address
    )

    data, server_address = client.recvfrom(4096)

    latency = (time.perf_counter() - start) * 1000

    return json.loads(data.decode()), latency


def discover_service(name):

    try:

        response, latency = send_request(
            (BROKER_IP, BROKER_PORT),
            {
                "action": "DISCOVER",
                "service": name
            }
        )

        print(f"Discovery latency: {latency:.3f} ms")

        if response["status"] == "FOUND":

            print("Service discovered!")

            return (
                response["ip"],
                response["port"]
            )

        print("Service unavailable.")
        return None

    except socket.timeout:

        print("Broker did not respond.")
        return None


def main():

    service_names = {
        "1": "calculator",
        "2": "messaging",
        "3": "file_info",
        "4": "network_monitor",
        "5": "time_service"
    }

    while True:

        print("\n============ UDP SERVICES ============")
        print("1. Calculator")
        print("2. Messaging")
        print("3. File Information")
        print("4. Network Monitor")
        print("5. Time Service")
        print("6. List Available Services")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "7":
            break

        if choice == "6":

            try:

                response, latency = send_request(
                    (BROKER_IP, BROKER_PORT),
                    {"action": "LIST"}
                )

                print("Available services:")
                print(response["services"])

            except socket.timeout:
                print("Broker did not respond.")

            continue

        if choice not in service_names:
            print("Invalid choice.")
            continue

        name = service_names[choice]

        worker = discover_service(name)

        if worker is None:
            continue

        if name == "calculator":

            try:
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
            except ValueError:
                print("Invalid numbers.")
                continue

            print("1. Add")
            print("2. Subtract")
            print("3. Multiply")
            print("4. Divide")

            operation_choice = input("Operation: ")

            operations = {
                "1": "add",
                "2": "subtract",
                "3": "multiply",
                "4": "divide"
            }

            if operation_choice not in operations:
                print("Invalid operation.")
                continue

            request = {
                "operation": operations[operation_choice],
                "a": a,
                "b": b
            }

        elif name == "messaging":

            request = {
                "message": input("Enter your message: ")
            }

        elif name == "file_info":

            request = {
                "filename": input("Enter filename: ")
            }

        else:

            request = {}

        try:

            response, latency = send_request(worker, request)

            print("\n======== SERVICE RESPONSE ========")
            print(json.dumps(response, indent=4))
            print(f"Worker response latency: {latency:.3f} ms")

        except socket.timeout:
            print("Worker did not respond.")

    client.close()


if __name__ == "__main__":
    main()