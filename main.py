#!/usr/bin/env python3
"""
Smart File Manager
An interactive command-line utility to browse, navigate, and manage files.
"""

import os
import sys
import hashlib
import shutil

def display_menu(current_dir):
    """
    Prints the main interactive menu options along with the current working directory.
    """
    print("\n" + "=" * 50)
    print(f" Smart File Manager | Current Dir: {current_dir}")
    print("=" * 50)
    print("1) List files in current directory")
    print("2) Navigate to a folder")
    print("3) Go up one directory")
    print("4) View a file/folder")
    print("5) Rename a file/folder")
    print("6) Find a file/folder")
    print("7) Create a file/folder")
    print("8) Delete a file/folder")
    print("9) View duplicate files")
    print("10) Exit")
    print("=" * 50)



def list_files(current_dir):
    """List all files and folders in the current directory with their type clearly shown."""
    print()
    try:
        # scandir is highly efficient as it gets entry types directly without extra stat calls
        with os.scandir(current_dir) as entries:
            items = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
            if not items:
                print("The directory is empty.")
                return
            
            # Print a clean, beautifully formatted header
            print(f"{'Name':<40} | {'Type':<10}")
            print("-" * 55)
            for entry in items:
                item_type = "[Folder]" if entry.is_dir() else "[File]"
                print(f"{entry.name:<40} | {item_type:<10}")
    except PermissionError:
        print("[Error] Permission denied to read this directory.")
    except FileNotFoundError:
        print("[Error] The current directory does not exist.")
    except Exception as e:
        print(f"[Error] Failed to list directory: {e}")


def navigate_to_folder(current_dir):
    """Let the user type a folder name to navigate into it, with graceful error handling."""
    print()
    folder_name = input("Enter folder name or path to navigate to: ").strip()
    if not folder_name:
        print("[Error] Folder name cannot be empty.")
        return current_dir

    # Support navigating to absolute or relative paths
    target_dir = os.path.abspath(os.path.join(current_dir, folder_name))

    if not os.path.exists(target_dir):
        print(f"[Error] The path '{folder_name}' does not exist.")
        return current_dir
    if not os.path.isdir(target_dir):
        print(f"[Error] '{folder_name}' is not a directory.")
        return current_dir

    # Verify we have permission/can read it
    try:
        os.listdir(target_dir)
    except PermissionError:
        print(f"[Error] Permission denied to access folder '{folder_name}'.")
        return current_dir
    except Exception as e:
        print(f"[Error] Cannot access folder '{folder_name}': {e}")
        return current_dir

    print(f"Successfully navigated to: {target_dir}")
    return target_dir


def go_up_directory(current_dir):
    """Move up one directory level."""
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
    if parent_dir == current_dir:
        print("\nAlready at the root directory.")
    else:
        print(f"\nMoved up to: {parent_dir}")
    return parent_dir


def view_item(current_dir):
    """Searches for a file or folder by name recursively and offers to view/list."""
    print()
    name = input("Enter name to view: ").strip()
    if not name:
        print("[Error] Name cannot be empty.")
        return

    # Find all matches recursively to handle potential name conflicts
    matches = []
    for root, dirs, files in os.walk(current_dir):
        for item in dirs + files:
            if item.lower() == name.lower():
                matches.append(os.path.join(root, item))

    if not matches:
        print(f"No items found with name '{name}'.")
        return
        
    print(f"\nFound {len(matches)} item(s) matching '{name}':")
    for i, path in enumerate(matches):
        print(f"{i+1}) {path}")
        
    choice = input("\nEnter number to view/list, or 'q' to cancel: ").strip()
    if choice.lower() == 'q':
        return
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(matches):
            target = matches[idx]
            
            if os.path.isfile(target):
                with open(target, 'r', encoding='utf-8') as f:
                    print(f"\n--- Contents of {os.path.basename(target)} ---\n")
                    print(f.read())
                    print(f"\n--- End of {os.path.basename(target)} ---")
            elif os.path.isdir(target):
                print(f"\n--- Contents of Directory: {os.path.basename(target)} ---")
                with os.scandir(target) as entries:
                    for entry in entries:
                        type_str = "[Folder]" if entry.is_dir() else "[File]"
                        print(f"{type_str} {entry.name}")
                print("--- End ---")
        else:
            print("[Error] Invalid selection.")
    except Exception as e:
        print(f"[Error] Action failed: {e}")


