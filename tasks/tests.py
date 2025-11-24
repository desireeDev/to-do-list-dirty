import importlib
import os
import json
from django.test import TestCase
from django.urls import reverse
from tasks.models import Task

class TaskTests(TestCase):
    """Batterie complète de tests pour l'app tasks"""

    def setUp(self):
        # Crée une tâche pour tester update/delete
        self.task = Task.objects.create(title="Test Task", complete=False)
        # Prépare le chemin du dataset.json
        self.dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')

    # ----------------- Tests page d'accueil -----------------
    def test_index_url_status(self):
        """Test que la page d'accueil '/' retourne 200"""
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)

    def test_index_url_content(self):
        """Test que la page d'accueil contient 'TO DO LIST'"""
        response = self.client.get(reverse('list'))
        self.assertContains(response, "TO DO LIST")

    # ----------------- Tests update_task -----------------
    def test_update_task_url_valid_id(self):
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_update_task_url_invalid_id(self):
        response = self.client.get(reverse('update_task', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_update_task_post(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': 'Task modifiée', 'complete': True}
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Task modifiée')
        self.assertTrue(self.task.complete)

    # ----------------- Tests delete_task -----------------
    def test_delete_task_url_valid_id(self):
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_task_url_invalid_id(self):
        response = self.client.get(reverse('delete', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_task_post(self):
        response = self.client.post(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    # ----------------- Test dataset.json -----------------
    def test_dataset_import(self):
        """Vérifie que le dataset.json est importé correctement"""
        Task.objects.all().delete()  # Base propre avant import
        with open(self.dataset_path) as f:
            data = json.load(f)
            for item in data:
                Task.objects.create(**item)

        # Vérifie que toutes les tâches du dataset sont présentes
        self.assertEqual(Task.objects.count(), len(data))
        for item in data:
            self.assertTrue(Task.objects.filter(title=item['title']).exists())
    # ----------------- Test import_dataset.py -----------------
def test_import_dataset_script(self):
    """Test que le script import_dataset.py fonctionne correctement"""
    script_path = os.path.join(os.path.dirname(__file__), 'import_dataset.py')
    spec = importlib.util.spec_from_file_location("import_dataset", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Vérifie qu'au moins une tâche a été importée
    self.assertTrue(Task.objects.exists())