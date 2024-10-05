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
TOOL_NAME = "Spider3 Enumeration"

# Figlet banner function
def banner():
    # Single-line banner as per request
    figlet_banner = pyfiglet.figlet_format("Spider3 Enumeration", font="slant")
    # Show the banner with the appropriate colors
    print(colored(figlet_banner.strip(), "red"))
    print(colored(f"                {CREATOR}", "blue"))

    # Check version status and display it in the appropriate color
    if "latest" in VERSION:
        print(colored(f"Current Spider3 Enumeration version {VERSION}", "green"))
    else:
        print(colored(f"Current Spider3 Enumeration version {VERSION}", "red"))

# Custom argument parser to handle errors
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Custom error message in red
        sys.stderr.write(colored(f"Error: {message}\n", "red"))
        self.print_usage()  # Show usage information
        sys.exit(1)  # Exit after showing error

# Argument parser for command line usage
def parse_args():
    # Using custom parser
    parser = CustomArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('command', help='Command to run the tool (run)')

    # Handling missing arguments
    if len(sys.argv) < 2:
        print(colored("Error: the following arguments are required: command", "red"))
        print(colored("Usage: ./spider3.py run", "yellow"))
        sys.exit(1)  # Exit the program if no command is provided
        
    return parser.parse_args()

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
    print(colored(f"Enumerating subdomains for {domain}...", "white"))
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
        print(colored(f"Found {len(subdomain_list)} subdomains for {domain} in {elapsed_time:.2f} seconds", "yellow"))

    except subprocess.CalledProcessError as e:
        print(colored(f"Error running subfinder: {e}", "red"))
    except FileNotFoundError:
        print(colored("subfinder is not installed or not in PATH", "red"))
    return subdomains

# Check live subdomains with concurrent requests
def check_live_subdomains(subdomains):
    live_subdomains = set()
    print(colored("\nChecking for live subdomains...", "magenta"))

    def check_subdomain(subdomain):
        protocols = ['http', 'https']
        for protocol in protocols:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(url, timeout=3)
                status = response.status_code
                status_text = requests.status_codes._codes[status][0].replace('_', ' ').capitalize()

                if status == 200:
                    print(colored(f"{url} [Status: {status} {status_text}]", "green"))
                    return url
                else:
                    print(colored(f"{url} [Status: {status} {status_text}]", "yellow"))
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

    print(colored("\nPerforming URL enumeration on live hosts...", "cyan", attrs=['bold']))
    for subdomain in live_subdomains:
        for url_suffix in urls_to_check:
            url = f"{subdomain}{url_suffix}"
            try:
                response = requests.get(url, timeout=3)
                status = response.status_code
                status_text = requests.status_codes._codes[status][0].replace('_', ' ').capitalize()

                if status == 200:
                    print(colored(f"Enumerating URL: {url} [Found]", "green"))
                else:
                    print(colored(f"Trying URL: {url} [Status: {status} {status_text}]", "yellow"))
            except (requests.ConnectionError, requests.Timeout):
                pass

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
