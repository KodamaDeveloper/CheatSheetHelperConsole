#!/usr/bin/env python3

"""
Plugin: Netcat Listener with Script Execution and Port Management
Description: Configures a Netcat listener with various options, executes a .sh or .py script upon receiving a connection, and manages open ports.
Author: AsheOfVoid
"""

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
import subprocess
import threading
import os
import json
import signal

console = Console()
MEMORY_FILE = 'memory.json'
listener_thread = None

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory, file, indent=4)

memory = load_memory()

def run(memory):
    global listener_thread
    print_usage_instructions()

    console.print("[bold blue]Netcat Listener Configuration[/bold blue]")

    port = IntPrompt.ask("[bold yellow]Enter the port to listen on[/bold yellow]", default=4444)
    script_type = Prompt.ask("[bold yellow]Enter the script type to execute (sh/py)[/bold yellow]", choices=["sh", "py"])

    script_dir = f"plugins/scripts/{script_type}"
    scripts = [f for f in os.listdir(script_dir) if f.endswith(f".{script_type}")]
    
    if not scripts:
        console.print(f"[bold red]No {script_type} scripts found in {script_dir} directory.[/bold red]")
        return
    
    console.print(f"[bold blue]Available {script_type.upper()} scripts:[/bold blue]")
    for i, script in enumerate(scripts, start=1):
        console.print(f"[bold cyan]{i}. {script}[/bold cyan]")
    
    script_choice = IntPrompt.ask(f"[bold yellow]Choose a script to execute by number[/bold yellow]", choices=[str(i) for i in range(1, len(scripts) + 1)])
    selected_script = scripts[script_choice - 1]
    script_path = os.path.join(script_dir, selected_script)
    
    if script_type == "sh":
        console.print(f"[bold blue]Setting execute permissions for {script_path}...[/bold blue]")
        subprocess.run(f"chmod +x {script_path}", shell=True)
    
    listener_thread = threading.Thread(target=start_nc_listener, args=(port, script_type, script_path))
    listener_thread.daemon = True
    listener_thread.start()
    
    console.print(f"[bold green]Netcat listener started on port {port}. Waiting for connections...[/bold green]")
    console.print("[bold yellow]Enter 'exit' to stop the listener, 'close' to close the port, and return to the main menu.[/bold yellow]")

    while True:
        command = Prompt.ask("[bold blue]Listener Command[/bold blue]")
        if command.lower() == "exit":
            stop_listener()
            console.print("[bold blue]Stopping the listener and exiting...[/bold blue]")
            break
        elif command.lower() == "close":
            close_port(port)
            console.print(f"[bold green]Port {port} closed.[/bold green]")
        elif command.lower() == "status":
            if listener_thread and listener_thread.is_alive():
                console.print(f"[bold green]Listener is running on port {port}.[/bold green]")
            else:
                console.print(f"[bold red]Listener is not running.[/bold red]")

def start_nc_listener(port, script_type, script_path):
    while True:
        nc_command = f"nc -lvp {port}"
        console.print(f"[bold blue]Running: {nc_command}[/bold blue]")
        result = subprocess.run(nc_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[bold green]Received connection on port {port}[/bold green]")
            console.print(f"[bold blue]Executing {script_path}...[/bold blue]")
            if script_type == "sh":
                script_result = subprocess.run(script_path, shell=True, capture_output=True, text=True)
            else:
                script_result = subprocess.run(f"python3 {script_path}", shell=True, capture_output=True, text=True)
            
            if script_result.returncode == 0:
                console.print(f"[bold green]Script output: {script_result.stdout}[/bold green]")
            else:
                console.print(f"[bold red]Script error: {script_result.stderr}[/bold red]")
        else:
            console.print(f"[bold red]Error with Netcat listener: {result.stderr}[/bold red]")

def close_port(port):
    # Find the process using the port and kill it
    find_command = f"lsof -i :{port} -t"
    result = subprocess.run(find_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        pid = result.stdout.strip()
        kill_command = f"kill -9 {pid}"
        subprocess.run(kill_command, shell=True)
        save_port_info(port, pid)
    else:
        console.print(f"[bold red]No process found using port {port}[/bold red]")

def save_port_info(port, pid):
    if "port_info" not in memory:
        memory["port_info"] = {}
    memory["port_info"][str(port)] = {
        "pid": pid,
        "status": "closed"
    }
    save_memory(memory)

def stop_listener():
    global listener_thread
    if listener_thread and listener_thread.is_alive():
        listener_thread = None

def print_usage_instructions():
    console.print(Panel("""
[bold blue]Netcat Listener with Script Execution and Port Management Plugin[/bold blue]

This plugin configures a Netcat listener with various options, executes a .sh or .py script upon receiving a connection, and manages open ports.

[bold yellow]How to use:[/bold yellow]
1. Enter the port you want the Netcat listener to listen on (default: 4444).
2. Select the script type you want to execute (sh or py).
3. Choose a script from the list of available scripts in the selected directory.
4. The listener will start and wait for connections.
5. When a connection is received, the selected script will be executed.
6. You can enter 'exit' at any time to stop the listener and return to the main menu.
7. You can enter 'close' to close the port being used by the listener.
8. Enter 'status' to check if the listener is running.

[bold yellow]Example:[/bold yellow]
1. Enter the port to listen on: [green]4444[/green]
2. Enter the script type to execute (sh/py): [green]sh[/green]
3. Choose a script to execute by number: [green]1[/green]
4. Netcat listener started on port 4444. Waiting for connections...
5. Enter 'exit' to stop the listener and return to the main menu.
6. Enter 'close' to close the port being used by the listener.
7. Enter 'status' to check if the listener is running.

[bold yellow]Note:[/bold yellow] The plugin will continuously listen for connections and execute the selected script each time a connection is received. It also allows you to manage and close open ports.
""", title="Netcat Listener with Script Execution and Port Management"))

if __name__ == "__main__":
    memory = {
        'target_ip': '127.0.0.1',
        'vpn_ip': '10.10.16.32',
        'os': 'Linux',
        'domain': 'None'
    }
    run(memory)
