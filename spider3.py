#!/usr/bin/env python3

import os
import sys
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
TOOL_NAME = "Spider3Running"

# Figlet banner function
def banner():
    figlet_banner = pyfiglet.figlet_format("Spider3Running", font="slant")
    print(colored(figlet_banner, "red", attrs=['bold']))
    print(colored(f"                          {CREATOR}", "blue"))
    
    # Set version color based on status
    if "latest" in VERSION:
        print(colored(f"Current Spider3 Enumeration tool version {VERSION}", "green"))
    else:
        print(colored(f"Current Spider3 Enumeration tool version {VERSION}", "red"))

def main():
    if len(sys.argv) < 2 or sys.argv[1] != 'run':
        print(colored("[ERR] Invalid command!", "red"))
        print(colored("Usage: ./spider3.py run", "yellow"))
        sys.exit(1)

    banner()  # Display banner before starting
    domain = input(colored("Enter Target Domain: ", "red", attrs=['bold']))
    setup(domain)

    # Blank line before starting tasks
    print()
    subdomains = find_subdomains(domain)
    
    # Blank line after finding subdomains
    print()
    live_subdomains = check_live_subdomains(subdomains)
    
    # Blank line after checking live subdomains
    print()
    enumerate_urls(live_subdomains)
    
    # Blank line before final result summary
    print()
    
    # Final summary
    print(colored(f"Enumeration process for {domain} completed.", "yellow", attrs=['bold']))
    print(colored(f"{len(subdomains)} subdomain(s), {len(live_subdomains)} live host(s), {0} URL(s) scanned.", "cyan", attrs=['bold']))

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
    print(colored(f"Enumerating subdomains for {colored(domain, 'white')}...", "yellow", attrs=['bold']))
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
        print(colored(f"Found {len(subdomain_list)} subdomains for {colored(domain, 'white')} in {elapsed_time:.2f} seconds", "yellow"))
        
    except subprocess.CalledProcessError as e:
        print(colored(f"Error running subfinder: {e}", "red"))
    except FileNotFoundError:
        print(colored("subfinder is not installed or not in PATH", "red", attrs=['bold']))
    return subdomains

# Check live subdomains with concurrent requests
def check_live_subdomains(subdomains):
    live_subdomains = set()
    print(colored("\nChecking for live subdomains...", "magenta", attrs=['bold']))

    def check_subdomain(subdomain):
        protocols = ['http', 'https']
        for protocol in protocols:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(url, timeout=3)
                status = response.status_code
                status_text = requests.status_codes._codes[status][0].replace('_', ' ').capitalize()

                # Color the subdomain and status accordingly
                subdomain_colored = colored(f"{url}", "white")
                if status == 200:
                    status_colored = colored(f"[Status: {status} {status_text}]", "green")
                else:
                    status_colored = colored(f"[Status: {status} {status_text}]", "red")

                print(f"{subdomain_colored} {status_colored}")
                return url if status == 200 else None

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
        "/console/", "/config/"
    ]
    
    print(colored("\nPerforming URL enumeration on live hosts...", "cyan", attrs=['bold']))
    for subdomain in live_subdomains:
        for url_suffix in urls_to_check:
            url = f"{subdomain}{url_suffix}"
            try:
                response = requests.get(url, timeout=3)
                status = response.status_code
                status_text = requests.status_codes._codes[status][0].replace('_', ' ').capitalize()

                # Display the status in color
                if status == 200:
                    print(colored(f"[INF] Enumerating URL: {url}", "white"))
                    print(colored(f"Trying URL: {url} [Found]", "green"))
                else:
                    print(colored(f"Trying URL: {url} [Status: {status} {status_text}]", "red"))

            except (requests.ConnectionError, requests.Timeout):
                pass

# Argument parser for command line usage
def parse_args():
    parser = argparse.ArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('command', help='Command to run the tool (run)')
    return parser.parse_args()

# Main process
if __name__ == "__main__":
    main()
