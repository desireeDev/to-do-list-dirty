import os
import sys
import django
import json
from tasks.models import Task

# Ajouter la racine du projet au PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Charger les settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo.settings')
django.setup()

# Chemin vers le dataset
dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')

with open(dataset_path) as f:
    data = json.load(f)
    count = 0
    for item in data:
        obj, created = Task.objects.get_or_create(**item)
        if created:
            count += 1

print(f"{count} tâches importées avec succès !")
