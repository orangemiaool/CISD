import sys
import socket
import struct 
import random
from rules import my_DNS, TYPE, CLASS

if len(sys.argv) != 5:
    print("Error: invalid arguments")
    print("Usage: client resolver_ip resolver_port name timeout")
    sys.exit(1)

resolver_ip = sys.argv[1]
resolver_port = int(sys.argv[2])
domain_name = sys.argv[3]
timeout = int(sys.argv[4])

if not (1025 <= resolver_port <= 65535) or timeout <= 0:
    print("Error: invalid arguments")
    print("Usage: client resolver_ip resolver_port name timeout")
    sys.exit(1)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# Prepare the DNS query message and send it to the resolver
udp_socket.sendto(my_DNS(domain_name, TYPE["A"], CLASS["IN"]), (resolver_ip, resolver_port))

udp_socket.settimeout(timeout)

def resolve(response):
    ip_addresses = []

    #extract IP addresses
    answer_count = struct.unpack("!H", response[6:8])[0]
    offset = 12  # Start offset for reading resource records
    for _ in range(answer_count):
        offset += len(response[offset:]) - len(response[offset:].lstrip(b"\xc0\x0c\x00\x01"))
        offset += 4
        r_type, r_class, _, r_data_length = struct.unpack("!HHIH", response[offset:offset + 10])
        offset += 10
        r_data = response[offset:offset + r_data_length]
        if r_type == 1: 
            ip_addresses.append(".".join(str(byte) for byte in r_data))
        
        offset += r_data_length
    return ip_addresses

try:
    response = udp_socket.recv(1024)
    dns_header = response[:12]
    # Extract the response code from the DNS header
    response_code = struct.unpack("!H", dns_header[3:5])[0] 
    # Check if there's an error code in the response
    if response_code == 1:
        print("Error: Format Error - The name server was unable to interpret the query.")
    elif response_code == 2:
        print("Error: Server Failure - The name server was unable to process the query.")
    elif response_code == 3:
        print(f"Error: Name Error - The server can't find the domain name '{domain_name}'.")
    else:
        ip_addresses = resolve(response)
        print(f"Successfully received IP addresses: {ip_addresses}")

except socket.timeout:
    print("Timeout: Resolver did not respond in time.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    udp_socket.close()
