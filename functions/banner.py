import pyfiglet
from termcolor import colored

VERSION = "v1.6.0 (latest)"
CREATOR = "create by heXliO"

def banner():
    figlet_banner = pyfiglet.figlet_format("Spider3Running", font="slant")
    print(colored(figlet_banner, "white", attrs=['bold']))
    print(colored(f"                               {CREATOR}", "blue", attrs=['bold']))
    
    if "latest" in VERSION:
        print(colored(f"Current Spider3 Enumeration tool version {VERSION}", "green"))
    else:
        print(colored(f"Current Spider3 Enumeration tool version {VERSION}", "red"))

