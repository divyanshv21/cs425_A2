# DNS Resolver Script

## Group Members

- **Deepika Sahu (210314)**
- **Satyam Gupta (210942)**
- **Divyansh Verma (210360)**

This script implements both **iterative** and **recursive** DNS resolution methods to resolve domain names to their respective IP addresses. The script queries DNS servers to retrieve A records (IPv4 addresses) of a given domain, and can operate using two modes:

1. **Iterative DNS Resolution** – Starts from the root DNS servers and performs iterative resolution.
2. **Recursive DNS Resolution** – Uses the system’s default resolver to fetch the result.

## Challenges Faced
- **Complex DNS Resolution Process:**  
  Implementing the iterative DNS lookup required an in-depth understanding of the DNS hierarchy and managing multiple types of responses. Handling varying responses from different servers (root, TLD, and authoritative) was non-trivial.

- **Dynamic DNS Responses:**  
  The recursive DNS lookup can produce different outputs on subsequent runs. This is due to load balancing, round-robin DNS, and geo-distribution of servers, which makes consistency a challenge.

- **Error Handling and Debugging:**  
  Managing timeouts and network errors, as well as providing clear debugging information without overwhelming the user, required careful consideration and iterative improvements.

- **Resolver Behavior:**  
  The behavior of system resolvers and external DNS servers sometimes led to unpredictable output ordering and content, necessitating robust handling and clear output formatting.

## Limitations
- **Inconsistent Output:**  
  The recursive lookup mode can yield different results for the same domain on different runs due to load balancing and DNS round-robin techniques.

- **No Caching Mechanism:**  
  Every query results in a fresh DNS lookup. There is no caching, which could otherwise improve performance for repeated queries.

- **Network Dependency:**  
  The script's success is highly reliant on stable network conditions and the responsiveness of external DNS servers.

## Workload Distribution
- **Deepika Sahu (34%):**
  - Led project planning and initial system design.
  - Developed the iterative DNS lookup component.
  - Managed extensive testing and debugging for the iterative resolution process.

- **Divyansh Verma (33%):**
  - Designed and implemented the recursive DNS lookup functionality.
  - Integrated error handling to improve system robustness.
  - Contributed to code documentation and refining the output format.

- **Satyam Gupta (33%):**
  - Coordinated the integration of iterative and recursive components into a cohesive project.
  - Worked on performance measurement and final system optimizations.
  - Created the README  file and provided detailed usage instructions.

## Requirements

This script requires the following Python packages:

- `dnspython` - A powerful DNS library for Python.

You can install this package using pip:

```bash
pip install dnspython
```

# How to Run

### Command-Line Usage

To use the script, run it from the command line with one of the following modes:
-	Iterative mode: Queries the DNS servers starting from the root servers.
-   Recursive mode: Uses the system’s default DNS resolver to resolve the domain.

Syntax:
```
python3 dns_server.py <mode> <domain>
```


Parameters:
- \<mode>: Specify the mode of DNS resolution. This can be either iterative or recursive.
- \<domain>: Specify the domain name you want to resolve (e.g. google.com).

Example Commands:
1.	Iterative DNS Lookup:

```
python3 dns_server.py iterative example.com
```

This command will perform an iterative DNS resolution for the domain example.com, starting from the root servers.

2. Recursive DNS Lookup:

```
python3 dns_server.py recursive example.com
```

This command will perform a recursive DNS resolution for the domain example.com using the system’s default DNS resolver.

Output:

The script will print the resolution process, including which servers are being queried and the resolved IP address, or any error that occurs during the resolution.

Sample Output for Iterative Mode:

```
[Iterative DNS Lookup] Resolving example.com
Extracted NS hostname: b.gtld-servers.net
Resolved b.gtld-servers.net to 192.12.94.30
Querying ROOT server (198.41.0.4) - SUCCESS
...
[SUCCESS] example.com -> 93.184.216.34
Time taken: 3.125 seconds

Sample Output for Recursive Mode:

[Recursive DNS Lookup] Resolving example.com
[SUCCESS] example.com -> 93.184.216.34
Time taken: 1.007 seconds

```

## Error Handling

The script handles several types of errors:
- Timeouts: If a DNS query times out, an error message will be printed.
- Incorrect Domain Names: If the domain does not exist, an error message will be shown.
- Unreachable Servers: If the DNS servers cannot be reached, the script will print an error and halt further queries.

## Sources Referred

- RFC 1035: https://tools.ietf.org/html/rfc1035
- Cloudflare Learning Center:
https://www.cloudflare.com/learning/dns/what-is-dns/
- dnspython Documentation:
https://www.dnspython.org/


## Declaration

We hereby declare that the code submitted is our original work and has not been plagiarized. 
