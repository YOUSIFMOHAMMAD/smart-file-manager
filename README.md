# Smart File Manager

A lightweight, interactive command-line file manager for Linux, built in Python.

## Overview
A terminal-based tool for browsing, organizing, and cleaning up files and folders without leaving the command line. Search, rename, and delete all work recursively across the current directory tree. The duplicate finder compares actual file content via MD5 hash, not filenames, so it catches true duplicates other tools would miss.

## Why this project
Built as a solo, independently-owned project — design, implementation, and full test suite written without a collaborator — to demonstrate complete ownership of a project end to end. This project complements my recent acquisition of the Linux Essentials certification.

## Features
1. List files and folders in the current directory.
2. Navigate into a folder
3. Go up one directory
4. View a file's contents or a folder's listing
5. Rename a file or folder — recursive search
6. Find a file or folder anywhere in the current directory tree
7. Create a new file or folder
8. Delete a file or folder (with confirmation)
9. Find duplicate files by content, not filename
10. Exit

## Testing
21 unit tests (unittest + unittest.mock) covering every menu action, including bug fixes: empty directories, non-existent paths, cancelled operations.

## Tech
Python 3, standard library only (os, sys, hashlib, shutil) — zero external dependencies.

## Requirements
Python 3.6+. No pip installs required.

## Installation
git clone https://github.com/YOUSIFMOHAMMAD/smart-file-manager.git
cd smart-file-manager

## How to run
python3 main.py

## Author
Yousif Mohammed
www.linkedin.com/in/yousif-al-hayali-39a102411
