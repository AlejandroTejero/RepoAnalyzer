import pandas as pd
from packaging.version import Version, InvalidVersion

from database.db import get_session
from database.models import Dependency


def load_dependencies_df(repo_id=None):
    """
    Carga las dependencias de la base de datos en un DataFrame de Pandas.
    Si se pasa repo_id, filtra solo las de ese repo.
    """
    session = get_session()
    query = session.query(Dependency)
    if repo_id is not None:
        query = query.filter(Dependency.repo_id == repo_id)

    deps = query.all()

    data = [
        {
            "name": d.name,
            "pinned_version": d.pinned_version,
            "latest_version": d.latest_version,
            "latest_release_date": d.latest_release_date,
        }
        for d in deps
    ]

    session.close()
    return pd.DataFrame(data)


def _extraer_numero_version(texto_version):
    """
    De un texto tipo '>=5.1' o '==2.31.0' extrae solo el número (5.1, 2.31.0),
    quitando el operador. Devuelve None si no se puede interpretar.
    """
    if not texto_version:
        return None

    numero = texto_version.lstrip("=><~")
    try:
        return Version(numero)
    except InvalidVersion:
        return None


def dependency_freshness(df):
    """
    Para cada dependencia, calcula si la versión mínima que exige el proyecto
    va por detrás de la última disponible en PyPI, y en qué medida
    (major, minor o patch de diferencia).
    Devuelve el DataFrame original con columnas nuevas: outdated, diferencia.
    """
    df = df.copy()

    def calcular_diferencia(fila):
        actual = _extraer_numero_version(fila["pinned_version"])
        ultima = _extraer_numero_version(fila["latest_version"])

        if actual is None or ultima is None:
            return pd.Series({"outdated": None, "diferencia": None})

        if actual >= ultima:
            return pd.Series({"outdated": False, "diferencia": "al día"})

        if actual.major != ultima.major:
            return pd.Series({"outdated": True, "diferencia": "major"})
        elif actual.minor != ultima.minor:
            return pd.Series({"outdated": True, "diferencia": "minor"})
        else:
            return pd.Series({"outdated": True, "diferencia": "patch"})

    resultado = df.apply(calcular_diferencia, axis=1)
    return pd.concat([df, resultado], axis=1)


def outdated_ranking(df):
    """
    Ordena las dependencias, mostrando primero las más desactualizadas
    (diferencia 'major' antes que 'minor', antes que 'patch').
    """
    orden_gravedad = {"major": 0, "minor": 1, "patch": 2, "al día": 3}
    df = df.copy()
    df["orden"] = df["diferencia"].map(orden_gravedad)
    return df.sort_values("orden").drop(columns="orden")


if __name__ == "__main__":
    df = load_dependencies_df()
    print("Total dependencias cargadas:", len(df))

    con_frescura = dependency_freshness(df)
    ranking = outdated_ranking(con_frescura)

    print("\nRanking de dependencias (más desactualizadas primero):")
    print(
        ranking[["name", "pinned_version", "latest_version", "diferencia"]]
        .to_string(index=False)
    )