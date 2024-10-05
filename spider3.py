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
    figlet_banner_spider = pyfiglet.figlet_format("Spider3", font="slant")
    figlet_banner_enum = pyfiglet.figlet_format("Enumeration", font="slant")

    # Show Spider3 in red and Enumeration in white
    print(colored(figlet_banner_spider, "red") + colored(figlet_banner_enum, "white"))
    print(colored(f"                {CREATOR}", "blue"))

    # Display version with proper colors for "latest" and other versions
    if "latest" in VERSION:
        print(colored(f"Current Spider3 Enumeration version {VERSION}", "green"))
    else:
        print(colored(f"Current Spider3 Enumeration version {VERSION}", "red"))

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Spider3 Enumeration Tool')
    parser.add_argument('command', nargs='?', default=None, help='Command to run the tool (run)')
    args = parser.parse_args()

    # Show banner and version when no 'run' command is provided
    if args.command is None:
        banner()
        sys.exit(0)

    # If command is 'run', proceed with domain input and enumeration
    if args.command == 'run':
        banner()
        domain = input(colored("Enter Target Domain: ", "red", attrs=['bold'])).strip()

        # Ensure we start with a blank line after domain input
        print()

        setup(domain)
        subdomains = find_subdomains(domain)
        live_subdomains = check_live_subdomains(subdomains)
        urls = enumerate_urls(live_subdomains)

        # Final summary
        print()
        print(colored(f"Spider3 done: {len(subdomains)} subdomains ({len(live_subdomains)} live hosts) {len(urls)} URLs scanned in {time.time():.2f} seconds", "magenta", attrs=['bold']))

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
    print(colored(f"Enumerating subdomains for {domain}...", "yellow"))
    command = f"subfinder -d {domain} -silent"
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        subdomain_list = result.stdout.splitlines()

        # Display each subdomain directly
        for subdomain in subdomain_list:
            subdomains.add(subdomain)
            print(colored(subdomain, "white"))

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
    print(colored("\nChecking for live subdomains...", "yellow", attrs=['bold']))

    def check_subdomain(subdomain):
        protocols = ['http', 'https']
        for protocol in protocols:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(url, timeout=3)
                status = response.status_code
                if status == 200:
                    print(colored(f"{url} [Status: {status} OK]", "green"))
                    return url
                elif status == 403:
                    print(colored(f"{url} [Status: {status} Forbidden]", "red"))
                    return None
                else:
                    print(colored(f"{url} [Status: {status}]", "blue"))
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
    urls_found = []
    for subdomain in live_subdomains:
        for url_suffix in urls_to_check:
            url = f"{subdomain}{url_suffix}"
            try:
                response = requests.get(url, timeout=3)
                status = response.status_code
                if status == 200:
                    print(colored(f"Enumerating URL: {url} [Found]", "green"))
                    urls_found.append(url)
                else:
                    print(colored(f"Trying URL: {url}", "blue"))
            except (requests.ConnectionError, requests.Timeout):
                pass

    return urls_found

if __name__ == "__main__":
    main()
