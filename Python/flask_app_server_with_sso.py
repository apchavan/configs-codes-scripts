"""
    Custom Flask server definition module for Microsoft's Single Sign-On (SSO).
    This can be useful in applications where Flask server is used in the backend.

    Reference 1: https://github.com/naderelshehabi/dash-flask-login/blob/main/app.py

    Reference 2: https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2

    Reference 3: https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-web-app-python-sign-in
"""


import flask
import flask_login
import msal

from modules.utility_functions import (
    get_flask_server_manager_key,
    get_sso_client_id,
    get_sso_client_secret_credential,
    get_sso_authority,
    get_sso_graph_endpoint,
    get_sso_scope,
)


class FlaskServerManager:
    """
    Class that defines custom Flask server configuration required to handle Single Sign-On (SSO) login sessions for the app.
    """

    # Exposing the Flask Server to enable configuring it for logging in
    _server: flask.Flask = None

    # Login manager object will be used to login / logout users
    _login_manager: flask_login.LoginManager = None

    # Single Sign-On (SSO) authentication
    # Reference: https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/dev/sample/username_password_sample.py
    _sso_auth: msal.ConfidentialClientApplication = None

    def _create_flask_server_manager():
        """
        Private method that initialise all required server side variables.
        """
        FlaskServerManager._server = flask.Flask(__name__)
        FlaskServerManager._server.config.update(
            SECRET_KEY=get_flask_server_manager_key(),  # TODO: Replace with custom unique server key (like long password).
            CLIENT_ID=get_sso_client_id(),  # TODO: Replace with Azure SSO client ID.
            CLIENT_SECRET=get_sso_client_secret_credential(),  # TODO: Replace with Azure SSO client secret credential.
            AUTHORITY=get_sso_authority(),  # TODO: Replace with Azure SSO authority.
            ENDPOINT=get_sso_graph_endpoint(),  # TODO: Replace with Azure SSO graph endpoint.
            SCOPE=get_sso_scope(),  # TODO: Replace with Azure SSO scope.
        )

        FlaskServerManager._sso_auth = msal.ConfidentialClientApplication(
            client_id=get_sso_client_id(),  # TODO: Replace with Azure SSO client ID.
            client_credential=get_sso_client_secret_credential(),  # TODO: Replace with Azure SSO client secret credential.
            authority=get_sso_authority(),  # TODO: Replace with Azure SSO authority.
        )

        FlaskServerManager._login_manager = flask_login.LoginManager()
        FlaskServerManager._login_manager.init_app(
            FlaskServerManager._server,
        )
        FlaskServerManager._login_manager.login_view = "/login"

    def _check_and_create_server_manager() -> None:
        """
        Private method that checks and ensures all required server side variables have been initialised.
        """
        if (
            FlaskServerManager._server is None
            or FlaskServerManager._login_manager is None
            or FlaskServerManager._sso_auth is None
        ):
            FlaskServerManager._create_flask_server_manager()

    def get_server_instance() -> flask.Flask:
        """
        Returns the Flask server instance.
        """
        FlaskServerManager._check_and_create_server_manager()
        return FlaskServerManager._server

    def get_login_manager_instance() -> flask_login.LoginManager:
        """
        Returns the login manager instance.
        """
        FlaskServerManager._check_and_create_server_manager()
        return FlaskServerManager._login_manager

    def get_sso_auth_instance() -> msal.ConfidentialClientApplication:
        """
        Returns the Single Sign-On (SSO) authentication object.
        """
        FlaskServerManager._check_and_create_server_manager()
        return FlaskServerManager._sso_auth


class User(flask_login.UserMixin):
    """
    Class with data model that has to have at least `self.id` at minimum.
    """

    def __init__(self, user_email):
        self.id = user_email


@FlaskServerManager.get_login_manager_instance().user_loader
def load_user(user_email):
    return User(user_email)
