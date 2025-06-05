#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Configurar el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    """Run administrative tasks."""
    # Asegurarse de que el directorio del proyecto esté en el PYTHONPATH
    project_path = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_path))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
