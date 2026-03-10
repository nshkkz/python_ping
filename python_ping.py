import sys
from ipaddress import IPv4Address
from pythonping import ping


def expand_targets(raw_input):
    targets = []
    seen = set()

    for part in raw_input.split(","):
        token = part.strip()
        if not token:
            continue

        if "-" in token:
            start_text, end_text = [p.strip() for p in token.split("-", 1)]
            try:
                start_ip = IPv4Address(start_text)
                end_ip = IPv4Address(end_text)
            except ValueError:
                # Not an IPv4 range, treat as a normal hostname/target.
                if token not in seen:
                    seen.add(token)
                    targets.append(token)
                continue

            if int(start_ip) > int(end_ip):
                raise ValueError(f"Invalid range '{token}': start IP is greater than end IP.")

            for ip_int in range(int(start_ip), int(end_ip) + 1):
                ip_text = str(IPv4Address(ip_int))
                if ip_text not in seen:
                    seen.add(ip_text)
                    targets.append(ip_text)
            continue

        if token not in seen:
            seen.add(token)
            targets.append(token)

    if not targets:
        raise ValueError("No valid targets were provided.")

    return targets


def ping_single_target(target):
    stats = ping(target, verbose=True, count=5)

    print(
        f"RTT (min/avg/max): "
        f"{stats.rtt_min_ms:.2f}ms/{stats.rtt_avg_ms:.2f}ms/{stats.rtt_max_ms:.2f}ms"
    )
    print(
        f"Packets sent: {stats.stats_packets_sent}, "
        f"packets returned: {stats.stats_packets_returned} ({(stats.stats_success_ratio * 100):.2f}%), "
        f"packets lost: {stats.packets_lost} ({(stats.packet_loss * 100.0):.2f}%)"
    )


def ping_multiple_targets(targets):
    single_probe_mode = len(targets) > 5
    ping_count = 1 if single_probe_mode else 5

    print(f"Pinging {len(targets)} targets (count={ping_count} each)...")

    responded = []
    no_response = []
    failures = []

    for target in targets:
        try:
            stats = ping(target, verbose=True, count=ping_count, timeout=1)
            if stats.stats_packets_returned > 0:
                responded.append(target)
            else:
                no_response.append(target)

            if not single_probe_mode:
                if stats.stats_packets_returned > 0:
                    print(
                        f"{target}: RTT(min/avg/max) "
                        f"{stats.rtt_min_ms:.2f}ms/{stats.rtt_avg_ms:.2f}ms/{stats.rtt_max_ms:.2f}ms "
                        f"| success {(stats.stats_success_ratio * 100):.2f}%"
                    )
                else:
                    print(f"{target}: no response")
        except Exception as ex:
            failures.append((target, str(ex)))

    if single_probe_mode:
        print("\nResponse summary:")
        print(f"Responded ({len(responded)}): {', '.join(responded) if responded else 'None'}")
        print(f"No response ({len(no_response)}): {', '.join(no_response) if no_response else 'None'}")

    if failures:
        print("\nErrors:")
        for target, error_msg in failures:
            print(f"{target}: {error_msg}")

if __name__ == "__main__":
    raw_target = None
    if len(sys.argv) < 2:
        raw_target = input(
            "Enter IP address/domain, comma-separated targets, or IPv4 ranges (ex. '192.168.1.1-192.168.1.255,1.1.1.1,google.com'): "
        )
    else:
        raw_target = " ".join(sys.argv[1:])

    try:
        targets = expand_targets(raw_target)

        if len(targets) == 1:
            ping_single_target(targets[0])
        else:
            ping_multiple_targets(targets)
    except Exception as ex:
        print(f"Failure to begin pinging: {ex}")
