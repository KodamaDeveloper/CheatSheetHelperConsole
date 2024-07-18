#!/usr/bin/env python3

"""
KodamaDeveloper: Intelligent Assistant for Pen Testers
License: MIT License
Author: KodamaDeveloper
"""

import os
import json
import subprocess
import re
import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import track
from importlib import import_module

console = Console()

DATA_DIR = 'data'
VPN_DIR = 'vpn'
CHEATSHEET_DIR = 'cheatsheet'
DICTIONARY_DIR = 'dictionaries'
ASSETS_DIR = 'assets'
AUTHOR_FILE = os.path.join(DATA_DIR, 'author.json')
CONFIG_FILE = 'config.txt'

# Load configuration
def load_config():
    config = {}
    with open(CONFIG_FILE, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config

config = load_config()

# Load plugin options
PLUGIN_OPTIONS_FILE = os.path.join('plugins', 'options.txt')
plugin_options = {}
if os.path.exists(PLUGIN_OPTIONS_FILE):
    with open(PLUGIN_OPTIONS_FILE, 'r') as file:
        for line in file.readlines():
            if line.strip():
                if line.startswith('####'):
                    plugin_options[line.strip()] = None
                else:
                    file_name, description = line.strip().split(' # ', 1)
                    plugin_options[description] = file_name
                    
# Memory management
def load_memory(session_name):
    memory_file = os.path.join(DATA_DIR, session_name, 'memory.json')
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as file:
            return json.load(file)
    return {}

def save_memory(session_name, memory):
    session_dir = os.path.join(DATA_DIR, session_name)
    os.makedirs(session_dir, exist_ok=True)
    memory_file = os.path.join(session_dir, 'memory.json')
    with open(memory_file, 'w') as file:
        json.dump(memory, file, indent=4)

def generate_random_session_name():
    return f"session_{int(time.time())}"

def initialize_memory(session_name):
    memory = {}
    memory['session_name'] = session_name
    memory['target_ip'] = Prompt.ask(f"[bold {config['main_color']}]Enter the target IP[/bold {config['main_color']}]")
    
    os_choices = {
        1: 'Windows',
        2: 'Linux',
        3: 'macOS',
        4: 'FreeBSD',
        5: 'Other'
    }
    console.print(Panel(f"[bold {config['main_color']}]Select the target OS:[/bold {config['main_color']}]", title="Operating System"))
    for idx, os_name in os_choices.items():
        console.print(f"[bold {config['option_color']}] {idx}. {os_name} [/bold {config['option_color']}]")
    
    os_choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose an option (1-5)[/bold {config['main_color']}]", choices=[str(i) for i in os_choices.keys()])
    memory['os'] = os_choices[os_choice]

    memory['domain'] = Prompt.ask(f"[bold {config['main_color']}]Enter the domain (if applicable)[/bold {config['main_color']}]", default="None")
    save_memory(session_name, memory)
    return memory

def display_target_info(memory):
    console.print(f"[bold {config['info_color']}]Target Info - IP: {memory.get('target_ip')} | Domain: {memory.get('domain')} | OS: {memory.get('os')} | Session: {memory.get('session_name')}[/bold {config['info_color']}]")

def check_target_availability(memory):
    target_ip = memory.get('target_ip')
    if not target_ip:
        console.print(f"[bold {config['error_color']}]Target IP not found in memory.[/bold {config['error_color']}]")
        return False
    
    console.print(f"[bold {config['info_color']}]Pinging {target_ip}...[/bold {config['info_color']}]")
    with console.status(f"[bold {config['main_color']}]Pinging...[/bold {config['main_color']}]", spinner="dots"):
        result = subprocess.run(['ping', '-c', '4', target_ip], capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print(f"[bold {config['success_color']}]Target {target_ip} is available.[/bold {config['success_color']}]")
        return True
    else:
        console.print(f"[bold {config['error_color']}]Target {target_ip} is not available.[/bold {config['error_color']}]")
        return False

def list_commands(session_name, memory):
    if "commands" not in memory:
        console.print(f"[bold {config['error_color']}]No commands found in memory.[/bold {config['error_color']}]")
        return
    for i, cmd in enumerate(memory["commands"], start=1):
        console.print(f"[bold {config['option_color']}] {i}. {cmd['command']} [/bold {config['option_color']}]")
    choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a command to re-execute or 0 to go back[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(memory["commands"]) + 1)] + ['0'])
    if choice != 0:
        index = int(choice) - 1
        command = memory["commands"][index]['command']
        console.print(f"[bold {config['info_color']}]Editing command: {command}[/bold {config['info_color']}]")
        edited_command = Prompt.ask(f"[bold {config['main_color']}]Edit the command as needed and press Enter to execute[/bold {config['main_color']}]", default=command)
        display_target_info(memory)
        execute_command(session_name, memory, edited_command)

