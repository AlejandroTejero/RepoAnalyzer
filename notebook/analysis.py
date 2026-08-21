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

    return active_authors_per_week, alt, commits_per_week, load_commits_df, mo


@app.cell
def _(mo):
    mo.md("""
    # Repo Analyzer — WebBuilder-TFG
    """)
    return


@app.cell
def _(load_commits_df):
    df = load_commits_df()
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
def _():
    from metrics.dependencies import load_dependencies_df, dependency_freshness, outdated_ranking

    return dependency_freshness, load_dependencies_df, outdated_ranking


@app.cell
def _(dependency_freshness, load_dependencies_df, outdated_ranking):
    deps_df = load_dependencies_df()
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


if __name__ == "__main__":
    app.run()