def rename_file(current_dir):
    """Rename a file or folder, handling ambiguous names by listing all matches."""
    print()
    name = input("Enter name to rename: ").strip()

    # Find all matches recursively to handle potential name conflicts
    matches = []
    for root, dirs, files in os.walk(current_dir):
        for item in dirs + files:
            if item.lower() == name.lower():
                matches.append(os.path.join(root, item))

    if not matches:
        print(f"No items found with name '{name}'.")
        return

    print(f"\nFound {len(matches)} item(s) matching '{name}':")
    for i, path in enumerate(matches):
        print(f"{i+1}) {path}")

    choice = input("\nEnter number to rename, or 'q' to cancel: ").strip()
    if choice.lower() == 'q':
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(matches):
            target = matches[idx]
            parent = os.path.dirname(target)
            new_name = input(f"Enter new name for '{os.path.basename(target)}': ").strip()
            if not new_name:
                print("[Error] Name cannot be empty.")
                return

            # Check for collision in the parent directory
            new_path = os.path.join(parent, new_name)
            if os.path.exists(new_path):
                print(f"[Error] '{new_name}' already exists in '{parent}'.")
                return

            confirm = input(f"Rename '{os.path.basename(target)}' to '{new_name}'? (y/n): ").lower()
            if confirm == 'y':
                os.rename(target, new_path)
                print("Renamed successfully.")
            else:
                print("Renaming cancelled.")
        else:
            print("[Error] Invalid selection.")
    except Exception as e:
        print(f"[Error] Rename failed: {e}")


def find_item(current_dir):
    """Searches recursively for a file/folder and offers to view or navigate to it."""
    print()
    name = input("Enter name to find: ").strip()
    if not name:
        print("[Error] Name cannot be empty.")
        return current_dir

    matches = []
    for root, dirs, files in os.walk(current_dir):
        for item in dirs + files:
            if item.lower() == name.lower():
                matches.append(os.path.join(root, item))

    if not matches:
        print(f"No items found with name '{name}'.")
        return current_dir

    print(f"\nFound {len(matches)} item(s) matching '{name}':")
    for i, path in enumerate(matches):
        print(f"{i+1}) {path}")
        
    choice = input("\nEnter number to select, or 'q' to cancel: ").strip()
    if choice.lower() == 'q':
        return current_dir
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(matches):
            target = matches[idx]
            
            if os.path.isdir(target):
                confirm = input(f"Navigate to directory '{target}'? (y/n): ").lower()
                if confirm == 'y':
                    print(f"Successfully navigated to: {target}")
                    return target
            else:
                confirm = input(f"View file '{target}'? (y/n): ").lower()
                if confirm == 'y':
                    with open(target, 'r', encoding='utf-8') as f:
                        print(f"\n--- Contents of {os.path.basename(target)} ---\n")
                        print(f.read())
                        print(f"\n--- End of {os.path.basename(target)} ---")
        else:
            print("[Error] Invalid selection.")
    except Exception as e:
        print(f"[Error] Action failed: {e}")
        
    return current_dir



def create_item(current_dir):
    """Create a new file or directory."""
    print()
    name = input("Enter name for the new file or directory: ").strip()
    if not name:
        print("[Error] Name cannot be empty.")
        return
    item_type = input("Create as (f)ile or (d)irectory? (f/d): ").lower().strip()
    path = os.path.join(current_dir, name)
    try:
        if item_type == 'f':
            with open(path, 'w') as f: pass
            print(f"File '{name}' created.")
        elif item_type == 'd':
            os.makedirs(path)
            print(f"Directory '{name}' created.")
        else:
            print("[Error] Invalid type. Use 'f' for file or 'd' for directory.")
    except Exception as e:
        print(f"[Error] Creation failed: {e}")


