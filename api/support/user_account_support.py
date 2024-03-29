# the file contains supporting methods for tests, like:
# 1) method to create a user account (with data generated by EmailAndPasswordGenerator-class)
# 2) method to delete the account (only an account with data generated by EmailAndPasswordGenerator-class before!)

from api.api_library.user_account import UserAccount
import requests
from api.support.temporary_email_generator import EmailAndPasswordGenerator
import allure

class UserAccountSupport:

    @allure.step('Create a new user account with credentials generated')
    def create_user_account(self):
        email_and_password_generator = EmailAndPasswordGenerator()
        username, email, password = email_and_password_generator.generate_username_and_email_and_password()

        not_authorized_session = requests.Session()
        user_account_api = UserAccount(not_authorized_session)
        request_user_registration = user_account_api.user_registration(username, email, password)
        status = request_user_registration[1]
        assert status == 201

        confirmation_token_from_email = email_and_password_generator.get_token_from_confirmation_link_for_registration()
        request_confirm_email = user_account_api.confirm_email(confirmation_token_from_email)
        status = request_confirm_email[1]
        assert status == 200

        return email_and_password_generator, username, email, password

    @allure.step('Delete user account created before (with credentials generated)')
    def delete_user_account(self, email_and_password_generator: EmailAndPasswordGenerator):
        not_authorized_session = requests.Session()
        user_account_api = UserAccount(not_authorized_session)
        email = email_and_password_generator.email
        password = email_and_password_generator.password

        request_user_log_in = user_account_api.log_in_with_email_or_username(email, password)
        response_body, status = request_user_log_in
        assert status == 200
        access_token_for_session = response_body.get("access_token")

        authorized_session = requests.Session()
        authorized_session.headers.update({"Authorization": f"Bearer {access_token_for_session}"})

        user_account_api = UserAccount(authorized_session)
        request_delete_user = user_account_api.request_delete_user()
        status = request_delete_user[1]
        assert status == 200
        code_from_email_to_confirm = email_and_password_generator.get_confirmation_code_for_delete_user()
        assert code_from_email_to_confirm is not None
        request_confirm_delete_user = user_account_api.delete_user(code_from_email_to_confirm)
        status = request_confirm_delete_user[1]
        assert status == 200

