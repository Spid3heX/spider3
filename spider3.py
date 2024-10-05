#!/usr/bin/env python3

import sys
import os
from termcolor import colored
from functions.banner import banner
from functions.utils import setup
from functions.enumeration import find_subdomains, check_live_subdomains, enumerate_urls

# Add the functions directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'functions')))

def main():
    if len(sys.argv) < 2 or sys.argv[1] != 'run':
        print(colored("[ERR] Invalid command!", "red"))
        print(colored("Usage: ./spider3.py run", "yellow"))
        sys.exit(1)

    banner()  # Display banner before starting
    domain = input(colored("Enter Target Domain: ", "red", attrs=['bold']))
    setup(domain)
    
    print()
    subdomains = find_subdomains(domain)
    
    print()
    live_subdomains = check_live_subdomains(subdomains, domain)
    
    print()
    enumerate_urls(live_subdomains, domain)
    
    print()
    print(colored(f"Enumeration process for {domain} completed.", "yellow", attrs=['bold']))
    print(colored(f"{len(subdomains)} subdomain(s), {len(live_subdomains)} live host(s), {0} URL(s) scanned.", "cyan", attrs=['bold']))

if __name__ == "__main__":
    main()