def execute_command(session_name, memory, command):
    display_target_info(memory)
    with console.status(f"[bold {config['main_color']}]Executing command...[/bold {config['main_color']}]", spinner="bouncingBar"):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        console.print(f"[bold {config['success_color']}]Output: {result.stdout}[/bold {config['success_color']}]")
    else:
        console.print(f"[bold {config['error_color']}]Error: {result.stderr}[/bold {config['error_color']}]")
    if "commands" not in memory:
        memory["commands"] = []
    memory["commands"].append({
        'command': command,
        'output': result.stdout,
        'error': result.stderr
    })
    save_memory(session_name, memory)

def list_plugins(session_name, memory):
    if not plugin_options:
        console.print(f"[bold {config['error_color']}]No plugins available.[/bold {config['error_color']}]")
        return
    
    console.print(f"[bold {config['info_color']}]Available plugins:[/bold {config['info_color']}]")

    categories = {}
    current_category = None
    for description, file_name in plugin_options.items():
        if description.startswith("####"):
            current_category = description[4:].strip()
            categories[current_category] = []
        elif current_category:
            categories[current_category].append((description, file_name))
        else:
            categories['Uncategorized'] = categories.get('Uncategorized', [])
            categories['Uncategorized'].append((description, file_name))

    plugin_index = 1
    plugin_map = {}
    for category, plugins in categories.items():
        console.print(f"\n[bold {config['main_color']}]#### {category}[/bold {config['main_color']}]")
        for description, file_name in plugins:
            console.print(f"[bold {config['option_color']}] {plugin_index}. {description} [/bold {config['option_color']}]")
            plugin_map[plugin_index] = file_name
            plugin_index += 1

    choice = IntPrompt.ask(
        f"[bold {config['main_color']}]Choose a plugin to execute or 0 to go back[/bold {config['main_color']}]",
        choices=[str(i) for i in range(1, plugin_index)] + ['0']
    )
    if choice != 0:
        plugin_name = plugin_map[choice]
        run_plugin(session_name, memory, plugin_name)
        
def run_plugin(session_name, memory, plugin_name):
    try:
        plugin = import_module(f'plugins.{plugin_name[:-3]}')  # Removing .py extension
        plugin.run(memory)
        save_memory(session_name, memory)
    except ModuleNotFoundError:
        console.print(f"[bold {config['error_color']}]Plugin {plugin_name} not found.[/bold {config['error_color']}]")
    except AttributeError:
        console.print(f"[bold {config['error_color']}]The plugin {plugin_name} does not have a 'run(memory)' function.[/bold {config['error_color']}]")

def search_commands(memory):
    if "commands" not in memory:
        console.print(f"[bold {config['error_color']}]No commands found in memory.[/bold {config['error_color']}]")
        return
    query = Prompt.ask(f"[bold {config['main_color']}]Enter the command or part of the command to search[/bold {config['main_color']}]")
    found = False
    for cmd in memory["commands"]:
        if query in cmd['command']:
            console.print(f"[bold {config['option_color']}] Command: {cmd['command']} [/bold {config['option_color']}]")
            console.print(f"[bold {config['success_color']}] Output: {cmd['output']} [/bold {config['success_color']}]")
            if cmd['error']:
                console.print(f"[bold {config['error_color']}] Error: {cmd['error']} [/bold {config['error_color']}]")
            found = True
    if not found:
        console.print(f"[bold {config['error_color']}]No matching commands found.[/bold {config['error_color']}]")

def show_memory(memory):
    memory_str = json.dumps(memory, indent=4)
    console.print(Panel(memory_str, title="Memory Contents", subtitle=f"Session: {memory.get('session_name')}", border_style="green"))

