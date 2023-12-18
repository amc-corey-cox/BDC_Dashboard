import responses
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse, resolve

from django.contrib.auth import get_user_model

from .jira_agent import *
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


class ViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(email='test@email.com', password='test_password')

    def test_documentation_view(self):
        url = reverse('tracker:documentation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertTemplateUsed(response, 'tracker/user_docs.html')

    def test_about_view(self):
        url = reverse('tracker:about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertTemplateUsed(response, 'tracker/about.html')

    def test_ticket_list_view(self):
        url = reverse('tracker:tickets-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')
        redirected_response = self.client.get(response.url)
        self.assertEqual(redirected_response.status_code, 200)

        self.client.login(email='test@email.com', password='test_password')

        auth_response = response = self.client.get(url)
        self.assertEqual(auth_response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertTemplateUsed(response, 'tracker/ticket_list.html')

    def test_ticket_detail_view(self):
        url = reverse('tracker:ticket-detail', kwargs={'pk': 'BDJW-123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/BDJW-123/detail/')
        redirected_response = self.client.get(response.url)

        self.client.login(email='test@email.com', password='test_password')

        auth_response = response = self.client.get(url)
        self.assertEqual(auth_response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertTemplateUsed(response, 'tracker/ticket_detail.html')

    def test_profile_view(self):
        url = reverse('tracker:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertTemplateUsed(response, 'tracker/profile.html')


class JiraAgentTest(TestCase):
    def test_issue_fields_and_field_names_consistency(self):
        issue_fields_keys = set(ISSUE_FIELDS.keys())
        field_names_values = set(FIELD_NAMES.values())

        self.assertEqual(issue_fields_keys, field_names_values)

    @responses.activate
    @override_settings(JIRA_TOKEN='your_test_token', JIRA_BASE_URL='https://test-jira-instance')
    def test_jira_agent_initialization(self):
        # Mock the response for get_board_config method
        responses.add(responses.GET, 'https://test-jira-instance/rest/agile/1.0/board/579/configuration',
                      json={'id': 579, 'name': 'Test Board Config'})

        jira_agent = JiraAgent()

        self.assertEqual(jira_agent.jira_token, 'your_test_token')
        self.assertEqual(jira_agent.base_url, 'https://test-jira-instance')
        self.assertEqual(jira_agent.project, JIRA_PROJECT)
        self.assertEqual(jira_agent.board_id, JIRA_BOARD_ID)
        self.assertEqual(jira_agent.epic_issuetype, JIRA_EPIC_ISSUETYPE)
        self.assertEqual(jira_agent.fields, ISSUE_FIELDS)
        self.assertEqual(jira_agent.field_names, FIELD_NAMES)
