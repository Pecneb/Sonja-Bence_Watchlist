import functools
import solara
from solara_enterprise import auth
from typing import Optional, Dict


def get_login_url(return_to_path: Optional[str] = None) -> str:
    """
    Generate the login URL for OAuth authentication.

    Args:
        return_to_path (Optional[str]): The path to redirect to after login.

    Returns:
        str: The login URL.
    """
    return auth.get_login_url(return_to_path)


def get_logout_url(return_to_path: Optional[str] = None) -> str:
    """
    Generate the logout URL for OAuth authentication.

    Args:
        return_to_path (Optional[str]): The path to redirect to after logout.

    Returns:
        str: The logout URL.
    """
    return auth.get_logout_url(return_to_path)


def get_current_user() -> Optional[Dict]:
    """
    Retrieve the currently authenticated user.

    Returns:
        Optional[auth.User]: The current user object or None if not authenticated.
    """
    return auth.user.value


@solara.component
def LoginButton():
    solara.Button("Login", icon_name="mdi-login", href=get_login_url(), text=True)


@solara.component
def LogOutButton():
    solara.Button("Logout", icon_name="mdi-logout", href=get_logout_url(), text=True)


@solara.component
def AuthAvatarMenu():
    """
    Display the user's avatar with a dropdown menu for logout.
    """
    if auth.user.value:
        with auth.AvatarMenu():
            LogOutButton()
    else:
        LoginButton()


def with_authentication(func):
    """
    Wrapper function to enforce authentication for pages and components.

    Args:
        func (Callable): The page or component to wrap.

    Returns:
        Callable: The wrapped component that enforces authentication.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            # Redirect to login page if the user is not authenticated
            return solara.Link(get_login_url())
        # Render the original component if authenticated
        return func(*args, **kwargs)

    return wrapper
