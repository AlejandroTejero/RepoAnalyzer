# Repo Analyzer

Herramienta de analítica de repositorios de software: analiza actividad, dependencias y bus factor de **cualquier repositorio de GitHub**, con visualización interactiva en Altair y Marimo.


## Qué hace

- **Actividad**: extrae el histórico de commits de un repositorio y calcula commits por semana y número de autores activos en el tiempo.
- **Dependencias**: lee el `requirements.txt` del repositorio y compara cada dependencia contra la última versión disponible en PyPI, clasificando el desfase (major/minor/patch).
- **Bus factor**: calcula qué porcentaje de los commits aporta cada autor y el número mínimo de personas de las que depende más del 50% del conocimiento del proyecto, además de su evolución mensual.

Todo se explora de forma interactiva en un notebook Marimo con un selector de repositorio, ya que la base de datos puede acumular varios proyectos analizados a la vez.

## Stack técnico

- **Python** — lenguaje base de todo el proyecto
- **PyGithub** — extracción de datos desde la API de GitHub (commits, contenido de ficheros)
- **PostgreSQL** + **SQLAlchemy** — almacenamiento persistente de commits, autores, repos y dependencias
- **Pandas** — procesamiento y cálculo de métricas
- **Altair** — visualización declarativa de los resultados
- **Marimo** — notebook reactivo para la exploración interactiva de los datos
- **PyPI API** — consulta de versiones y fechas de publicación de dependencias

## Arquitectura

```
GitHub API / PyPI API
        │
        ▼
   extractor/          ← extrae commits y dependencias
        │
        ▼
   database/            ← PostgreSQL, vía SQLAlchemy (modelos: Repo, Author, Commit, Dependency)
        │
        ▼
   metrics/              ← calcula actividad, frescura de dependencias y bus factor con Pandas
        │
        ▼
   notebook/analysis.py  ← Marimo + Altair, selector de repositorio, todo reactivo
```


## Cómo se usa

**1. Clona el repositorio e instala dependencias**
```bash
git clone https://github.com/AlejandroTejero/RepoAnalyzer.git
cd RepoAnalyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configura las variables de entorno**

Copia `.env.example` a `.env` y rellena:
```
GITHUB_TOKEN=tu_token_de_github
DATABASE_URL=postgresql://usuario:password@localhost:5432/repo_analyzer
```

**3. Crea las tablas en PostgreSQL**
```bash
python3 -c "from database.db import init_db; init_db()"
```

**4. Extrae datos de un repositorio (cualquiera)**
```bash
python3 -m extractor.github_extractor <owner> <repo>
python3 -m extractor.dependency_extractor <owner> <repo>
```

Ejemplo:
```bash
python3 -m extractor.github_extractor encode httpx
python3 -m extractor.dependency_extractor encode httpx
```

**5. Abre el notebook interactivo**
```bash
marimo edit notebook/analysis.py
```

Abre la URL que se muestre en la terminal, y selecciona el repositorio a analizar desde el desplegable.