import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def list_sessions():
    console.print("[bold green]Current Sessions:[/bold green]")
    subprocess.run(['who'], check=True)

def check_network_connections():
    console.print("[bold green]Active Network Connections:[/bold green]")
    subprocess.run(['netstat', '-tunlp'], check=True)

def identify_processes_with_open_connections():
    console.print("[bold green]Processes with Open Network Connections:[/bold green]")
    subprocess.run(['lsof', '-i'], check=True)

def check_suspicious_processes():
    console.print("[bold green]Suspicious Processes:[/bold green]")
    suspicious_processes = ["nc", "netcat", "ncat", "bash", "sh", "python", "perl", "php"]
    for process in suspicious_processes:
        console.print(f"Checking for {process} processes...")
        result = subprocess.run(['pgrep', '-l', process], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"No {process} processes found.")

def check_unusual_logins():
    console.print("[bold green]Unusual Login Attempts:[/bold green]")
    # Since 'lastb' is not available, let's use 'journalctl' as an alternative
    subprocess.run(['journalctl', '_COMM=sshd', '--since', 'yesterday'], check=True)

def run(memory):
    console.print("[bold blue]Antivirus Plugin for Kali Linux[/bold blue]")

    while True:
        console.print("\n[bold yellow]Choose an option:[/bold yellow]")
        console.print("1. List current sessions")
        console.print("2. Check active network connections")
        console.print("3. Identify processes with open network connections")
        console.print("4. Check for suspicious processes")
        console.print("5. Check unusual login attempts")
        console.print("0. Exit")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "0"])

        if choice == "1":
            list_sessions()
        elif choice == "2":
            check_network_connections()
        elif choice == "3":
            identify_processes_with_open_connections()
        elif choice == "4":
            check_suspicious_processes()
        elif choice == "5":
            check_unusual_logins()
        elif choice == "0":
            console.print("[bold blue]Exiting Antivirus Plugin...[/bold blue]")
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")

if __name__ == "__main__":
    run({})
