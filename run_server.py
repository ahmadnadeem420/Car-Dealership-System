import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print(f"Starting Django server from: {current_dir}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cardealership.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver"]) 