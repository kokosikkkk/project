from django.test import TestCase
from django.contrib.auth.models import User
from website.models import ToDoList
from django.utils import timezone
from datetime import timedelta

class SimpleTest(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_tasks_page_requires_login(self):
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 302)

    def test_statistics_page_requires_login(self):
        response = self.client.get('/statistics/')
        self.assertEqual(response.status_code, 302)

    def test_register_user(self):
        response = self.client.post('/register/', {
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertRedirects(response, '/profile/')

class TaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        self.client.login(username='testuser2', password='testpass123')
        
        self.task1 = ToDoList.objects.create(
            user=self.user,
            task_name='Тестовая задача',
            task_type='homework',
            status=False,
            spent_time=0,
        )
        self.task2 = ToDoList.objects.create(
            user=self.user,
            task_name='Подготовка к экзамену',
            task_type='exam',
            status=True,
            spent_time=3600,
            completed_at=timezone.now() - timedelta(days=2),
        )

    def test_tasks_appear_in_list(self):
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertContains(response, 'Подготовка к экзамену')

    def test_task_status_toggle(self):
        response = self.client.post(
            f'/toggle/{self.task1.id}/',
            data='{"status": true}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.status)

    def test_statistics_shows_completed_tasks(self):
        response = self.client.get('/statistics/')
        self.assertEqual(response.status_code, 200)