#!/usr/bin/env python3

import os
import subprocess
import requests
import sys
from termcolor import colored

# Banner function using figlet for Spider3 tool name and normal text for "created by"
def banner():
    # Using subprocess to run figlet for the Spider3 tool name
    figlet_text = subprocess.run("Spider3 Enumeration Tool", shell=True, capture_output=True, text=True)
    
    # Printing the figlet text and keeping other details intact
    print(colored(figlet_text.stdout, "green"))  # Spider3 ASCII art banner
    print(colored("=======================================", "green"))
    print(colored("                create by heXliO v1.0", "red"))  # Your requested text
    print(colored("=======================================", "green"))

# Function to create necessary files and directories
def setup(domain):
    if not os.path.exists(domain):
        os.makedirs(domain)
    open(f"{domain}/subdomain.txt", 'w').close()
    open(f"{domain}/livehost.txt", 'w').close()
    open(f"{domain}/urls.txt", 'w').close()

# Function to find subdomains using subfinder
def find_subdomains(domain):
    subdomains = set()
    print(colored(f"Finding subdomains for {domain}...", "green"))
    command = f"subfinder -d {domain} -silent"  # Using subfinder as an example
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    subdomains.update(result.stdout.splitlines())
    return subdomains

# Function to check live subdomains
def check_live_subdomains(subdomains):
    live_subdomains = set()
    print(colored("Checking for live subdomains...", "green"))
    for subdomain in subdomains:
        try:
            response = requests.get(f"http://{subdomain}", timeout=3)
            if response.status_code == 200:
                live_subdomains.add(subdomain)
                print(colored(f"Live: {subdomain}", "green"))
        except requests.ConnectionError:
            print(colored(f"Dead: {subdomain}", "red"))
    return live_subdomains

# Function to perform URL enumeration
def enumerate_urls(live_subdomains):
    print(colored("Performing URL enumeration on live hosts...", "green"))
    urls = set()
    for subdomain in live_subdomains:
        urls.add(f"http://{subdomain}/robots.txt")  # Example of enumerating a common URL
    return urls

# Main process
def main():
    if len(sys.argv) != 2 or sys.argv[1].lower() != "run":
        print(colored("Usage: ./spider3.py run", "red"))
        sys.exit(1)

    banner()
    domain = input(colored("{enterTarget domain:} ", "red"))
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
    print(colored(f"{{{domain} enumeration finished...}}", "green"))

if __name__ == "__main__":
    main()
