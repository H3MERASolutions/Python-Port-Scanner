import socket
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Enable ANSI colors for Windows users
if os.name == 'nt':
    os.system('')

#region ----------Color Constants-------------------
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
ORANGE = "\033[33m"
RESET = "\033[0m"
#endregion

#region ------------Banner and UI------------
def show_banner():
    banner = f"""
{ORANGE}====================================================
{YELLOW}     ____   ___   ____  _____   ____   ____ 
    |  _ \ / _ \ |  _ \|_   _| / ___| / ___|
    | |_) | | | || |_) | | |   \___ \ \___ \\
    |  __/| |_| ||  _ <  | |    ___) | ___) |
    |_|    \___/ |_| \_\ |_|   |____/ |____/ 
                                             
          {BLUE}>> Network Port Scanner v1.0 <<{RESET}
{ORANGE}===================================================={RESET}
    """
    print(banner)

#endregion

#region -------------Port Scanner Logic--------------

def check_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "unknown"
                return port, service
    except (OSError, socket.error):
        pass
    return None

def scan_url(url, start_port=1, end_port=1024):
    # Strip URL prefixes
    clean_url = url.replace("https://", "").replace("http://", "").split('/')[0]
    
    try:
        target_ip = socket.gethostbyname(clean_url)
        print(f"\n{BLUE}[*]{RESET} Target Host: {YELLOW}{clean_url}{RESET}")
        print(f"{BLUE}[*]{RESET} IP Address:  {YELLOW}{target_ip}{RESET}")
        print(f"{BLUE}[*]{RESET} Scanning Ports: {start_port} - {end_port}\n")
    except socket.gaierror:
        print(f"{RED}[!] Error:{RESET} Could not resolve URL. Check your connection.")
        return

    ports_to_scan = range(start_port, end_port + 1)
    total = len(ports_to_scan)
    open_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(check_port, target_ip, p) for p in ports_to_scan]
        
        for i, future in enumerate(futures, 1):
            result = future.result()
            if result:
                open_ports.append(result)

            # Yellow Loading Bar
            fraction = i / total
            bar_len = 25
            arrow = int(fraction * bar_len - 1) * '=' + '>' if i < total else '=' * bar_len
            padding = ' ' * (bar_len - len(arrow))
            
            sys.stdout.write(f'\r{ORANGE}Scanning:{RESET} [{YELLOW}{arrow}{RESET}{padding}] {int(fraction*100)}% | {GREEN}Found: {len(open_ports)}{RESET}')
            sys.stdout.flush()

    print(f"\n\n{GREEN}Scan Complete!{RESET}")
    if open_ports:
        print(f"\n{'PORT':<10} {'SERVICE':<10}")
        print("-" * 25)
        for port, service in open_ports:
            print(f"{GREEN}{port:<10}{RESET} {service}")
    else:
        print(f"{RED}No open ports found.{RESET}")

#endregion

#region ---------------User interaction Part-------------------

if __name__ == "__main__":
    show_banner()
    
    # Using a try-except here allows the user to exit cleanly with Ctrl+C
    try:
        target = input(f"{BLUE}Enter Target URL (e.g., google.com): {RESET}")
        if target:
            scan_url(target)
        else:
            print(f"{RED}No target entered. Exiting.{RESET}")
    except KeyboardInterrupt:
        print(f"\n{RED}Scan halted by user.{RESET}")
        sys.exit()

#endregion