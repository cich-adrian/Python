#!/usr/bin/env python3
import socket
import struct
import time
import os
import sys
import platform
import select
import argparse

# ICMP Header Fields
ICMP_ECHO_REQUEST = 8
ICMP_CODE = 0

def checksum(source_string):
    """Calculate the checksum of a source string."""
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum += this_val
        sum = sum & 0xffffffff
        count += 2

    if count_to < len(source_string):
        sum += source_string[-1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(seq_number, packet_size):
    """Create a new ICMP echo request packet."""
    if packet_size < 64 or packet_size > 1500:
        print("Rozmiar pakietu musi mieścić się w zakresie 64–1500 bajtów.")
        sys.exit(1)

    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, ICMP_CODE, 0, os.getpid() & 0xFFFF, seq_number)
    data = (packet_size - 8) * b'Q'  # Payload filled with 'Q'
    my_checksum = checksum(header + data)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, ICMP_CODE, my_checksum, os.getpid() & 0xFFFF, seq_number)
    return header + data

def send_ping(sock, addr, seq_number, packet_size):
    """Send an ICMP packet."""
    packet = create_packet(seq_number, packet_size)
    sock.sendto(packet, (addr, 1))

def receive_ping(sock, timeout):
    """Receive the ping response."""
    start_time = time.time()
    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0] == []:  # Timeout
            return None, None, None
        time_received = time.time()
        recv_packet, addr = sock.recvfrom(1024)
        icmp_header = recv_packet[20:28]
        icmp_type, icmp_code, _, _, seq = struct.unpack('!BBHHH', icmp_header)
        ttl = recv_packet[8]
        if icmp_type == 0 and icmp_code == 0:  # Echo reply
            return time_received, seq, ttl

def ping(host, count=5, packet_size=64, rapid=False, wait=1):
    """Ping a host."""
    try:
        addr = socket.gethostbyname(host)
        print(f'PING {host} ({addr}): {packet_size} data bytes')
    except socket.gaierror as e:
        print(f'Ping request could not find host {host}. Please check the name and try again.')
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("Root privileges are required to run this script.")
        sys.exit(1)

    rtts = []
    sent_packets = 0
    received_packets = 0
    seq_number = 0

    try:
        if rapid:
            output = []  # Buffer for rapid output
        
        while seq_number < count:
            sent_packets += 1
            send_time = time.time()
            send_ping(sock, addr, seq_number, packet_size)
            try:
                recv_time, seq, ttl = receive_ping(sock, timeout=0.5 if rapid else 1)
                if recv_time:
                    received_packets += 1
                    rtt = (recv_time - send_time) * 1000
                    rtts.append(rtt)
                    if rapid:
                        output.append("!")
                    else:
                        print(f'{packet_size + 8} bytes from {addr}: icmp_seq={seq} ttl={ttl} time={rtt:.3f} ms')
                else:
                    if rapid:
                        output.append(".")
                    else:
                        print(f'Request timeout for icmp_seq {seq_number}')
            except Exception as e:
                print(f'Error: {e}')
            seq_number += 1
            if not rapid:
                time.sleep(wait)

        if rapid:
            print("".join(output))

    except KeyboardInterrupt:
        print("\n--- Ping interrupted by user ---")
    finally:
        sock.close()
        # Print statistics
        print(f'\n--- {host} ping statistics ---')
        if sent_packets > 0:  # Avoid division by zero
            print(f'{sent_packets} packets transmitted, {received_packets} packets received, '
                  f'{(sent_packets - received_packets) / sent_packets * 100:.1f}% packet loss')
            if rtts:
                print(f'round-trip min/avg/max = {min(rtts):.3f}/{sum(rtts)/len(rtts):.3f}/{max(rtts):.3f} ms')
        else:
            print("No packets were transmitted.")

if __name__ == "__main__":
    if platform.system().lower() != 'windows' and os.geteuid() != 0:
        print("This script requires root privileges to run on Linux.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Ping a host in JunOS style")
    parser.add_argument("host", help="Target host to ping (e.g., 192.168.1.3 or example.com)")
    parser.add_argument("--size", type=int, default=64, help="Rozmiar pakietu w bajtach (domyślnie: 64, zakres: 64–1500)")
    parser.add_argument("--count", type=int, default=5, help="Number of packets to send (default: 5)")
    parser.add_argument("--rapid", action="store_true", help="Send packets as fast as possible without waiting")
    parser.add_argument("--wait", type=int, default=1, help="Wait time in seconds between packets (default: 1 second)")
    args = parser.parse_args()

    ping(args.host, count=args.count, packet_size=args.size, rapid=args.rapid, wait=args.wait)
