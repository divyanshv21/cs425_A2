import dns.message
import dns.query
import dns.rdatatype
import dns.resolver
import time

# Root DNS servers used to start the iterative resolution process.
# These are hardcoded and are used to begin the DNS query chain from the root servers.
ROOT_SERVERS = {
    "198.41.0.4": "Root (a.root-servers.net)",
    "199.9.14.201": "Root (b.root-servers.net)",
    "192.33.4.12": "Root (c.root-servers.net)",
    "199.7.91.13": "Root (d.root-servers.net)",
    "192.203.230.10": "Root (e.root-servers.net)"
}

TIMEOUT = 3  # Timeout duration (in seconds) for each DNS query attempt


def send_dns_query(server, domain):
    """
    Sends a DNS query to the given server for an A record of the specified domain.
    Returns the response if successful, otherwise returns None.
    Handles potential exceptions such as network errors or timeouts.
    """
    try:
        # Create a DNS query message for the A record (IPv4 address) of the domain
        query = dns.message.make_query(domain, dns.rdatatype.A)

        # Send the query via UDP to the DNS server with a specified timeout
        response = dns.query.udp(query, server, timeout=TIMEOUT)

        return response  # Return the DNS response if successful
    except Exception as e:
        # If an error occurs (e.g., timeout, network issue), print an error message and return None
        print(f"[ERROR] Query failed: {e}")
        return None


def extract_next_nameservers(response):
    """
    Extracts nameserver (NS) records from the authority section of the DNS response.
    Resolves those NS names to IP addresses and returns a list of IPs of the next authoritative nameservers.
    Handles cases where resolving the NS records may fail.
    """
    ns_ips = []  # List to store resolved nameserver IPs
    ns_names = []  # List to store nameserver domain names (hostnames)

    # Loop through the authority section of the DNS response to find NS records
    for rrset in response.authority:
        if rrset.rdtype == dns.rdatatype.NS:
            # For each NS record, extract the nameserver hostname
            for rr in rrset:
                ns_name = rr.to_text()  # Convert the NS record to a string (hostname)
                ns_names.append(ns_name)  # Add to list of nameservers
                print(f"Extracted NS hostname: {ns_name}")

    # Attempt to resolve each NS hostname to an IP address (A record)
    for ns_name in ns_names:
        try:
            # Resolve the nameserver's hostname to an IP address
            resolved_ips = dns.resolver.resolve(ns_name, "A")

            # For each resolved IP, append it to the list and print the result
            for ip in resolved_ips:
                ns_ips.append(ip.to_text())  # Convert the IP address to a string
                print(f"Resolved {ns_name} to {ip}")
        except Exception as e:
            # If resolving the nameserver fails, print an error message
            print(f"[ERROR] Failed to resolve {ns_name}: {e}")

    # Return the list of resolved nameserver IP addresses
    return ns_ips


def iterative_dns_lookup(domain):
    """
    Performs an iterative DNS resolution starting from root servers.
    The process queries root servers, then TLD servers, and finally authoritative servers,
    following the DNS hierarchy until an answer is found or resolution fails.
    """
    print(f"[Iterative DNS Lookup] Resolving {domain}")

    # Start with the list of root server IPs, which are stored in the ROOT_SERVERS dictionary
    next_ns_list = list(ROOT_SERVERS.keys())
    stage = "ROOT"  # Track the current stage of resolution (ROOT, TLD, AUTH)

    # Perform iterative DNS resolution by querying servers and following the DNS hierarchy
    while next_ns_list:
        ns_ip = next_ns_list.pop(0)  # Get the first nameserver in the list
        response = send_dns_query(ns_ip, domain)  # Send DNS query to the nameserver

        if response:
            # If a response is received, print debug info
            print(f"[DEBUG] Querying {stage} server ({ns_ip}) - SUCCESS")

            # If an answer is found in the response, print the result and stop further queries
            if response.answer:
                print(f"[SUCCESS] {domain} -> {response.answer[0][0]}")
                return

            # If no answer is found, extract the next batch of nameservers and move to the next stage
            next_ns_list = extract_next_nameservers(response)
            if stage == "ROOT":
                stage = "TLD"  # Move to TLD server stage after querying root
            elif stage == "TLD":
                stage = "AUTH"  # Move to AUTH server stage after querying TLD servers
        else:
            # If the query fails (e.g., server is unreachable or times out), print an error message
            print(f"[ERROR] Query failed for {stage} {ns_ip}")
            return  # Stop resolution if a query fails

    # If no nameservers respond at any point, print a final error message indicating resolution failure
    print("[ERROR] Resolution failed.")


def recursive_dns_lookup(domain):
    """
    Performs recursive DNS resolution using the system's default resolver.
    This approach relies on an external DNS resolver (e.g., Google DNS or a local ISP resolver)
    to recursively fetch the result.
    """
    print(f"[Recursive DNS Lookup] Resolving {domain}")
    try:
        # First, resolve NS records
        ns_answer = dns.resolver.resolve(domain, "NS")
        for rdata in ns_answer:
            # rdata.target is the nameserver's hostname
            print(f"[SUCCESS] {domain} -> {rdata.target}")

        # Next, resolve A records
        a_answer = dns.resolver.resolve(domain, "A")
        for rdata in a_answer:
            # rdata is the IP address
            print(f"[SUCCESS] {domain} -> {rdata}")

    except Exception as e:
        print(f"[ERROR] Recursive lookup failed: {e}")


if __name__ == "__main__":
    import sys

    # Check if the script is being executed with the correct arguments
    if len(sys.argv) != 3 or sys.argv[1] not in {"iterative", "recursive"}:
        print("Usage: python3 dns_server.py <iterative|recursive> <domain>")
        sys.exit(1)  # Exit the program with an error code if arguments are incorrect

    mode = sys.argv[1]  # Get the DNS resolution mode (iterative or recursive)
    domain = sys.argv[2]  # Get the domain name to resolve
    start_time = time.time()  # Record the start time to measure execution duration

    # Execute the selected DNS resolution mode
    if mode == "iterative":
        iterative_dns_lookup(domain)  # Perform iterative DNS lookup if the mode is 'iterative'
    else:
        recursive_dns_lookup(domain)  # Perform recursive DNS lookup if the mode is 'recursive'

    # Calculate and print the time taken to execute the DNS resolution
    print(f"Time taken: {time.time() - start_time:.3f} seconds")