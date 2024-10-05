# Spider3 Enumeration Tool

![spider3Logo](https://github.com/user-attachments/assets/7f392565-5b08-4c66-9649-33085dae8600)

Spider3 is an enumeration and penetration testing tool designed to help you find subdomains of a target domain, check which subdomains are live, and perform URL enumeration on live hosts. The tool saves results in structured files within a folder corresponding to the target domain.

## Features
- Automatically creates a folder with the domain name.
- Finds subdomains and saves them in `subdomain.txt`.
- Checks for live subdomains and saves them in `livehost.txt`.
- Performs URL enumeration on live subdomains and saves the results in `urls.txt`.
- Simple and easy-to-use with just one command.


## Installation & Usage Guide for Spider3
- Clone the Spider3 repository: To install the tool, simply clone the repository from GitHub:
 `git clone https://github.com/Spid3heX/spider3.git`
 `cd spider3`
 `chmod +x spider3.py`
- Running the Tool: To start the enumeration process, make sure to run the command with the argument run. For example:
  `./spider3.py run`
  ## Usage Note
- To fix any shebang issues on Linux:
  Install dos2unix using sudo `apt install dos2unix`, then convert the script with `dos2unix spider3.py` to remove Windows-style line endings. After that, run the tool with   `./spider3.py run`.