def add_key_value_to_memory(session_name, memory):
    key = Prompt.ask(f"[bold {config['main_color']}]Enter the key to add[/bold {config['main_color']}]")
    value = Prompt.ask(f"[bold {config['main_color']}]Enter the value for this key[/bold {config['main_color']}]")
    memory[key] = value
    save_memory(session_name, memory)
    console.print(f"[bold {config['success_color']}]Added {key}: {value} to memory.[/bold {config['success_color']}]")

def manage_memory(session_name, memory):
    while True:
        console.print(Panel(f"[bold {config['info_color']}]Memory Management[/bold {config['info_color']}]"))
        console.print(f"[bold {config['option_color']}]1. Show memory contents[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]2. Clear memory contents[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]3. Remove commands with errors[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]4. Remove single character commands[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]5. Remove specific command by number[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]6. Add key-value to memory[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]7. Back to main menu[/bold {config['option_color']}]")
        
        choice = Prompt.ask(f"[bold {config['main_color']}]Choose an option[/bold {config['main_color']}]", choices=[str(i) for i in range(1, 8)])
        if choice == "1":
            show_memory(memory)
        elif choice == "2":
            memory.clear()
            save_memory(session_name, memory)
            console.print(f"[bold {config['success_color']}]Memory cleared.[/bold {config['success_color']}]")
        elif choice == "3":
            if "commands" in memory:
                memory["commands"] = [cmd for cmd in memory["commands"] if cmd['error'] == ""]
                save_memory(session_name, memory)
                console.print(f"[bold {config['success_color']}]Removed commands with errors.[/bold {config['success_color']}]")
            else:
                console.print(f"[bold {config['error_color']}]No commands found in memory.[/bold {config['error_color']}]")
        elif choice == "4":
            if "commands" in memory:
                memory["commands"] = [cmd for cmd in memory["commands"] if len(cmd['command']) > 1]
                save_memory(session_name, memory)
                console.print(f"[bold {config['success_color']}]Removed single character commands.[/bold {config['success_color']}]")
            else:
                console.print(f"[bold {config['error_color']}]No commands found in memory.[/bold {config['error_color']}]")
        elif choice == "5":
            if "commands" in memory:
                for i, cmd in enumerate(memory["commands"], start=1):
                    console.print(f"[bold {config['option_color']}] {i}. {cmd['command']} [/bold {config['option_color']}]")
                cmd_number = IntPrompt.ask(f"[bold {config['main_color']}]Enter the command number to remove[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(memory["commands"]) + 1)])
                if 1 <= cmd_number <= len(memory["commands"]):
                    del memory["commands"][cmd_number - 1]
                    save_memory(session_name, memory)
                    console.print(f"[bold {config['success_color']}]Command removed.[/bold {config['success_color']}]")
                else:
                    console.print(f"[bold {config['error_color']}]Invalid command number.[/bold {config['error_color']}]")
            else:
                console.print(f"[bold {config['error_color']}]No commands found in memory.[/bold {config['error_color']}]")
        elif choice == "6":
            add_key_value_to_memory(session_name, memory)
        elif choice == "7":
            break
        else:
            console.print(f"[bold {config['error_color']}]Invalid option, please try again.[/bold {config['error_color']}]")

def list_dictionaries():
    dictionaries = [f for f in os.listdir(DICTIONARY_DIR) if f.endswith('.txt')]
    if not dictionaries:
        console.print(f"[bold {config['error_color']}]No dictionary files found in the {DICTIONARY_DIR} directory.[/bold {config['error_color']}]")
        return None

    console.print(f"[bold {config['info_color']}]Available dictionary files:[/bold {config['info_color']}]")
    for i, dictionary in enumerate(dictionaries, start=1):
        console.print(f"[bold {config['option_color']}] {i}. {dictionary} [/bold {config['option_color']}]")

    dictionary_choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a dictionary file by number[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(dictionaries) + 1)])
    selected_dictionary = dictionaries[dictionary_choice - 1]
    return os.path.join(DICTIONARY_DIR, selected_dictionary)

