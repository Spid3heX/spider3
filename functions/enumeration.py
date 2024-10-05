import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import time
from functions.utils import save_data

def find_subdomains(domain):
    subdomains = set()
    print(colored(f"Enumerating subdomains for {colored(domain, 'white')}...", "yellow", attrs=['bold']))
    command = f"subfinder -d {domain} -silent"
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        subdomain_list = result.stdout.splitlines()
        for subdomain in subdomain_list:
            subdomains.add(subdomain)
            print(colored(f"{subdomain}", "white"))
        
        elapsed_time = time.time() - start_time
        print(colored(f"Found {len(subdomain_list)} subdomains for {colored(domain, 'white')} in {elapsed_time:.2f} seconds", "yellow"))
        
        save_data("subdomains", domain, subdomains)

    except subprocess.CalledProcessError as e:
        print(colored(f"Error running subfinder: {e}", "red"))
    except FileNotFoundError:
        print(colored("subfinder is not installed or not in PATH", "red", attrs=['bold']))
    return subdomains

def check_live_subdomains(subdomains, domain):
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
    
    save_data("livehosts", domain, live_subdomains)

    return live_subdomains

def enumerate_urls(live_subdomains, domain):
    urls_to_check = [
        "/robots.txt", "/sitemap.xml", "/wp-admin.php", "/admin.php", "/login.php", "/config.php", "/wp-config.php", 
        "/server-status", "/admin", "/administrator", "/phpinfo.php", "/backup.zip", "/debug.php", "/test.php", 
        "/upload.php", "/hidden/", "/private/", "/portal/", "/secret/", "/backup/", "/old/", "/dev/", "/beta/", 
        "/staging/", "/error.log", "/forgot_password.php", "/shell.php", "/uploads/", "/console/"
    ]
    
    print(colored("\nPerforming URL enumeration on live hosts...", "cyan", attrs=['bold']))
    found_urls = set()
    for subdomain in live_subdomains:
        for url_suffix in urls_to_check:
            url = f"{subdomain}{url_suffix}"
            try:
                response = requests.get(url, timeout=3)
                status = response.status_code
                status_text = requests.status_codes._codes[status][0].replace('_', ' ').capitalize()

                if status == 200:
                    print(colored(f"[INF] Enumerating URL: {url}", "white"))
                    print(colored(f"Trying URL: {url} [Found]", "green"))
                    found_urls.add(url)
                else:
                    print(colored(f"Trying URL: {url} [Status: {status} {status_text}]", "red"))

            except (requests.ConnectionError, requests.Timeout):
                pass

    save_data("urls", domain, found_urls)
