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
    figlet_banner_spider = pyfiglet.figlet_format("Spider3", font="slant")
    figlet_banner_enum = pyfiglet.figlet_format("Enumeration", font="slant")

    # Show Spider3 in red and Enumeration in white
    print(colored(figlet_banner_spider, "red") + colored(figlet_banner_enum, "white"))
    print(colored(f"                {CREATOR}", "blue"))
    print(colored(f"[INF] Current Spider3 Enumeration version {VERSION}", "yellow"))

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
        
        # Display each subdomain directly
        for subdomain in subdomain_list:
            subdomains.add(subdomain)
            print(colored(f"{subdomain}", "white"))
        
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
    print(colored("\n[INF] Checking for live subdomains...", "yellow"))

    def check_subdomain(subdomain):
        protocols = ['http', 'https']
        for protocol in protocols:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(url, timeout=3)
                status = response.status_code
                if status == 200:
                    print(colored(f"Live: {url} ", "white") + colored("[Status: 200]", "green"))
                    return url
                else:
                    print(colored(f"Dead: {subdomain} ", "white") + colored(f"[Status: {status}]", "blue"))
            except (requests.ConnectionError, requests.Timeout):
                pass
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_subdomain, subdomains)
        live_subdomains.update([res for res in results if res])

    return live_subdomains

# URL enumeration for live subdomains
def enumerate_urls(live_subdomains):
    urls_to_check = [
        "/robots.txt", "/sitemap.xml", "/wp-admin.php", "/admin.php", "/login.php", "/config.php", 
        "/wp-config.php", "/server-status", "/admin", "/administrator", "/admin/login", "/user/login", 
        "/phpinfo.php", "/backup.zip", "/debug.php", "/test.php", "/api", "/upload.php", "/hidden/",
        "/private/", "/restricted/", "/portal/", "/internal/", "/secret/", "/backup/", "/old/", "/dev/",
        "/beta/", "/staging/", "/tmp/", "/logs/", "/error.log", "/errors.log", "/access.log", "/adminpanel/",
        "/manage/", "/control/", "/dashboard/", "/cgi-bin/", "/uploads/", "/forgot_password.php", 
        "/signup.php", "/old-admin/", "/api-docs/", "/webmail/", "/mailadmin/", "/shell.php", "/dbadmin/",
        "/console/", "/config/."
    ]
    
    print(colored("\n[INF] Performing URL enumeration on live hosts...", "yellow"))
    for subdomain in live_subdomains:
        for url_suffix in urls_to_check:
            url = f"{subdomain}{url_suffix}"
            try:
                response = requests.get(url, timeout=3)
                status = response.status_code
                if status == 200:
                    print(colored(f"[INF] Enumerating URL: {url}", "white"))
                    print(colored(f"[INF] Trying URL: {url} [Found]", "green"))
                else:
                    print(colored(f"[INF] Trying URL: {url}", "blue"))
            except (requests.ConnectionError, requests.Timeout):
                pass

# Argument parser for command line usage
def parse_args():
    parser = argparse.ArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('command', help='Command to run the tool (run)')
    return parser.parse_args()

# Main process
def main():
    args = parse_args()
    if args.command != 'run':
        print(colored("Error: Invalid command. Usage: ./spider3.py run", "red"))
        return
    
    banner()
    domain = input(colored("Enter Target Domain: ", "red", attrs=['bold']))
    setup(domain)

    # Enumerating subdomains
    subdomains = find_subdomains(domain)
    with open(f"{domain}/subdomain.txt", 'w') as f:
        f.write('\n'.join(subdomains))

    # Checking for live subdomains
    live_subdomains = check_live_subdomains(subdomains)
    with open(f"{domain}/livehost.txt", 'w') as f:
        f.write('\n'.join(live_subdomains))

    # URL enumeration
    enumerate_urls(live_subdomains)
    print(colored(f"Enumeration process for {domain} completed.", "green"))

if __name__ == "__main__":
    main()
