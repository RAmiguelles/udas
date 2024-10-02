from rest_framework.authtoken.models import Token


def CHECK_TOKEN(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        key = request.META['HTTP_AUTHORIZATION'][6:]
        token = Token.objects.filter(key=key)
        if not token:
            return {"detail": "Invalid token."}
    else:
        return {"detail": "Authentication credentials were not provided."}
