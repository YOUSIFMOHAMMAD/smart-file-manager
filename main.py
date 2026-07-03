#!/usr/bin/env python3
"""
Smart File Manager
An interactive command-line utility to browse, navigate, and manage files.
"""

import os
import sys

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
    print("4) View a file")
    print("5) Rename a file")
    print("6) Delete a file")
    print("7) Categorize files")
    print("8) Find duplicate files")
    print("9) Exit")
    print("=" * 50)


# --- Menu Option Placeholders ---

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


def view_file(current_dir):
    """Display the contents of a text file the user selects."""
    filename = input("Enter filename to view: ").strip()
    path = os.path.join(current_dir, filename)
    if not os.path.isfile(path):
        print(f"[Error] '{filename}' is not a valid file.")
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            print(f"\n--- Contents of {filename} ---\n")
            print(f.read())
            print(f"\n--- End of {filename} ---")
    except PermissionError:
        print("[Error] Permission denied.")
    except Exception as e:
        print(f"[Error] Could not read file: {e}")


def rename_file(current_dir):
    """Rename a file, asking for confirmation before proceeding."""
    filename = input("Enter current filename: ").strip()
    path = os.path.join(current_dir, filename)
    if not os.path.isfile(path):
        print(f"[Error] '{filename}' not found.")
        return
    new_name = input("Enter new filename: ").strip()
    if not new_name:
        print("[Error] Name cannot be empty.")
        return
    confirm = input(f"Rename '{filename}' to '{new_name}'? (y/n): ").lower()
    if confirm == 'y':
        try:
            os.rename(path, os.path.join(current_dir, new_name))
            print("Renamed successfully.")
        except Exception as e:
            print(f"[Error] Rename failed: {e}")
    else:
        print("Renaming cancelled.")


def delete_file(current_dir):
    """Delete a file, but only after showing the filename and requiring the user to type 'yes' to confirm."""
    filename = input("Enter filename to delete: ").strip()
    path = os.path.join(current_dir, filename)
    if not os.path.isfile(path):
        print(f"[Error] '{filename}' not found.")
        return
    confirm = input(f"WARNING: Are you sure you want to delete '{filename}'? Type 'yes' to confirm: ").strip()
    if confirm == 'yes':
        try:
            os.remove(path)
            print("Deleted successfully.")
        except Exception as e:
            print(f"[Error] Deletion failed: {e}")
    else:
        print("Deletion cancelled.")



def categorize_files():
    """Placeholder: Categorize files in the current directory."""
    print("\n[Placeholder] Option 7 selected: Categorizing files...")


def find_duplicate_files():
    """Placeholder: Find duplicate files."""
    print("\n[Placeholder] Option 8 selected: Finding duplicate files...")


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
            choice = input("Enter your choice (1-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            sys.exit(0)

        # Dispatch user choices to their corresponding handler functions
        if choice == "1":
            list_files(current_dir)
        elif choice == "2":
            current_dir = navigate_to_folder(current_dir)
        elif choice == "3":
            current_dir = go_up_directory(current_dir)
        elif choice == "4":
            view_file(current_dir)
        elif choice == "5":
            rename_file(current_dir)
        elif choice == "6":
            delete_file(current_dir)
        elif choice == "7":
            categorize_files()
        elif choice == "8":
            find_duplicate_files()
        elif choice == "9":
            print("\nExiting Smart File Manager. Goodbye!")
            break
        else:
            print("\n[Error] Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
