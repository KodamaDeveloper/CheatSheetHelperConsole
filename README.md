# CheatSheetHelperConsole

# Intelligent Assistant for Pen Testers

## Overview
An intelligent assistant designed for penetration testers. It facilitates various pentesting tasks, including command execution, plugin management, VPN connection handling, and cheatsheet usage. This guide explains how to use the program, manage sessions, execute commands from cheatsheets, create plugins, and customize the tool.

## Features

- Command execution and history
- Plugin management
- VPN connection handling
- Cheatsheet management and execution
- Session and memory management
- Customizable interface

## Configuration

Customize the appearance and behavior of the tool by editing the config.txt file. Here is an example configuration:

author_name=KOdDEv
user_name=KOdy
greeting_message=Assistant for pentesting!
main_color=#00FF00
highlight_color=#FFD700
error_color=#FF0000
info_color=#1E90FF
success_color=#00FF00
warning_color=#FFA500
option_color=#04FF12

/ Adding ASCII Art

    Place ASCII art text files in the assets directory.
    Ensure the files have a .txt extension.
    The program will display a random ASCII art file on each menu interaction.


## Sessions and Memory Management

Manage sessions to save and load different pentesting activities. Memory is used to store session-specific information.

    Manage sessions: Create, load, and save sessions.
    Show memory contents: Display current session memory.
    Manage memory: Add key-value pairs, clear memory, or remove specific commands.

## VPN Connections

Handle VPN connections required for certain pentesting environments.

    Manage VPN connections: Start or stop VPN connections using .ovpn files located in the vpn directory.

## Cheatsheet Management

Execute pre-defined commands from cheatsheets. Cheatsheets are stored in the cheatsheet directory.

    Execute command from cheatsheet: Choose and run commands from available cheatsheets with variable.

Example Cheatsheets>

Here are some example cheatsheets to get you started:
cheatsheet/nmap_cheatsheet.txt

nmap -Pn -n -vvv $target_ip
nmap -Pn -n -vvv -p1-500 $target_ip
nmap -Pn -n -vvv -p- $target_ip
nmap -Pn -n -vvv -p22,80 $target_ip
sudo nmap -Pn -n -vvv -sU $target_ip

## Command Execution

Execute new commands and view command history.

    Execute a new command: Enter and run any shell command.
    List and re-execute previous commands: View and re-run previously executed commands.
    Search executed commands: Search through the command history.


## Creating a Plugin

To extend the functionality, you can create custom plugins. Plugins are Python scripts stored in the `plugins` directory. Each plugin must have a `run(memory)` function that will be executed when the plugin is selected.

### Steps to Create a Plugin

1. **Create a New Python Script:**
   Create a new Python script in the `plugins` directory. For example, create `example_plugin.py`.

2. **Define the `run(memory)` Function:**
   In your new script, define a function named `run` that takes a single argument `memory`. This function will contain the logic of your plugin.

3. **Add the Plugin to `options.txt`:**
   Add an entry for your plugin in the `plugins/options.txt` file. This entry should include the file name of your plugin and a description.

### Example Plugin

Here is an example of a very basic plugin:

#### `plugins/example_plugin.py`

```python
def run(memory):
    print("This is an example plugin.")
