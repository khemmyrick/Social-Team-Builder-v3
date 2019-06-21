from django.contrib import messages


def identify(request, target_user):
    """Check if current user has permission to access a view.
    If not, redirect to home view.
    """
    if request.user != target_user:
        messages.error(
            request,
            "You are not allowed to do that."
        )
        return True
    else:
        False
