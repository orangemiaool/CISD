
import sys
import socket
import struct
import random
from rules import read_domain_name, my_DNS, TYPE, CLASS

def read_root_hints(filename):
    root_hints = []

    with open(filename, "r") as file:
        lines = file.readlines()

    record = {}
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue

        if parts[0].startswith(";"):
            continue

        if parts[0] == ".":
            if record:
                root_hints.append(record)
                record = {}
        else:
            if parts[2] == "A": 
                record["name"] = parts[0]
                record["ttl"] = int(parts[1])
                record["type"] = parts[2]
                record["data"] = parts[3]
    
    if record:
        root_hints.append(record)

    return root_hints

def resolve_query(query):
    domain_name, _ = read_domain_name(query, 12)
    domain_name = domain_name.decode("ASCII")
    # Handle PTR type queries

    reverse_mapping = {
    "1.0.0.127.in-addr.arpa": "localhost",  # Example entry: Reverse mapping for IP 127.0.0.1
    "2.0.0.127.in-addr.arpa": "example.com",  # Example entry: Reverse mapping for IP 127.0.0.2
    # Add more entries as needed for other IP addresses and their corresponding domain names
}
    if query == TYPE["PTR"]:
        ip_address = domain_name  # The domain_name is the IP address in reverse format
        # Look up the IP address in your reverse mapping dictionary to find the associated domain name
        # Note: You need to build this reverse mapping dictionary based on your actual data
        domain_name = reverse_mapping[ip_address]
        
        # Create the DNS response message with the PTR record containing the domain name
        dns_response_message = my_DNS(domain_name, TYPE["PTR"], query_class)
    else:
        root_hints = read_root_hints("named.root")
        root_hint = random.choice(root_hints)
        root_ip = root_hint["data"]

        record_type = TYPE["A"]
        query_class = CLASS["IN"]

        dns_query_message = my_DNS(domain_name, record_type, query_class) 
        root_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        root_udp_socket.sendto(dns_query_message, (root_ip, 53))

        response, _ = root_udp_socket.recvfrom(1024)
        root_udp_socket.close()
        # Extract the response code from the DNS header
        dns_header = response[:12]
        response_code = struct.unpack("!H", dns_header[3:5])[0] 

        # Check if there's an error code in the response
        if response_code == 1:
            print("Error: Format Error - The name server was unable to interpret the query.")
        elif response_code == 2:
            print("Error: Server Failure - The name server was unable to process the query.")
        elif response_code == 3:
            print(f"Error: Name Error - The server can't find the domain name '{domain_name}'.")
        else:
            return response
    return dns_response_message


if len(sys.argv) != 2:
    print("Error: invalid arguments")
    print("Usage: resolver port")
    sys.exit(1)

port = int(sys.argv[1])

if not (1024 <= port <= 65535):
    print("Error: invalid arguments")
    print("Usage: resolver port")
    sys.exit(1)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
udp_socket.bind(("127.0.0.1", port))


print(f"Resolver is listening on 127.0.0.1: {port}")

while True:
    query, client_address = udp_socket.recvfrom(1024)
    print(f"Received query from {client_address}")
    timeout = 5
    udp_socket.settimeout(timeout)
    try:
        response = resolve_query(query)
        udp_socket.sendto(response, client_address)
    except socket.timeout:
        print("Timeout: Resolver did not respond in time.")
    except Exception as e:
        print(f"An error occurred: {e}")
 

