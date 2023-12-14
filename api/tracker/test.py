from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from .views import TicketsList, UserProfile, TicketDetail, DocumentationView, AboutView


class UrlsTest(SimpleTestCase):
    def test_tickets_list_url(self):
        url = reverse('tracker:tickets-list')
        self.assertEqual(resolve(url).func.view_class, TicketsList)

    def test_user_profile_url(self):
        url = reverse('tracker:profile')
        self.assertEqual(resolve(url).func.view_class, UserProfile)

    def test_ticket_detail_url(self):
        url = reverse('tracker:ticket-detail', kwargs={'pk': 'valid_string'})
        self.assertEqual(resolve(url).func.view_class, TicketDetail)

    def test_documentation_url(self):
        url = reverse('tracker:documentation')
        self.assertEqual(resolve(url).func.view_class, DocumentationView)

    def test_about_url(self):
        url = reverse('tracker:about')
        self.assertEqual(resolve(url).func.view_class, AboutView)


class DocumentationViewTest(TestCase):
    def test_template_rendering(self):
        url = reverse('tracker:documentation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/user_docs.html')
