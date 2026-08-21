import pandas as pd

from database.db import get_session
from database.models import Commit, Author


def load_commits_with_authors_df(repo_id=None):
    """
    Carga los commits junto con el nombre del autor (via join),
    en un DataFrame de Pandas.
    """
    session = get_session()
    query = session.query(Commit, Author).join(Author, Commit.author_id == Author.id)
    if repo_id is not None:
        query = query.filter(Commit.repo_id == repo_id)

    resultados = query.all()

    data = [
        {
            "hash": commit.hash,
            "date": commit.date,
            "author_name": author.name,
            "author_id": author.id,
        }
        for commit, author in resultados
    ]

    session.close()
    return pd.DataFrame(data)


def contribution_share(df):
    """
    Calcula qué % de los commits totales aporta cada autor.
    Devuelve un DataFrame ordenado de mayor a menor aportación,
    con columnas: author_name, num_commits, porcentaje.
    """
    total = len(df)
    conteo = df.groupby("author_name").size().reset_index(name="num_commits")
    conteo["porcentaje"] = (conteo["num_commits"] / total * 100).round(1)
    return conteo.sort_values("num_commits", ascending=False).reset_index(drop=True)


def calculate_bus_factor(df, umbral=0.5):
    """
    Calcula el bus factor: el número mínimo de autores cuya suma de commits
    alcanza el 'umbral' (por defecto 50%) del total.
    Un bus factor bajo (ej. 1 o 2) significa que el proyecto depende
    de muy poca gente.
    """
    share = contribution_share(df)
    total = share["num_commits"].sum()

    acumulado = 0
    contador = 0
    for _, fila in share.iterrows():
        acumulado += fila["num_commits"]
        contador += 1
        if acumulado / total >= umbral:
            break

    return contador


def bus_factor_over_time(df, umbral=0.5):
    """
    Calcula cómo ha evolucionado el bus factor a lo largo del tiempo,
    recalculándolo mes a mes usando solo los commits hasta esa fecha
    (una especie de "foto acumulada" de cada mes).
    Devuelve un DataFrame con columnas: mes, bus_factor.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").apply(lambda p: p.start_time)

    meses = sorted(df["month"].unique())
    resultados = []

    for mes in meses:
        subset = df[df["month"] <= mes]
        bf = calculate_bus_factor(subset, umbral=umbral)
        resultados.append({"month": mes, "bus_factor": bf})

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    df = load_commits_with_authors_df()
    print("Total commits cargados:", len(df))

    share = contribution_share(df)
    print("\nAportación por autor:")
    print(share.to_string(index=False))

    bf = calculate_bus_factor(df)
    print(f"\nBus factor actual: {bf}")

    evolucion = bus_factor_over_time(df)
    print("\nEvolución del bus factor por mes:")
    print(evolucion.to_string(index=False))