#!/usr/bin/env python3

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
VERSION = "v1.6.0 (latest)"
CREATOR = "create by heXliO"
TOOL_NAME = "Spider3 Enumeration"

# Figlet banner function
def banner():
    figlet_banner = pyfiglet.figlet_format(TOOL_NAME)
    print(colored(figlet_banner, "blue"))
    print(colored(f"                {CREATOR}", "yellow"))
    print(colored(f"[INF] Current {TOOL_NAME} version {VERSION}", "yellow"))

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
    command = f"subfinder -d {domain} -silent"
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
                if response.status_code in [200, 403, 404]:
                    color = "green" if response.status_code == 200 else "blue"
                    print(colored(f"Live: {url}", "white") + colored(f" [Status: {response.status_code}]", color))
                    if response.status_code == 200:
                        return url
            except (requests.ConnectionError, requests.Timeout):
                pass
        print(colored(f"Dead: {subdomain}", "white") + colored(" [Status: Dead]", "red"))
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_subdomain, subdomains)
        live_subdomains.update([res for res in results if res])

    return live_subdomains

# URL enumeration for live subdomains
def enumerate_urls(live_subdomains):
    print(colored("[INF] Performing URL enumeration on live hosts...", "yellow"))
    urls = set()
    common_paths = ["robots.txt", "security.txt", "wp-admin", "xmlrpc.php"]

    for subdomain in live_subdomains:
        for path in common_paths:
            url = f"{subdomain}/{path}"
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    urls.add(url)
                    print(colored(f"[INF] Enumerating URL: {url}", "green"))
                else:
                    print(colored(f"[INF] Trying URL: {url} [Status: {response.status_code}]", "yellow"))
            except (requests.ConnectionError, requests.Timeout):
                print(colored(f"[INF] Failed to reach URL: {url}", "red"))

    return urls

# Argument parser for command line usage
def parse_args():
    parser = argparse.ArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('command', help='Command to run the tool (use "run")')
    return parser.parse_args()

# Main process
def main():
    args = parse_args()
    
    if args.command.lower() != 'run':
        print(colored("Error: Invalid command. Use './spider3.py run' to execute.", "red"))
        return

    # Display banner and version information
    banner()

    # Get the target domain from the user
    domain = input(colored("Enter Target Domain: ", "white"))

    # Setup environment (create files and directories)
    setup(domain)

    # Finding subdomains
    subdomains = find_subdomains(domain)
    with open(f"{domain}/subdomain.txt", 'w') as f:
        f.write('\n'.join(subdomains))

    # Checking for live subdomains
    live_subdomains = check_live_subdomains(subdomains)
    with open(f"{domain}/livehost.txt", 'w') as f:
        f.write('\n'.join(live_subdomains))

    # URL enumeration
    urls = enumerate_urls(live_subdomains)
    with open(f"{domain}/urls.txt", 'w') as f:
        f.write('\n'.join(urls))

    # Completion message
    print(colored(f"Enumeration process for {domain} completed.", "green"))

if __name__ == "__main__":
    main()
