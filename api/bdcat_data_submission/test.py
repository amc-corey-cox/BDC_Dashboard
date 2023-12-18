from django.test import TestCase

from django.urls import reverse, resolve
from django.contrib.admin import AdminSite


class UrlsTest(TestCase):
    def test_admin_url(self):
        url = reverse('admin:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(resolve(url).url_name, 'index')

        resolved_func = resolve(url).func
        expected_func = AdminSite(name='admin').index
        resolved_func_wrapped = resolved_func.__wrapped__ if hasattr(resolved_func, '__wrapped__') else resolved_func
        self.assertEqual(resolved_func_wrapped.__qualname__, expected_func.__qualname__)

    def test_admin_redirect(self):
        url = reverse('admin:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/login/?next=/admin/')
        self.assertEqual(resolve(url).url_name, 'index')

    def test_admin_follow_redirect(self):
        url = reverse('admin:index')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
        self.assertEqual(resolve(url).url_name, 'index')

    def test_admin_login(self):
        url = reverse('admin:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
        self.assertEqual(resolve(url).url_name, 'login')
