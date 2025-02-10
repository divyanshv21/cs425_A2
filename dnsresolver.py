import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
import time

# Root DNS servers used to start the iterative resolution process
ROOT_SERVERS = {
    "198.41.0.4": "Root (a.root-servers.net)",
    "199.9.14.201": "Root (b.root-servers.net)",
    "192.33.4.12": "Root (c.root-servers.net)",
    "199.7.91.13": "Root (d.root-servers.net)",
    "192.203.230.10": "Root (e.root-servers.net)"
}

TIMEOUT = 3  # Timeout in seconds for each DNS query attempt


def send_dns_query(server, domain):
    """ 
    Sends a DNS query to the given server for an A record of the specified domain.
    Returns the response if successful, otherwise returns None.
    """
    try:
        query = dns.message.make_query(domain, dns.rdatatype.A)  # Construct the DNS query
        response = dns.query.udp(query, server, timeout=TIMEOUT)  # Send the query using UDP
        return response
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return None


def extract_next_nameservers(response):
    """
    Extracts nameserver (NS) records from the authority section of the response.
    Then, resolves those NS names to IP addresses.
    Returns a list of IPs of the next authoritative nameservers.
    """
    ns_ips = []  # List to store resolved nameserver IPs
    ns_names = []  # List to store nameserver domain names

    # Loop through the authority section to extract NS records
    for rrset in response.authority:
        if rrset.rdtype == dns.rdatatype.NS:
            for rr in rrset:
                ns_name = rr.to_text()
                ns_names.append(ns_name)  # Extract nameserver hostname
                print(f"Extracted NS hostname: {ns_name}")

    # Resolve the extracted NS hostnames to IP addresses
    for ns_name in ns_names:
        try:
            resolved_ips = dns.resolver.resolve(ns_name, "A")
            for ip in resolved_ips:
                ns_ips.append(ip.to_text())
                print(f"Resolved {ns_name} to {ip}")
        except Exception as e:
            print(f"[ERROR] Failed to resolve {ns_name}: {e}")

    return ns_ips  # Return list of resolved nameserver IPs


def iterative_dns_lookup(domain):
    """
    Performs an iterative DNS resolution starting from root servers.
    It queries root servers, then TLD servers, then authoritative servers,
    following the hierarchy until an answer is found or resolution fails.
    """
    print(f"[Iterative DNS Lookup] Resolving {domain}")

    next_ns_list = list(ROOT_SERVERS.keys())  # Start with the root server IPs
    stage = "ROOT"  # Track resolution stage (ROOT, TLD, AUTH)

    while next_ns_list:
        ns_ip = next_ns_list.pop(0)  # Get the first nameserver to query
        response = send_dns_query(ns_ip, domain)

        if response:
            print(f"[DEBUG] Querying {stage} server ({ns_ip}) - SUCCESS")

            # If an answer is found, print and return
            if response.answer:
                print(f"[SUCCESS] {domain} -> {response.answer[0][0]}")
                return

            # If no answer, extract next nameservers and move to next stage
            next_ns_list = extract_next_nameservers(response)
            if stage == "ROOT":
                stage = "TLD"
            elif stage == "TLD":
                stage = "AUTH"
        else:
            print(f"[ERROR] Query failed for {stage} {ns_ip}")
            return  # Stop resolution if a query fails

    print("[ERROR] Resolution failed.")  # Final failure message if no nameservers respond


def recursive_dns_lookup(domain):
    """
    Performs recursive DNS resolution using the system's default resolver.
    This approach relies on a resolver (like Google DNS or a local ISP resolver)
    to fetch the result recursively.
    """
    print(f"[Recursive DNS Lookup] Resolving {domain}")
    try:
        answer = dns.resolver.resolve(domain, "A")
        for rdata in answer:
            print(f"[SUCCESS] {domain} -> {rdata}")
    except Exception as e:
        print(f"[ERROR] Recursive lookup failed: {e}")  # Handle resolution failure


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3 or sys.argv[1] not in {"iterative", "recursive"}:
        print("Usage: python3 dns_server.py <iterative|recursive> <domain>")
        sys.exit(1)

    mode = sys.argv[1]  # Get mode (iterative or recursive)
    domain = sys.argv[2]  # Get domain to resolve
    start_time = time.time()  # Record start time

    # Execute the selected DNS resolution mode
    if mode == "iterative":
        iterative_dns_lookup(domain)
    else:
        recursive_dns_lookup(domain)

    print(f"Time taken: {time.time() - start_time:.3f} seconds")  # Print execution time