#!/usr/bin/env python3

"""
Plugin: Execute Scripts in Loop
Description: Allows selecting and executing a script from the 'py' or 'sh' directory in a loop for a specified number of times, setting execution permissions if necessary.
Author: AsheOfVoid
"""

import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
import time

console = Console()

def print_usage_instructions():
    console.print(Panel("""
[bold blue]Execute Scripts in Loop Plugin[/bold blue]

This plugin allows you to select and execute a script from the 'py' or 'sh' directory in a loop for a specified number of times. It sets execution permissions for shell scripts if necessary.

[bold yellow]How to use:[/bold yellow]
1. Choose the type of script to execute (Shell Script or Python Script).
2. Select a script from the list of available scripts in the chosen directory.
3. Enter the number of times you want to execute the script.
4. Enter the time to wait between each execution (in seconds).
5. The plugin will execute the selected script the specified number of times and display the output.

[bold yellow]Example:[/bold yellow]
1. Choose script type to execute: [green]1 (Shell Script)[/green]
2. Choose a script to execute by number: [green]1[/green]
3. Enter the number of times to execute the script: [green]3[/green]
4. Enter time to wait between each execution (in seconds): [green]5[/green]

[bold yellow]Notes:[/bold yellow]
- The plugin will automatically set execute permissions for shell scripts.
- The output and errors for each execution will be displayed.
""", title="Execute Scripts in Loop Plugin"))

def run(memory):
    print_usage_instructions()

    script_dir = "plugins/scripts"
    script_types = {"1": "sh", "2": "py"}
    
    console.print("[bold blue]Choose script type to execute:[/bold blue]")
    console.print("[bold cyan]1. Shell Script (.sh)[/bold cyan]")
    console.print("[bold cyan]2. Python Script (.py)[/bold cyan]")
    
    script_type_choice = Prompt.ask("[bold yellow]Enter choice (1/2)[/bold yellow]", choices=["1", "2"])
    script_type = script_types[script_type_choice]
    
    scripts = [f for f in os.listdir(os.path.join(script_dir, script_type)) if f.endswith(f".{script_type}")]
    
    if not scripts:
        console.print(f"[bold red]No {script_type} scripts found in {script_dir}/{script_type} directory.[/bold red]")
        return
    
    console.print("[bold blue]Available scripts:[/bold blue]")
    for i, script in enumerate(scripts, start=1):
        console.print(f"[bold cyan]{i}. {script}[/bold cyan]")
    
    script_choice = IntPrompt.ask("[bold yellow]Choose a script to execute by number[/bold yellow]", choices=[str(i) for i in range(1, len(scripts) + 1)])
    selected_script = scripts[script_choice - 1]
    num_executions = IntPrompt.ask("[bold yellow]Enter the number of times to execute the script[/bold yellow]", default=1)
    wait_time = IntPrompt.ask("[bold yellow]Enter time to wait between each execution (in seconds)[/bold yellow]", default=0)
    parameters = Prompt.ask("[bold yellow]Enter parameters for the script (leave empty if none)[/bold yellow]", default="")

    script_path = os.path.join(script_dir, script_type, selected_script)
    
    # Set execution permissions
    if script_type == "sh":
        console.print(f"[bold blue]Setting execute permissions for {script_path}...[/bold blue]")
        subprocess.run(f"chmod +x {script_path}", shell=True)
    
    for i in range(num_executions):
        console.print(f"[bold blue]Executing {script_path} (Iteration {i + 1}/{num_executions})...[/bold blue]")
        if script_type == "sh":
            result = subprocess.run(f"{script_path} {parameters}", shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(f"python3 {script_path} {parameters}", shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[bold green]Output: {result.stdout}[/bold green]")
        else:
            console.print(f"[bold red]Error: {result.stderr}[/bold red]")
        
        if i < num_executions - 1:
            console.print(f"[bold yellow]Waiting {wait_time} seconds before next execution...[/bold yellow]")
            time.sleep(wait_time)

if __name__ == "__main__":
    memory = {}  # In a real scenario, this would be passed from the main program
    run(memory)