def execute_cheatsheet_command(session_name, memory):
    cheatsheet_files = [f for f in os.listdir(CHEATSHEET_DIR) if f.endswith('.txt')]
    if not cheatsheet_files:
        console.print(f"[bold {config['error_color']}]No cheatsheet files found in the {CHEATSHEET_DIR} directory.[/bold {config['error_color']}]")
        return

    console.print(f"[bold {config['info_color']}]Available cheatsheet files:[/bold {config['info_color']}]")
    for i, cheatsheet in enumerate(cheatsheet_files, start=1):
        console.print(f"[bold {config['option_color']}] {i}. {cheatsheet} [/bold {config['option_color']}]")

    cheatsheet_choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a cheatsheet file by number[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(cheatsheet_files) + 1)])
    selected_cheatsheet = cheatsheet_files[cheatsheet_choice - 1]
    cheatsheet_path = os.path.join(CHEATSHEET_DIR, selected_cheatsheet)

    with open(cheatsheet_path, 'r') as file:
        cheatsheet = file.readlines()

    categories = {}
    current_category = None

    for line in cheatsheet:
        line = line.strip()
        if line.startswith('####'):
            current_category = line[4:].strip()
            categories[current_category] = []
        elif current_category and line:
            categories[current_category].append(line)

    console.print(f"[bold {config['info_color']}]Available categories:[/bold {config['info_color']}]")
    for i, category in enumerate(categories.keys(), start=1):
        console.print(f"[bold {config['option_color']}] {i}. {category} [/bold {config['option_color']}]")

    category_choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a category by number[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(categories) + 1)])
    selected_category = list(categories.keys())[category_choice - 1]

    console.print(f"[bold {config['info_color']}]Available commands in {selected_category}:[/bold {config['info_color']}]")
    for i, command in enumerate(categories[selected_category], start=1):
        console.print(f"[bold {config['option_color']}] {i}. {command} [/bold {config['option_color']}]")

    command_choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a command to execute by number[/bold {config['main_color']}]", choices=[str(i) for i in range(1, len(categories[selected_category]) + 1)])
    selected_command = categories[selected_category][command_choice - 1]

    # Check if the command requires a dictionary
    if '<dictionary>' in selected_command:
        dictionary_path = list_dictionaries()
        if dictionary_path:
            selected_command = selected_command.replace('<dictionary>', dictionary_path)
        else:
            console.print(f"[bold {config['error_color']}]Dictionary selection failed. Command execution aborted.[/bold {config['error_color']}]")
            return

    # Replace placeholders with memory values or ask the user for input
    placeholders = re.findall(r'\$(\w+)', selected_command)
    for placeholder in placeholders:
        value = memory.get(placeholder, None)
        if not value:
            value = Prompt.ask(f"[bold {config['main_color']}]Enter value for {placeholder}[/bold {config['main_color']}]", default="")
            memory[placeholder] = value
            save_memory(session_name, memory)
        selected_command = selected_command.replace(f'${placeholder}', value)

    console.print(f"[bold {config['info_color']}]Executing command: {selected_command}[/bold {config['info_color']}]")
    execute_command(session_name, memory, selected_command)

def manage_sessions():
    sessions = [f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))]
    
    console.print(f"[bold {config['info_color']}]Available sessions:[/bold {config['info_color']}]")
    for i, session in enumerate(sessions, start=1):
        console.print(f"[bold {config['option_color']}] {i}. {session} [/bold {config['option_color']}]")

    choice = IntPrompt.ask(f"[bold {config['main_color']}]Choose a session to load or 0 to create a new session[/bold {config['main_color']}]", choices=[str(i) for i in range(len(sessions) + 1)] + ['0'])
    if choice == 0:
        session_name = Prompt.ask(f"[bold {config['main_color']}]Enter the session name[/bold {config['main_color']}]", default=generate_random_session_name())
        memory = initialize_memory(session_name)
    else:
        session_name = sessions[choice - 1]
        memory = load_memory(session_name)

    return session_name, memory

