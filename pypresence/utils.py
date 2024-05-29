"""Util functions that are needed but messy."""
import asyncio
import json
import os
import sys
import tempfile
import time

from .exceptions import PyPresenceException


def remove_none(d: dict):
    for item in d.copy():
        if isinstance(d[item], dict):
            if len(d[item]):
                d[item] = remove_none(d[item])
            if not len(d[item]):
                del d[item]
        elif d[item] is None:
            del d[item]
    return d

## FUNCION AGREGADA: Busca la ruta donde esta el Unix Socket de Discord para establecer el estado de Discord, esto sirve para cuando el script dew HTB-Presence se ejecute como Root.

def find_folder(file_prefix, directory='/'):
    # Walk through all directories and files within the specified directory
    for r, d, f in os.walk(directory):
        for file in f:
            if file.startswith(file_prefix):
                return r + os.sep  # Add a slash at the end of the folder path

    # If the file is not found
    return None

target_prefix = "discord-ipc-"
start_directory = "/run/user"  # You can change this directory if you want to start the search elsewhere

found_folder = find_folder(target_prefix, start_directory)

if found_folder:
    print("A file starting with the specified prefix was found in the following folder:")
    print(found_folder)
else:
    print("No file starting with the specified prefix was found in the system.")


# Returns on first IPC pipe matching Discord's
def get_ipc_path(pipe=None):
    ipc = 'discord-ipc-'
    if pipe:
        ipc = f"{ipc}{pipe}"

    if sys.platform in ('linux', 'darwin'):

        tempdir = os.environ.get('XDG_RUNTIME_DIR') or (f"/run/user/{os.getuid()}" if os.path.exists(f"/run/user/{os.getuid()}") else tempfile.gettempdir()) 
        paths = ['.', 'snap.discord', 'app/com.discordapp.Discord', 'app/com.discordapp.DiscordCanary']
        if os.getuid() == 0:
            tempdir = found_folder
        
    elif sys.platform == 'win32':
        tempdir = r'\\?\pipe'
        paths = ['.']
    else:
        return
    
    for path in paths:
        full_path = os.path.abspath(os.path.join(tempdir, path))
        if sys.platform == 'win32' or os.path.isdir(full_path):
            for entry in os.scandir(full_path):
                if entry.name.startswith(ipc) and os.path.exists(entry):
                    return entry.path


def get_event_loop(force_fresh=False):
    if force_fresh:
        return asyncio.new_event_loop()
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()
    if running.is_closed():
        return asyncio.new_event_loop()
    return running
