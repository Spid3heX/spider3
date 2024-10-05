import os
from termcolor import colored

def setup(domain):
    if not os.path.exists(domain):
        os.makedirs(domain)
    open(f"{domain}/subdomain.txt", 'w').close()
    open(f"{domain}/livehost.txt", 'w').close()
    open(f"{domain}/urls.txt", 'w').close()

def save_data(data_type, domain, data):
    file_map = {
        "subdomains": f"{domain}/subdomain.txt",
        "livehosts": f"{domain}/livehost.txt",
        "urls": f"{domain}/urls.txt"
    }
    if data_type in file_map:
        with open(file_map[data_type], 'a') as file:
            for item in data:
                file.write(f"{item}\n")
    else:
        print(colored("[ERR] Invalid data type for saving.", "red"))

