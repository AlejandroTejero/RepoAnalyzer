import pandas as pd

from database.db import get_session
from database.models import Commit, Author


def load_commits_df(repo_id=None):
    """
    Carga los commits de la base de datos en un DataFrame de Pandas.
    Si se pasa repo_id, filtra solo los de ese repo.
    """
    session = get_session()
    query = session.query(Commit)
    if repo_id is not None:
        query = query.filter(Commit.repo_id == repo_id)

    commits = query.all()

    data = [
        {
            "hash": c.hash,
            "date": c.date,
            "author_id": c.author_id,
            "repo_id": c.repo_id,
        }
        for c in commits
    ]

    session.close()
    return pd.DataFrame(data)


def commits_per_week(df):
    """
    Agrupa los commits por semana y cuenta cuántos hay en cada una.
    Devuelve un DataFrame con columnas: semana, num_commits.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W").apply(lambda p: p.start_time)

    resultado = df.groupby("week").size().reset_index(name="num_commits")
    return resultado.sort_values("week")


def active_authors_per_week(df):
    """
    Para cada semana, cuenta cuántos autores distintos hicieron al menos un commit.
    Devuelve un DataFrame con columnas: semana, autores_activos.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W").apply(lambda p: p.start_time)

    resultado = (
        df.groupby("week")["author_id"]
        .nunique()
        .reset_index(name="autores_activos")
    )
    return resultado.sort_values("week")


if __name__ == "__main__":
    df = load_commits_df()
    print("Total commits cargados:", len(df))

    semanal = commits_per_week(df)
    print("\nCommits por semana:")
    print(semanal.to_string(index=False))

    activos = active_authors_per_week(df)
    print("\nAutores activos por semana:")
    print(activos.to_string(index=False))