import json
from base64 import urlsafe_b64decode
from os import environ

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import redirect, render
import requests
from django.urls import reverse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


if environ.get('OAUTH_URL', False):
    def oauth(request: HttpRequest) -> HttpResponse:
        redirect_uri = f'{settings.SITE_SCHEMA}%3A%2F%2F{settings.SITE_URL}:{settings.SITE_PORT}{reverse("base:oauth_redirect")}'
        return redirect(
            f'{settings.OAUTH_URL}?'
            f'client_id={settings.OAUTH_CLIENT_ID}'
            f'&redirect_uri={redirect_uri}'
            f'&response_type=code'
            f'&scope=openid+profile'
        )


    def oauth_redirect(request: HttpRequest) -> HttpResponse:
        if 'code' not in request.GET:
            return HttpResponseBadRequest()

        auth_resp = requests.post(
            "https://keycloak.general.pve2.secshell.net/realms/main/protocol/openid-connect/token", data={
                "client_id": settings.OAUTH_CLIENT_ID,
                "client_secret": settings.OAUTH_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": request.GET['code'],
                "redirect_uri": f"{settings.SITE_SCHEMA}://{settings.SITE_URL}:{settings.SITE_PORT}{reverse('base:oauth_redirect')}",
                "scope": "identify",
            }, headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )

        if not auth_resp.ok:
            return HttpResponseBadRequest()

        if not (access_token := auth_resp.json().get('access_token')) or len(access_token.split(".")) <= 1:
            return HttpResponseBadRequest()

        user_info_encoded = access_token.split(".")[1]
        user_info = json.loads(urlsafe_b64decode(user_info_encoded + '=' * (4 - (len(user_info_encoded) % 4))).decode())

        user, _ = User.objects.get_or_create(
            username=user_info.get('preferred_username'),
            first_name=user_info.get('given_name'),
            last_name=user_info.get('family_name'),
            email=user_info.get('email'),
        )

        login(request, user, backend="oauth2_provider.backends.OAuth2Backend")

        return redirect(settings.LOGIN_REDIRECT_URL)
