import os
from rich.console import Console
from rich.prompt import Prompt, IntPrompt

console = Console()
hosts_file_path = "/etc/hosts"

def load_hosts_file():
    with open(hosts_file_path, 'r') as file:
        return file.readlines()

def save_hosts_file(lines):
    with open(hosts_file_path, 'w') as file:
        file.writelines(lines)

def display_hosts():
    console.print("[bold blue]Current /etc/hosts content:[/bold blue]")
    lines = load_hosts_file()
    for i, line in enumerate(lines):
        console.print(f"{i+1}. {line.strip()}")

def add_subdomain():
    domain = Prompt.ask("[bold yellow]Enter the domain name[/bold yellow]")
    subdomain = Prompt.ask("[bold yellow]Enter the subdomain name[/bold yellow]")
    ip_address = Prompt.ask("[bold yellow]Enter the IP address for the subdomain[/bold yellow]")

    lines = load_hosts_file()
    lines.append(f"{ip_address} {subdomain}.{domain}\n")
    save_hosts_file(lines)
    console.print(f"[bold green]Subdomain {subdomain}.{domain} added with IP {ip_address}[/bold green]")

def add_domain():
    domain = Prompt.ask("[bold yellow]Enter the domain name[/bold yellow]")
    ip_address = Prompt.ask("[bold yellow]Enter the IP address for the domain[/bold yellow]")

    lines = load_hosts_file()
    lines.append(f"{ip_address} {domain}\n")
    save_hosts_file(lines)
    console.print(f"[bold green]Domain {domain} added with IP {ip_address}[/bold green]")

def clean_errors():
    lines = load_hosts_file()
    clean_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    save_hosts_file(clean_lines)
    console.print("[bold green]Errors cleaned from /etc/hosts file[/bold green]")

def edit_host():
    lines = load_hosts_file()
    display_hosts()
    choice = IntPrompt.ask("[bold blue]Choose a host entry to edit by number[/bold blue]", choices=[str(i) for i in range(1, len(lines) + 1)])
    index = choice - 1
    current_ip, current_host = lines[index].strip().split(maxsplit=1)
    
    new_ip = Prompt.ask(f"[bold yellow]Enter new IP address for {current_host}[/bold yellow]", default=current_ip)
    new_host = Prompt.ask(f"[bold yellow]Enter new host name for IP {current_ip}[/bold yellow]", default=current_host)
    
    lines[index] = f"{new_ip} {new_host}\n"
    save_hosts_file(lines)
    console.print(f"[bold green]Host entry updated to {new_ip} {new_host}[/bold green]")

def delete_host():
    lines = load_hosts_file()
    display_hosts()
    choice = IntPrompt.ask("[bold blue]Choose a host entry to delete by number[/bold blue]", choices=[str(i) for i in range(1, len(lines) + 1)])
    index = choice - 1

    del lines[index]
    save_hosts_file(lines)
    console.print("[bold green]Host entry deleted[/bold green]")

def run(memory):
    console.print("[bold blue]Hosts File Manager[/bold blue]")
    while True:
        console.print("[bold yellow]1. Display /etc/hosts[/bold yellow]")
        console.print("[bold yellow]2. Add a subdomain[/bold yellow]")
        console.print("[bold yellow]3. Add a domain[/bold yellow]")
        console.print("[bold yellow]4. Clean errors from /etc/hosts[/bold yellow]")
        console.print("[bold yellow]5. Edit a host entry[/bold yellow]")
        console.print("[bold yellow]6. Delete a host entry[/bold yellow]")
        console.print("[bold yellow]0. Exit[/bold yellow]")

        choice = Prompt.ask("[bold blue]Choose an option[/bold blue]", choices=["1", "2", "3", "4", "5", "6", "0"])

        if choice == "1":
            display_hosts()
        elif choice == "2":
            add_subdomain()
        elif choice == "3":
            add_domain()
        elif choice == "4":
            clean_errors()
        elif choice == "5":
            edit_host()
        elif choice == "6":
            delete_host()
        elif choice == "0":
            break
        else:
            console.print("[bold red]Invalid option, please try again.[/bold red]")

if __name__ == "__main__":
    run({})
