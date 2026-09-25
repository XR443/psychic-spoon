import pytest
from django.urls import reverse
from .models import User


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def url(self):
        return "/greet/"

    def test_get_renders_form(self, client, url):
        response = client.get(url)
        assert response.status_code == 200
        assert "index.html" in [t.name for t in response.templates]
        assert response.context["user"] is None
        assert response.context["error"] is None

    def test_post_valid_creates_user(self, client, url):
        response = client.post(url, {"name": "Иван"})

        assert response.status_code == 200
        assert User.objects.count() == 1

        user = User.objects.get()
        assert user.name == "Иван"
        assert response.context["user"] == user
        assert response.context["error"] is None

    def test_post_empty_shows_error(self, client, url):
        response = client.post(url, {"name": ""})

        assert User.objects.count() == 0
        assert response.context["user"] is None
        assert response.context["error"] == "Пожалуйста, введите имя."

    def test_post_whitespace_shows_error(self, client, url):
        response = client.post(url, {"name": "   "})
        assert User.objects.count() == 0
        assert response.context["error"] is not None