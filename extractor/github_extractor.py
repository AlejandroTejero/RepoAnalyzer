import os
from datetime import datetime, timezone
from github import Github
from dotenv import load_dotenv

from database.db import get_session
from database.models import Repo, Author, Commit

from github import Auth

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_or_create_repo(session, name, url):
    """Busca el repo en la BD; si no existe, lo crea."""
    repo = session.query(Repo).filter_by(url=url).first()
    if repo is None:
        repo = Repo(name=name, url=url)
        session.add(repo)
        session.commit()
    return repo


def get_or_create_author(session, name, email):
    """Busca el autor en la BD; si no existe, lo crea."""
    author = session.query(Author).filter_by(email=email).first()
    if author is None:
        author = Author(name=name, email=email)
        session.add(author)
        session.commit()
    return author


def extract_commits(repo_owner, repo_name):
    """
    Conecta con GitHub, recorre los commits de un repo,
    y los guarda en la base de datos si no existen ya.
    """
    gh = Github(auth=Auth.Token(GITHUB_TOKEN))
    gh_repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    session = get_session()
    db_repo = get_or_create_repo(
        session, name=repo_name, url=gh_repo.html_url
    )

    nuevos = 0
    for gh_commit in gh_repo.get_commits():
        existe = session.query(Commit).filter_by(hash=gh_commit.sha).first()
        if existe:
            continue

        commit_author = gh_commit.commit.author
        author = get_or_create_author(
            session,
            name=commit_author.name,
            email=commit_author.email,
        )

        nuevo_commit = Commit(
            hash=gh_commit.sha,
            message=gh_commit.commit.message,
            date=commit_author.date.astimezone(timezone.utc).replace(tzinfo=None),
            repo_id=db_repo.id,
            author_id=author.id,
        )
        session.add(nuevo_commit)
        nuevos += 1

    session.commit()
    session.close()
    print(f"Listo. {nuevos} commits nuevos guardados de {repo_owner}/{repo_name}.")


if __name__ == "__main__":
    extract_commits("AlejandroTejero", "WebBuilder-TFG")