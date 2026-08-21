import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import sys
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    import marimo as mo
    import altair as alt
    from metrics.activity import load_commits_df, commits_per_week, active_authors_per_week
    from metrics.dependencies import load_dependencies_df, dependency_freshness, outdated_ranking
    from metrics.bus_factor import load_commits_with_authors_df, contribution_share, bus_factor_over_time
    from database.db import get_session
    from database.models import Repo

    return (
        Repo,
        active_authors_per_week,
        alt,
        bus_factor_over_time,
        commits_per_week,
        contribution_share,
        dependency_freshness,
        get_session,
        load_commits_df,
        load_commits_with_authors_df,
        load_dependencies_df,
        mo,
        outdated_ranking,
    )


@app.cell
def _(Repo, get_session, mo):
    session = get_session()
    repos_disponibles = session.query(Repo).all()
    opciones = {r.name: r.id for r in repos_disponibles}
    session.close()

    selector_repo = mo.ui.dropdown(
        options=opciones,
        value=list(opciones.keys())[0],
        label="Repositorio a analizar",
    )
    selector_repo
    return (selector_repo,)


@app.cell
def _(mo):
    mo.md("""
    # Repo Analyzer
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Actividad
    """)
    return


@app.cell
def _(load_commits_df, selector_repo):
    df = load_commits_df(repo_id=selector_repo.value)
    df
    return (df,)


@app.cell
def _(commits_per_week, df):
    semanal = commits_per_week(df)
    semanal
    return (semanal,)


@app.cell
def _(active_authors_per_week, df):
    activos = active_authors_per_week(df)
    activos
    return (activos,)


@app.cell
def _(alt, semanal):
    chart_commits = (
        alt.Chart(semanal)
        .mark_bar()
        .encode(
            x=alt.X("week:T", title="Semana"),
            y=alt.Y("num_commits:Q", title="Commits"),
            tooltip=["week:T", "num_commits:Q"],
        )
        .properties(title="Commits por semana", width=600)
    )
    chart_commits
    return


@app.cell
def _(activos, alt):
    chart_autores = (
        alt.Chart(activos)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:T", title="Semana"),
            y=alt.Y("autores_activos:Q", title="Autores activos"),
            tooltip=["week:T", "autores_activos:Q"],
        )
        .properties(title="Autores activos por semana", width=600)
    )
    chart_autores
    return


@app.cell
def _(mo):
    mo.md("""
    ## Dependencias
    """)
    return


@app.cell
def _(
    dependency_freshness,
    load_dependencies_df,
    outdated_ranking,
    selector_repo,
):
    deps_df = load_dependencies_df(repo_id=selector_repo.value)
    deps_con_frescura = dependency_freshness(deps_df)
    ranking = outdated_ranking(deps_con_frescura)
    ranking[["name", "pinned_version", "latest_version", "diferencia"]]
    return (deps_con_frescura,)


@app.cell
def _(alt, deps_con_frescura):
    chart_deps = (
        alt.Chart(deps_con_frescura)
        .mark_bar()
        .encode(
            x=alt.X("name:N", title="Dependencia", sort="-y"),
            y=alt.Y("diferencia:N", title="Estado"),
            color=alt.Color(
                "diferencia:N",
                scale=alt.Scale(
                    domain=["major", "minor", "patch", "al día"],
                    range=["#d62728", "#ff7f0e", "#ffdd57", "#2ca02c"],
                ),
                legend=alt.Legend(title="Gravedad"),
            ),
            tooltip=["name:N", "pinned_version:N", "latest_version:N", "diferencia:N"],
        )
        .properties(title="Estado de las dependencias", width=600)
    )
    chart_deps
    return


@app.cell
def _(mo):
    mo.md("""
    ## Bus Factor
    """)
    return


@app.cell
def _(contribution_share, load_commits_with_authors_df, selector_repo):
    autores_df = load_commits_with_authors_df(repo_id=selector_repo.value)
    aportacion = contribution_share(autores_df)
    aportacion
    return aportacion, autores_df


@app.cell
def _(alt, aportacion):
    chart_aportacion = (
        alt.Chart(aportacion)
        .mark_bar()
        .encode(
            x=alt.X("author_name:N", title="Autor", sort="-y"),
            y=alt.Y("porcentaje:Q", title="% de commits"),
            tooltip=["author_name:N", "num_commits:Q", "porcentaje:Q"],
        )
        .properties(title="Aportación por autor", width=600)
    )

    texto = chart_aportacion.mark_text(dy=-10).encode(text="porcentaje:Q")

    chart_final = chart_aportacion + texto
    chart_final
    return


@app.cell
def _(autores_df, bus_factor_over_time):
    evolucion_bf = bus_factor_over_time(autores_df)
    return (evolucion_bf,)


@app.cell
def _(alt, evolucion_bf):
    chart_bus_factor = (
        alt.Chart(evolucion_bf)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:T", title="Mes"),
            y=alt.Y("bus_factor:Q", title="Bus factor"),
            tooltip=["month:T", "bus_factor:Q"],
        )
        .properties(title="Evolución del bus factor", width=600)
    )
    chart_bus_factor
    return


if __name__ == "__main__":
    app.run()
