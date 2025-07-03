#!/usr/bin/env python
"""
Script to setup the database and import initial data
"""
import os
import sys
import subprocess

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        return False
    
    return True

def setup_database():
    """Setup Django database and import data"""
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    print(f"Setting up database in: {project_root}")
    
    # Django commands
    commands = [
        ("python manage.py makemigrations", "Create database migrations"),
        ("python manage.py migrate", "Apply database migrations"),
        ("python scripts/import_tech_books.py", "Import tech books data"),
        ("python scripts/import_literature_books.py", "Import literature books data"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"Failed to execute: {description}")
            return False
    
    print(f"\n{'='*50}")
    print("Database setup completed successfully!")
    print("Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the development server: python manage.py runserver")
    print('='*50)
    
    return True

if __name__ == '__main__':
    setup_database()