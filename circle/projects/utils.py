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


def show_messages(request):
    """Display stored user messages."""
    if request.user.is_authenticated and request.user.notifications:
        messages.info(
            request,
            request.user.notifications
        )
        request.user.notifications = ''
        request.user.save()
        return
