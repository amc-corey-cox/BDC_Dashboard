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
    @responses.activate
    @override_settings(JIRA_TOKEN='your_test_token', JIRA_BASE_URL='https://test-jira-instance')
    def setUp(self):
        response_json = {
            "id": 579,
            "name": "Test Board Config",
            "type": "kanban",
            "filter": {"id": "20705"},
            "subQuery": {"query": "fixVersion in unreleasedVersions() OR fixVersion is EMPTY"},
            "columnConfig": {
                "columns": [
                    {"name": "Backlog", "statuses": []},
                    {"name": "IDENTIFIED", "statuses": [{"id": "13501"}]},
                    {"name": "BLOCKED", "statuses": [{"id": "10105"}]},
                    {"name": "PRE-INGESTION", "statuses": [{"id": "13300"}]},
                    {"name": "GEN3 INGESTION", "statuses": [{"id": "13900"}]},
                    {"name": "BDC DATA RELEASE", "statuses": [{"id": "13901"}]},
                    {"name": "BDC RELEASED", "statuses": [{"id": "13902"}]}
                ],
                "constraintType": "issueCount"
            },
            "ranking": {"rankCustomFieldId": 10009}
        }
        response_url = 'https://test-jira-instance/rest/agile/1.0/board/579/configuration'
        responses.add(responses.GET, response_url, json=response_json, status=200)

        self.jira_agent = JiraAgent()

    def test_issue_fields_and_field_names_consistency(self):
        issue_fields_keys = set(ISSUE_FIELDS.keys())
        field_names_values = set(FIELD_NAMES.values())

        self.assertEqual(issue_fields_keys, field_names_values)

    def test_jira_agent__init__(self):
        self.assertEqual(self.jira_agent.jira_token, 'your_test_token')
        self.assertEqual(self.jira_agent.base_url, 'https://test-jira-instance')
        self.assertEqual(self.jira_agent.project, JIRA_PROJECT)
        self.assertEqual(self.jira_agent.board_id, JIRA_BOARD_ID)
        self.assertEqual(self.jira_agent.epic_issuetype, JIRA_EPIC_ISSUETYPE)
        self.assertEqual(self.jira_agent.fields, ISSUE_FIELDS)
        self.assertEqual(self.jira_agent.field_names, FIELD_NAMES)

    @responses.activate
    def test_get_data(self):
        responses.add(responses.GET, 'https://test-jira-instance/not/the/right/place', status=404)
        data = self.jira_agent.get_data('/not/the/right/place')
        self.assertIsNone(data)

        responses.add(responses.GET, 'https://test-jira-instance/rest/agile/1.0/board/579/configuration',
                      json={'id': 579, 'name': 'Test Board Config'})
        data = self.jira_agent.get_data('/rest/agile/1.0/board/579/configuration')

        self.assertEqual(data['id'], 579)
        self.assertEqual(data['name'], 'Test Board Config')

    @responses.activate
    def test_get_board_config(self):
        responses.add(responses.GET, 'https://test-jira-instance/rest/agile/1.0/board/579/configuration',
                      json={'id': 579, 'name': 'Test Board Config'})

        board_config = self.jira_agent.get_board_config()

        self.assertEqual(board_config['id'], 579)
        self.assertEqual(board_config['name'], 'Test Board Config')

    @responses.activate
    def test_get_board_statuses(self):
        # Agent is initialized in setUp()
        board_statuses = self.jira_agent.get_board_statuses()
        self.assertEqual(len(board_statuses), 7)

        board_statuses = self.jira_agent.get_board_statuses(remove_statuses="Backlog")
        self.assertEqual(len(board_statuses), 6)

        board_statuses = self.jira_agent.get_board_statuses(remove_statuses=["Backlog", "BLOCKED"])
        self.assertEqual(len(board_statuses), 5)

        expected_statuses = [{'name': 'IDENTIFIED', 'selected': False, 'statuses': [{'id': '13501'}]},
                             {'name': 'PRE-INGESTION', 'selected': False, 'statuses': [{'id': '13300'}]},
                             {'name': 'GEN3 INGESTION', 'selected': False, 'statuses': [{'id': '13900'}]},
                             {'name': 'BDC DATA RELEASE', 'selected': False, 'statuses': [{'id': '13901'}]},
                             {'name': 'BDC RELEASED', 'selected': False, 'statuses': [{'id': '13902'}]}]

        self.assertEqual(board_statuses, expected_statuses)

    def test_get_fields_string(self):
        fields_string = self.jira_agent.get_fields_string(['summary', 'status'])
        self.assertEqual(fields_string, 'fields=summary,status')

        fields_string = self.jira_agent.get_fields_string()
        self.assertEqual(len(fields_string), 384)
        self.assertIn('fields=', fields_string)

    @responses.activate
    def test_get_epics_by_contact(self):
        base_url = 'https://test-jira-instance'
        endpoint = '/rest/api/latest/search?jql=project=BDJW+AND+issuetype=10000&fields=status,summary'
        responses.add(responses.GET, base_url + endpoint, json={'issues': [{'key': 'BDJW-123'}]})

        test_epics = self.jira_agent.get_epics_by_contact('staff', ['status', 'summary'])
        self.assertEqual(len(test_epics), 1)
        self.assertEqual(test_epics[0]['key'], 'BDJW-123')

        fields_string = self.jira_agent.get_fields_string()
        endpoint = f"/rest/api/latest/search?jql=project=BDJW+AND+issuetype=10000&{fields_string}"
        responses.add(responses.GET, base_url + endpoint, json={'issues': [{'key': 'BDJW-123'}]})

        test_epics = self.jira_agent.get_epics_by_contact('staff')
        self.assertEqual(len(test_epics), 1)
        self.assertEqual(test_epics[0]['key'], 'BDJW-123')

    @responses.activate
    def test_get_issues_by_contact(self):
        base_url = 'https://test-jira-instance'
        endpoint = '/rest/api/latest/search?jql=project=BDJW+AND+issuetype=10000&fields=customfield_15202,summary'
        responses.add(responses.GET, base_url + endpoint, json={'issues': [{'key': 'BDJW-123'}]})
        endpoint = '/rest/api/latest/search?jql=cf[10005]+in+(BDJW-123)&fields=status,summary'
        json_result = {'issues': [{'key': 'BDJW-234', 'fields': {'customfield_10005': 'BDJW-123'}}]}
        responses.add(responses.GET, base_url + endpoint, json=json_result)

        test_issues = self.jira_agent.get_issues_by_contact('staff', ['status', 'summary'])
        self.assertEqual(len(test_issues), 1)
        self.assertEqual(test_issues[0]['key'], 'BDJW-234')

        fields_string = self.jira_agent.get_fields_string()
        endpoint = f"/rest/api/latest/search?jql=cf[10005]+in+(BDJW-123)&{fields_string}"
        json_result = {'issues': [{'key': 'BDJW-234', 'fields': {'customfield_10005': 'BDJW-123'}}]}
        responses.add(responses.GET, base_url + endpoint, json=json_result)

        test_issues = self.jira_agent.get_issues_by_contact('staff')
        self.assertEqual(len(test_issues), 1)
        self.assertEqual(test_issues[0]['key'], 'BDJW-234')

    @responses.activate
    def test_get_issue(self):
        base_url = 'https://test-jira-instance'
        endpoint = '/rest/api/latest/issue/BDJW-123?fields=status'
        responses.add(responses.GET, base_url + endpoint, json={'key': 'BDJW-123', 'fields': {'status': 'Test'}})

        issue = self.jira_agent.get_issue('BDJW-123', ['status'])
        self.assertEqual(issue['key'], 'BDJW-123')
        self.assertEqual(issue['fields']['status'], 'Test')
