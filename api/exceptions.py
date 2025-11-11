import traceback
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError, AuthenticationFailed, NotAuthenticated, PermissionDenied
)
from django.http import Http404
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from api.tasks import send_error_email_to_admin


def _extract_message(data):
    if isinstance(data, dict):
        if "detail" in data and isinstance(data["detail"], str):
            return data["detail"]

        if "messages" in data and isinstance(data["messages"], list) and data["messages"]:
            msg = data["messages"][0]
            if isinstance(msg, dict):
                if "message" in msg and isinstance(msg["message"], str):
                    return msg["message"]

        for v in data.values():
            if isinstance(v, str):
                return v

    if isinstance(data, list) and data and isinstance(data[0], str):
        return data[0]

    return str(data)


def custom_exception_handler(exc, context):
    request = context.get("request")
    url = request.build_absolute_uri() if request else "Unknown"
    user = (request.user.username
            if request and hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous")

    response = drf_exception_handler(exc, context)

    if response is not None:
        message = _extract_message(response.data)

        try:
            traceback_details = traceback.format_exc()
            send_error_email_to_admin.delay(
                url, user, type(exc).__name__, str(exc), traceback_details
            )
        except Exception:
            pass

        response.data = {
            "status": False,
            "message": message,
            "data": None,
        }
        return response

    try:
        traceback_details = traceback.format_exc()
        send_error_email_to_admin.delay(
            url, user, type(exc).__name__, str(exc), traceback_details
        )
    except Exception:
        pass

    return Response(
        {"status": False, "message": "Internal Server Error", "data": None},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
