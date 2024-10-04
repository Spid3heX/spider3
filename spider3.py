import os
import subprocess
import requests
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import time
import pyfiglet

# Global variables
VERSION = "v2.6.0 (outdated)"
CREATOR = "projectdiscovery.io"
TOOL_NAME = "Spider3"

# Stylish banner function using Figlet
def banner(phase):
    if phase == 'main':
        figlet_banner = pyfiglet.figlet_format(TOOL_NAME)
        print(colored(figlet_banner, "blue"))
        print(colored(f"                {CREATOR}", "yellow"))
        print(colored(f"[INF] Current {TOOL_NAME} version {VERSION}", "yellow"))
        print(colored("[INF] Loading provider config from set location", "yellow"))
    elif phase == 'subdomain':
        print(colored("\n[+] Spider3 Phase 1: Enumerating Subdomains", "cyan"))
        print(colored("============================================================", "cyan"))
    elif phase == 'status':
        print(colored("\n[+] Spider3 Phase 2: HTTP Status Checking for Live Hosts", "cyan"))
        print(colored("============================================================", "cyan"))
    elif phase == 'urls':
        print(colored("\n[+] Spider3 Phase 3: URL Gathering", "cyan"))
        print(colored("============================================================", "cyan"))

# Function to create necessary files and directories
def setup(domain):
    if not os.path.exists(domain):
        os.makedirs(domain)
    open(f"{domain}/subdomain.txt", 'w').close()
    open(f"{domain}/livehost.txt", 'w').close()
    open(f"{domain}/urls.txt", 'w').close()

# Subdomain finder using subfinder
def find_subdomains(domain):
    subdomains = set()
    print(colored(f"[INF] Enumerating subdomains for {domain}...", "yellow"))
    command = f"subfinder -d {domain} -silent"  # Using subfinder as an example
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        subdomain_list = result.stdout.splitlines()
        
        for subdomain in subdomain_list:
            subdomains.add(subdomain)
            print(colored(f"[INF] Found subdomain: {subdomain}", "white"))
        
        elapsed_time = time.time() - start_time
        print(colored(f"[INF] Found {len(subdomain_list)} subdomains for {domain} in {elapsed_time:.2f} seconds", "yellow"))
        
    except subprocess.CalledProcessError as e:
        print(colored(f"Error running subfinder: {e}", "red"))
    except FileNotFoundError:
        print(colored("subfinder is not installed or not in PATH", "red"))
    return subdomains

# Check live subdomains with concurrent requests
def check_live_subdomains(subdomains):
    live_subdomains = set()
    print(colored("[INF] Checking for live subdomains...", "yellow"))

    def check_subdomain(subdomain):
        protocols = ['http', 'https']
        for protocol in protocols:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(colored(f"Live: {url}", "white") + colored(" [Status: Live]", "blue"))
                    return url
            except (requests.ConnectionError, requests.Timeout):
                pass
        print(colored(f"Dead: {subdomain}", "white") + colored(" [Status: Dead]", "blue"))
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_subdomain, subdomains)
        live_subdomains.update([res for res in results if res])

    return live_subdomains

# URL enumeration for live subdomains
def enumerate_urls(live_subdomains):
    print(colored("[INF] Performing URL enumeration on live hosts...", "yellow"))
    urls = set()
    for subdomain in live_subdomains:
        url = f"{subdomain}/robots.txt"
        urls.add(url)
        print(colored(f"[INF] Enumerating URL: {url}", "white"))
    return urls

# Argument parser for command line usage
def parse_args():
    parser = argparse.ArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('domain', help='Target domain to enumerate')
    return parser.parse_args()

# Main process
def main():
    args = parse_args()
    domain = args.domain

    # Setup logging
    logging.basicConfig(filename=f'{domain}/spider3.log', level=logging.INFO)

    # Main banner
    banner('main')
    setup(domain)

    # Subdomain Enumeration Phase
    banner('subdomain')
    subdomains = find_subdomains(domain)
    with open(f"{domain}/subdomain.txt", 'w') as f:
        f.write('\n'.join(subdomains))

    # HTTP Status Checking Phase
    banner('status')
    live_subdomains = check_live_subdomains(subdomains)
    with open(f"{domain}/livehost.txt", 'w') as f:
        f.write('\n'.join(live_subdomains))

    # URL Gathering Phase
    banner('urls')
    urls = enumerate_urls(live_subdomains)
    with open(f"{domain}/urls.txt", 'w') as f:
        f.write('\n'.join(urls))

    # Completion message
    logging.info(f"{domain} enumeration finished.")
    print(colored(f"{{{domain} enumeration finished...}}", "green"))

if __name__ == "__main__":
    main()