def export_session_to_sh(session_name, memory):
    session_dir = os.path.join(DATA_DIR, session_name)
    os.makedirs(session_dir, exist_ok=True)
    export_path = os.path.join(session_dir, f"{session_name}_export.sh")
    with open(export_path, 'w') as file:
        file.write("#!/bin/bash\n\n")
        file.write(f"# Session: {session_name}\n")
        file.write(f"# Target IP: {memory.get('target_ip')}\n")
        file.write(f"# OS: {memory.get('os')}\n")
        file.write(f"# Domain: {memory.get('domain')}\n\n")
        if "commands" in memory:
            for cmd in memory["commands"]:
                file.write(f"{cmd['command']}\n")

    console.print(f"[bold {config['success_color']}]Session exported to {export_path}[/bold {config['success_color']}]")

def add_author():
    if not os.path.exists(AUTHOR_FILE):
        author_name = Prompt.ask(f"[bold {config['main_color']}]Enter your hacker name[/bold {config['main_color']}]")
        author_info = {"author": author_name}
        with open(AUTHOR_FILE, 'w') as file:
            json.dump(author_info, file, indent=4)
    else:
        with open(AUTHOR_FILE, 'r') as file:
            author_info = json.load(file)
        author_name = author_info.get("author", "Unknown")

    console.print(f"[bold {config['info_color']}]Hacker: {author_name}[/bold {config['info_color']}]")

def load_random_ascii():
    ascii_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.txt')]
    if ascii_files:
        selected_file = random.choice(ascii_files)
        with open(os.path.join(ASSETS_DIR, selected_file), 'r') as file:
            return file.read()
    return None

def change_target_ip(session_name, memory):
    new_target_ip = Prompt.ask(f"[bold {config['main_color']}]Enter the new target IP[/bold {config['main_color']}]")
    memory['target_ip'] = new_target_ip
    save_memory(session_name, memory)
    console.print(f"[bold {config['success_color']}]Target IP changed to {new_target_ip}[/bold {config['success_color']}]")

def main_menu():
    add_author()
    session_name, memory = manage_sessions()

    while True:
        ascii_art = load_random_ascii()
        if ascii_art:
            console.print(Panel(ascii_art, title="Welcome", subtitle=config['greeting_message'], border_style=config['main_color']))

        console.print(Panel(f"[bold {config['main_color']}]Hacker: {config['author_name']}[/bold {config['main_color']}]\n[bold {config['main_color']}]User: {config['user_name']}[/bold {config['main_color']}]\n[bold {config['main_color']}]Message: {config['greeting_message']}[/bold {config['main_color']}]"))
        display_target_info(memory)
        console.print(f"[bold {config['option_color']}]1. Execute command from cheatsheet[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]2. Execute a new command[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]3. List and re-execute previous commands[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]4. Execute a plugin[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]5. Search executed commands[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]6. Show memory contents[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]7. Manage memory[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]8. Check target availability[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]9. List and execute scripts[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]10. Export session to shell script[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]11. Manage sessions[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]12. Change target IP[/bold {config['option_color']}]")
        console.print(f"[bold {config['option_color']}]0. Exit[/bold {config['option_color']}]")
        
        choice = Prompt.ask(f"[bold {config['main_color']}]Choose an option[/bold {config['main_color']}]", choices=[str(i) for i in range(14)])
        if choice == "1":
            execute_cheatsheet_command(session_name, memory)
        elif choice == "2":
            display_target_info(memory)
            command = Prompt.ask(f"[bold {config['main_color']}]Enter the command to execute[/bold {config['main_color']}]")
            execute_command(session_name, memory, command)
        elif choice == "3":
            list_commands(session_name, memory)
        elif choice == "4":
            list_plugins(session_name, memory)
        elif choice == "5":
            search_commands(memory)
        elif choice == "6":
            show_memory(memory)
        elif choice == "7":
            manage_memory(session_name, memory)
        elif choice == "8":
            check_target_availability(memory)
        elif choice == "9":
            list_and_execute_scripts(memory)
        elif choice == "10":
            export_session_to_sh(session_name, memory)
        elif choice == "11":
            session_name, memory = manage_sessions()
        elif choice == "12":
            change_target_ip(session_name, memory)
        elif choice == "0":
            console.print(Panel(f"[bold {config['main_color']}]Exiting the program...[/bold {config['main_color']}]"))
            break
        else:
            console.print(Panel(f"[bold {config['error_color']}]Invalid option, please try again.[/bold {config['error_color']}]"))

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join('plugins', 'scripts', 'sh'), exist_ok=True)
    os.makedirs(DICTIONARY_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    main_menu()
