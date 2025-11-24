from django.test import TestCase
from django.urls import reverse
from tasks.models import Task

class TaskURLTests(TestCase):
    """Batterie de tests pour les URLs principales de l'app tasks"""

    def setUp(self):
        # Crée une tâche pour tester update/delete
        self.task = Task.objects.create(title="Test Task", complete=False)

    # ----------------- Tests page d'accueil -----------------
    def test_index_url_status_and_content(self):
        """Test que la page d'accueil '/' fonctionne et contient le texte attendu"""
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TO DO LIST")

    # ----------------- Tests update_task -----------------
    def test_update_task_url_valid_id(self):
        """Test que la page de mise à jour d'une tâche fonctionne avec un ID valide"""
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_update_task_url_invalid_id(self):
        """Test que l'URL update_task avec un ID inexistant retourne 404"""
        response = self.client.get(reverse('update_task', args=[999]))
        self.assertEqual(response.status_code, 404)

    # ----------------- Tests delete_task -----------------
    def test_delete_task_url_valid_id(self):
        """Test que la page de suppression d'une tâche fonctionne avec un ID valide"""
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_task_url_invalid_id(self):
        """Test que l'URL delete_task avec un ID inexistant retourne 404"""
        response = self.client.get(reverse('delete', args=[999]))
        self.assertEqual(response.status_code, 404)

    # ----------------- Tests POST pour update/delete -----------------
    def test_update_task_post(self):
        """Test la mise à jour d'une tâche via POST"""
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': 'Task modifiée', 'complete': True}
        )
        self.assertEqual(response.status_code, 302)  # Redirect après update
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Task modifiée')
        self.assertTrue(self.task.complete)

    def test_delete_task_post(self):
        """Test la suppression d'une tâche via POST"""
        response = self.client.post(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)  # Redirect après suppression
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
