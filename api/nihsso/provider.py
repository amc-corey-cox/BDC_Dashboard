from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

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
        return dict(
                    email=data['email'])

    # def get_default_scope(self):
    #     pass


providers.registry.register(CustomProvider)
