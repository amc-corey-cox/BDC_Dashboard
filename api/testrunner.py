# api/tracker/testrunner.py

from django.test.runner import DiscoverRunner
from django.core.management import call_command


class GetStaticTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        # Run collectstatic before setting up the test environment
        call_command('collectstatic', '--noinput')
        super().setup_test_environment(**kwargs)
