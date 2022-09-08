from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
import logging

class NIHSSOSocialAccountAdapter(DefaultSocialAccountAdapter):
	def populate_user(self, request, sociallogin, data):
		logger = logging.getLogger("django")
		username = data.get("email")
		email = data.get("email")
		name = data.get("name")
		logger.info("in populate_user, name = " + name)
		user = sociallogin.user
		user_username(user, username or "")
		user_email(user, email)
		user_field(user, "name", name)
		return user