def delete_item(current_dir):
    """Deletes a file or directory, handling ambiguous names by listing all matches."""
    print()
    name = input("Enter name to delete: ").strip()
    
    # Find all matches recursively to handle potential name conflicts
    matches = []
    for root, dirs, files in os.walk(current_dir):
        for item in dirs + files:
            if item.lower() == name.lower():
                matches.append(os.path.join(root, item))
    
    if not matches:
        print(f"No items found with name '{name}'.")
        return
        
    print(f"\nFound {len(matches)} item(s) matching '{name}':")
    for i, path in enumerate(matches):
        print(f"{i+1}) {path}")
        
    choice = input("\nEnter number to delete, or 'q' to cancel: ").strip()
    if choice.lower() == 'q':
        return
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(matches):
            target = matches[idx]
            confirm = input(f"Are you sure you want to delete '{target}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"'{target}' deleted successfully.")
            else:
                print("Deletion cancelled.")
        else:
            print("[Error] Invalid selection.")
    except Exception as e:
        print(f"[Error] Deletion failed: {e}")


def calculate_md5(file_path):
    """Calculate the MD5 hash for a file's content, reading in chunks to conserve memory."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None


def find_duplicates(current_dir):
    """
    Scan all files in the current directory, calculate MD5 hash for each file's content,
    and return a dictionary grouping files sharing the same hash (only groups with duplicates are returned).
    """
    hash_map = {}
    with os.scandir(current_dir) as entries:
        for entry in entries:
            if entry.is_file():
                file_hash = calculate_md5(entry.path)
                if file_hash:
                    hash_map.setdefault(file_hash, []).append(entry.name)
                    
    # Filter out entries that do not have any duplicates (i.e., list length <= 1)
    duplicates = {h: sorted(files, key=str.lower) for h, files in hash_map.items() if len(files) > 1}
    return duplicates


def find_duplicate_files(current_dir):
    """Scan the current directory for duplicate files based on content hashes and display them."""
    print()
    try:
        duplicates = find_duplicates(current_dir)
        if not duplicates:
            print("No duplicate files found in this directory.")
            return
            
        print("Duplicate Files Found:")
        print("-" * 30)
        group_num = 1
        for file_hash, files in sorted(duplicates.items()):
            print(f"Group {group_num} [MD5: {file_hash}]:")
            for filename in files:
                print(f"  - {filename}")
            print()
            group_num += 1
    except PermissionError:
        print("[Error] Permission denied to read this directory.")
    except FileNotFoundError:
        print("[Error] The current directory does not exist.")
    except Exception as e:
        print(f"[Error] Failed to find duplicate files: {e}")


def exit_program():
    """Prints a goodbye message and exits the application."""
    print("\nExiting Smart File Manager. Goodbye!")
    sys.exit(0)


# --- Main Application Loop ---

def main():
    """
    Main loop that controls the interactive CLI menu and coordinates user actions.
    """
    # Start tracking the current working directory
    current_dir = os.getcwd()

    while True:
        display_menu(current_dir)
        try:
            choice = input("Enter your choice (1-10): ").strip()
        except (KeyboardInterrupt, EOFError):
            exit_program()

        # Dispatch user choices
        if choice == "1":
            list_files(current_dir)
        elif choice == "2":
            current_dir = navigate_to_folder(current_dir)
        elif choice == "3":
            current_dir = go_up_directory(current_dir)
        elif choice == "4":
            view_item(current_dir)
        elif choice == "5":
            rename_file(current_dir)
        elif choice == "6":
            current_dir = find_item(current_dir)
        elif choice == "7":
            create_item(current_dir)
        elif choice == "8":
            delete_item(current_dir)
        elif choice == "9":
            find_duplicate_files(current_dir)
        elif choice == "10":
            exit_program()
        else:
            print("\n[Error] Invalid choice. Please enter a number from 1 to 10.")



if __name__ == "__main__":
    main()
