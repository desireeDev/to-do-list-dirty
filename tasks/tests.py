from django.test import TestCase
from django.urls import reverse
from tasks.models import Task

class TaskURLTests(TestCase):
    #Test Urls for the tasks app
    def setUp(self):
        # Crée une tâche pour tester update/delete
        self.task = Task.objects.create(title="Test Task", complete=False)

    def test_index_url(self):
        """Test que la page d'accueil '/' fonctionne"""
        response = self.client.get(reverse('list'))  # <-- changé ici
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TO DO LIST")

    def test_update_task_url(self):
        """Test que la page de mise à jour d'une tâche fonctionne"""
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_task_url(self):
        """Test que la page de suppression d'une tâche fonctionne"""
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    
