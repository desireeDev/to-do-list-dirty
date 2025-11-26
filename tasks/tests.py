import importlib.util
import os
import json
from django.test import TestCase
from django.urls import reverse
from tasks.models import Task


class TaskTests(TestCase):
    """Batterie complète de tests pour l'app tasks."""

    def setUp(self):
        """Prépare une tâche de test et le chemin du dataset."""
        self.task = Task.objects.create(title="Test Task", complete=False)
        # Chemin vers le dataset (assurez-vous que dataset.json existe)
        self.dataset_path = os.path.join(
            os.path.dirname(__file__), 'dataset.json'
        )

    # ================================
    # Tests pour la view index (/)
    # ================================
    def test_01_index_get(self):
        """GET / affiche correctement la liste."""
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TO DO LIST")

    def test_02_index_post_valid(self):
        """POST / avec données valides ajoute la tâche."""
        response = self.client.post(
            reverse('list'),
            {'title': 'Nouvelle Tâche', 'complete': False}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Nouvelle Tâche').exists())

    def test_03_index_post_invalid(self):
        """POST / avec données invalides ne crée pas de tâche."""
        response = self.client.post(reverse('list'), {'title': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    # ================================
    # Tests pour updateTask
    # ================================
    def test_04_update_task_get_valid_id(self):
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_05_update_task_get_invalid_id(self):
        response = self.client.get(reverse('update_task', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_06_update_task_post_valid(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': 'Task modifiée', 'complete': True}
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Task modifiée')
        self.assertTrue(self.task.complete)

    def test_07_update_task_post_invalid(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, '')

    # ================================
    # Tests pour deleteTask
    # ================================
    def test_08_delete_task_get_valid_id(self):
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_09_delete_task_get_invalid_id(self):
        response = self.client.get(reverse('delete', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_10_delete_task_post(self):
        response = self.client.post(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    # ================================
    # Tests dataset
    # ================================
    def test_11_dataset_import(self):
        """Import du dataset JSON crée toutes les tâches."""
        Task.objects.all().delete()
        with open(self.dataset_path) as f:
            data = json.load(f)
        for item in data:
            Task.objects.create(**item)
        self.assertEqual(Task.objects.count(), len(data))
        for item in data:
            self.assertTrue(Task.objects.filter(title=item['title']).exists())

    def test_12_import_dataset_script(self):
        """Test l'import via le script import_dataset.py."""
        script_path = os.path.join(
            os.path.dirname(__file__), 'import_dataset.py'
        )
        spec = importlib.util.spec_from_file_location(
            "import_dataset", script_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(Task.objects.exists())

    # ================================
    # Tests modèles
    # ================================
    def test_13_task_str(self):
        """Vérifie la représentation en chaîne de la tâche."""
        self.assertEqual(str(self.task), self.task.title)

    def test_14_task_created_field(self):
        """Vérifie que le champ created est défini à la création."""
        self.assertIsNotNone(self.task.created)
