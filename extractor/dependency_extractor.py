import sys

import re
from datetime import datetime, timezone

import requests
from github import Github, Auth

from database.db import get_session
from database.models import Repo, Dependency
from extractor.github_extractor import GITHUB_TOKEN, get_or_create_repo


def parse_requirements(content):
    """
    Convierte el texto crudo de un requirements.txt en una lista de tuplas
    (nombre, version_declarada). Soporta ==, >=, <=, ~= y extras tipo [socialaccount].
    Si hay varias condiciones (ej. >=5.1,<6.0), se queda con la primera.
    Ignora comentarios y líneas vacías.
    """
    dependencias = []
    for linea in content.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue

        match = re.match(
            r"^([A-Za-z0-9_.\-]+)(\[[A-Za-z0-9_,\-]+\])?\s*(==|>=|<=|~=)\s*([A-Za-z0-9_.\-]+)",
            linea,
        )
        if match:
            nombre = match.group(1)
            operador = match.group(3)
            version = match.group(4)
            dependencias.append((nombre, f"{operador}{version}"))

    return dependencias

def get_pypi_info(package_name):
    """
    Consulta la API de PyPI para un paquete y devuelve
    (ultima_version, fecha_publicacion) de esa última versión.
    Si el paquete no existe en PyPI o falla la consulta, devuelve (None, None).
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None, None

    data = response.json()
    latest_version = data["info"]["version"]

    releases = data["releases"].get(latest_version, [])
    if not releases:
        return latest_version, None

    fecha_str = releases[0]["upload_time_iso_8601"]
    fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
    fecha = fecha.astimezone(timezone.utc).replace(tzinfo=None)

    return latest_version, fecha


def extract_dependencies(repo_owner, repo_name):
    """
    Lee el requirements.txt de un repo de GitHub, consulta PyPI
    para cada dependencia, y guarda/actualiza los resultados en la BD.
    """
    gh = Github(auth=Auth.Token(GITHUB_TOKEN))
    gh_repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    contenido_file = gh_repo.get_contents("requirements.txt")
    contenido = contenido_file.decoded_content.decode("utf-8")

    dependencias = parse_requirements(contenido)

    session = get_session()
    db_repo = get_or_create_repo(session, name=repo_name, url=gh_repo.html_url)

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)

    for nombre, version_fijada in dependencias:
        latest_version, latest_date = get_pypi_info(nombre)

        existente = (
            session.query(Dependency)
            .filter_by(repo_id=db_repo.id, name=nombre)
            .first()
        )

        if existente:
            existente.pinned_version = version_fijada
            existente.latest_version = latest_version
            existente.latest_release_date = latest_date
            existente.checked_at = ahora
        else:
            nueva = Dependency(
                name=nombre,
                pinned_version=version_fijada,
                latest_version=latest_version,
                latest_release_date=latest_date,
                checked_at=ahora,
                repo_id=db_repo.id,
            )
            session.add(nueva)

    session.commit()
    session.close()
    print(f"Listo. {len(dependencias)} dependencias procesadas de {repo_owner}/{repo_name}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 -m extractor.dependency_extractor <owner> <repo>")
        sys.exit(1)

    repo_owner = sys.argv[1]
    repo_name = sys.argv[2]
    extract_dependencies(repo_owner, repo_name)