from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
import logging

# The following sites were relied on heavily for instructions on adding a custom provider:
# https://petersimpson.dev/blog/django-allauth-custom-provider/
# https://raphaelyancey.fr/en/2018/05/28/setting-up-django-oauth2-server-client.html

class CustomAccount(ProviderAccount):
    pass


class CustomProvider(OAuth2Provider):

    id = 'nihsso'
    name = 'NIH Login'
    account_class = CustomAccount

    def extract_uid(self, data):
    	print(data)
    	return str(data['email'])

    def extract_common_fields(self, data):
    	logger = logging.getLogger("django")
    	logger.info("In extract_common_fields, email=" + data['email'] + ", name=" + data.get('name', ""))
    	return dict(
                    email=data['email'], name=data.get('name', ""))

    # def get_default_scope(self):
    #     pass


providers.registry.register(CustomProvider)
