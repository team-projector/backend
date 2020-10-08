import functools

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.tasks import add_action_task


def gitlab_api_call(func):
    """Decorator for log gitlab api calls."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # noqa: WPS430
        func_result = func(*args, **kwargs)
        add_action_task.delay(verb=ACTION_GITLAB_CALL_API)

        return func_result  # noqa: WPS331

    return wrapper
