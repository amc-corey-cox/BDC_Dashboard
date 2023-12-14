from django.test import SimpleTestCase
from django.urls import reverse, resolve


class UrlsTest(SimpleTestCase):
    def test_admin_url(self):
        url = reverse('admin:index')
        self.assertEqual(resolve(url).url_name, 'index')

    def test_accounts_url(self):
        url = reverse('account_login')  # Assuming you are using allauth for login
        self.assertEqual(resolve(url).url_name, 'account_login')
