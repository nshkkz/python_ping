import sys
from pythonping import ping

if __name__ == "__main__":
    ip = None
    if len(sys.argv) < 2:
        ip = input("Enter IP address (from 0.0.0.0 to 255.255.255.255) or domain (ex. 'google.com'): ")
    else:
        ip = sys.argv[1]
    
    try:
        stats = ping(ip, verbose=True, count=5)
		
        print(f"RTT (min/avg/max): {stats.rtt_min_ms:.2f}ms/{stats.rtt_avg_ms:.2f}ms/{stats.rtt_max_ms:.2f}ms")
        print(f"Packets sent: {stats.stats_packets_sent}, \
packets returned: {stats.stats_packets_returned} ({(stats.stats_success_ratio * 100):.2f}%), \
packets lost: {stats.packets_lost} ({(stats.packet_loss * 100.0):.2f}%)")
    except Exception as ex:
        print(f"Failure to begin pinging: {ex}")
