from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /page/author/."""
        response = self.guest_client.get('/page/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /page/author/."""
        response = self.guest_client.get('/page/author/')
        self.assertTemplateUsed(response, 'static_pages/author.html')
