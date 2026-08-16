import hashlib
import hmac
import json
import logging
import os
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError


logger = logging.getLogger(__name__)


class DeploymentConfigurationError(RuntimeError):
    """Raised when the PythonAnywhere deployment environment is incomplete."""


def _valid_github_signature(body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature.startswith("sha256="):
        return False

    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    return hmac.compare_digest(expected, signature)


def _repository_path() -> Path:
    return Path(os.getenv("DEPLOY_REPOSITORY_PATH", settings.BASE_DIR)).resolve()


def _wsgi_file_path() -> Path:
    explicit_path = os.getenv("PYTHONANYWHERE_WSGI_FILE")
    if explicit_path:
        return Path(explicit_path)

    username = os.getenv("PYTHONANYWHERE_USERNAME")
    if username:
        return Path(f"/var/www/{username}_pythonanywhere_com_wsgi.py")

    raise DeploymentConfigurationError(
        "Configure PYTHONANYWHERE_USERNAME or PYTHONANYWHERE_WSGI_FILE."
    )


def _pull_main_branch() -> str:
    repo = Repo(_repository_path())

    # Nunca sobrescreve alterações locais rastreadas no servidor.
    if repo.is_dirty(untracked_files=False):
        raise GitCommandError(
            "deploy",
            1,
            stderr="The deployment checkout contains tracked local changes.",
        )

    origin = repo.remote("origin")
    origin.fetch("main")

    if repo.head.is_detached or repo.active_branch.name != "main":
        repo.git.checkout("main")

    # Apenas fast-forward: um histórico divergente deve ser corrigido manualmente.
    repo.git.merge("--ff-only", "origin/main")
    return repo.head.commit.hexsha


def _reload_pythonanywhere() -> None:
    # O PythonAnywhere documenta o touch do arquivo WSGI como forma de reload.
    _wsgi_file_path().touch()


@require_GET
def hello_world(request):
    return render(request, "hello_world.html")


@csrf_exempt
@require_POST
def update_server(request):
    """Receive a signed GitHub webhook and deploy only pushes to main."""

    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not _valid_github_signature(request.body, signature, secret):
        return JsonResponse({"detail": "Invalid webhook signature."}, status=403)

    event = request.headers.get("X-GitHub-Event", "")
    if event == "ping":
        return JsonResponse({"detail": "Webhook configured successfully."})

    if event != "push":
        return JsonResponse(
            {"detail": "Event ignored.", "event": event},
            status=202,
        )

    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON payload."}, status=400)

    if payload.get("ref") != "refs/heads/main":
        return JsonResponse(
            {"detail": "Push ignored because it is not from main."},
            status=202,
        )

    try:
        commit_sha = _pull_main_branch()
        _reload_pythonanywhere()
    except DeploymentConfigurationError:
        logger.exception("PythonAnywhere deployment is not configured.")
        return JsonResponse(
            {"detail": "Deployment environment is not configured."},
            status=503,
        )
    except (GitCommandError, InvalidGitRepositoryError, NoSuchPathError):
        logger.exception("Git deployment failed.")
        return JsonResponse({"detail": "Deployment failed."}, status=500)
    except OSError:
        logger.exception("PythonAnywhere reload failed.")
        return JsonResponse({"detail": "Deployment reload failed."}, status=500)

    return JsonResponse(
        {
            "detail": "Deployment updated successfully.",
            "commit": commit_sha,
        }
    )
