# plugins/show_important_info.py

import os
import json
import re
from rich.console import Console
from rich.table import Table

console = Console()

def run(memory):
    # Check if memory has the required keys
    required_keys = ["target_ip", "domain", "os", "commands"]
    for key in required_keys:
        if key not in memory:
            console.print(f"[bold red]Error: {key} not found in memory.[/bold red]")
            return

    # Display target information
    console.print(f"[bold blue]Target Info[/bold blue]")
    console.print(f"IP Address: [bold yellow]{memory['target_ip']}[/bold yellow]")
    console.print(f"Domain: [bold yellow]{memory['domain']}[/bold yellow]")
    console.print(f"Operating System: [bold yellow]{memory['os']}[/bold yellow]")

    # Display command outputs
    console.print(f"[bold blue]Executed Commands[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command")
    table.add_column("Output")
    table.add_column("Error")

    for command_info in memory["commands"]:
        table.add_row(command_info["command"], command_info["output"], command_info["error"])

    console.print(table)

    # Extract and display important information
    console.print(f"[bold blue]Important Information Extracted[/bold blue]")

    ip_addresses = set()
    open_ports = set()
    port_info = {}
    vulnerabilities = set()
    services = {}
    subdomains = memory.get("subdomains", [])
    paths = memory.get("paths", [])

    for command_info in memory["commands"]:
        output = command_info["output"]
        if output:
            # Extract IP addresses
            ip_matches = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', output)
            ip_addresses.update(ip_matches)

            # Extract open ports and their states and services
            port_matches = re.findall(r'(\d{1,5})/tcp\s+(\w+)\s+(\w+)', output)
            for port, state, service in port_matches:
                open_ports.add(port)
                port_info[port] = (state, service)

            # Extract services running on open ports
            service_matches = re.findall(r'(\d{1,5})/tcp\s+open\s+(\w+)', output)
            for port, service in service_matches:
                services[port] = service

            # Extract potential vulnerabilities (dummy pattern for illustration)
            vuln_matches = re.findall(r'(CVE-\d{4}-\d{4,7})', output)
            vulnerabilities.update(vuln_matches)

    # Display extracted information
    if ip_addresses:
        console.print(f"IP Addresses found: [bold yellow]{', '.join(ip_addresses)}[/bold yellow]")
    else:
        console.print("[bold red]No IP Addresses found.[/bold red]")

    if open_ports:
        console.print(f"Open Ports: [bold yellow]{', '.join(open_ports)}[/bold yellow]")
        port_table = Table(show_header=True, header_style="bold magenta")
        port_table.add_column("Port")
        port_table.add_column("State")
        port_table.add_column("Service")
        for port, (state, service) in port_info.items():
            port_table.add_row(port, state, service)
        console.print(port_table)
    else:
        console.print("[bold red]No Open Ports found.[/bold red]")

    if services:
        console.print(f"Services Running on Open Ports: [bold yellow]{', '.join(services.values())}[/bold yellow]")
        service_table = Table(show_header=True, header_style="bold magenta")
        service_table.add_column("Port")
        service_table.add_column("Service")
        for port, service in services.items():
            service_table.add_row(port, service)
        console.print(service_table)
    else:
        console.print("[bold red]No Services found running on open ports.[/bold red]")

    if vulnerabilities:
        console.print(f"Vulnerabilities: [bold yellow]{', '.join(vulnerabilities)}[/bold yellow]")
    else:
        console.print("[bold red]No Vulnerabilities found.[/bold red]")

    if subdomains:
        console.print(f"Subdomains found: [bold yellow]{', '.join(subdomains)}[/bold yellow]")
    else:
        console.print("[bold red]No Subdomains found.[/bold red]")

    if paths:
        console.print(f"Paths found: [bold yellow]{', '.join(paths)}[/bold yellow]")
    else:
        console.print("[bold red]No Paths found.[/bold red]")

if __name__ == "__main__":
    data_dir = 'data'
    session_name = 'ghost'
    memory_file = os.path.join(data_dir, f'{session_name}_memory.json')

    if os.path.exists(memory_file):
        with open(memory_file, 'r') as file:
            memory = json.load(file)
        run(memory)
    else:
        console.print("[bold red]Session memory file not found.[/bold red]")
