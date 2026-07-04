\
import os, json, sqlite3
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from ruamel.yaml import YAML
import typer
from openai import OpenAI

app=typer.Typer(help="MetaForge MVP")

load_dotenv()
OUT=Path(os.getenv("OUTPUT_DIR","generated")); OUT.mkdir(exist_ok=True)
DB_DIR=Path("db"); DB_DIR.mkdir(exist_ok=True)
logger.add(OUT/"meta-forge.log")

yaml=YAML()

def _schema_ddl(entities: list) -> str:
    lines=[]
    for e in entities:
        lines.append(f"-- Entity: {e['name']}")
        lines.append(f"CREATE TABLE {e['table']} (id INTEGER PRIMARY KEY);")
    return "\n".join(lines)

def load_model():
    return yaml.load(Path("examples/manufacturing.yaml"))

@app.command()
def validate():
    m=load_model()
    typer.echo(f"Loaded {len(m['entities'])} entities.")
    logger.info("Validation successful")

@app.command()
def generate():
    m=load_model()
    project=m.get("project","meta-forge")
    ddl=_schema_ddl(m["entities"])

    ddl_path=OUT/f"{project}-ddl.sql"
    ddl_path.write_text(ddl)
    logger.info(f"Schema written to {ddl_path}")

    client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                  base_url=os.getenv("OPENAI_BASE_URL"))
    prompt=(
        f"Given this SQL DDL schema:\n\n{ddl}\n\n"
        f"Generate INSERT statements to seed each table with realistic sample data. "
        f"Output ONLY valid SQL — no markdown, no explanations, no code fences."
    )
    try:
        r=client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=[{"role":"user","content":prompt}]
        )
        sql=r.choices[0].message.content.strip()
        sql=_clean_sql(sql)
    except Exception as ex:
        sql=f"-- LLM unavailable\n-- {ex}"
    seed_path=OUT/f"{project}-insert.sql"
    seed_path.write_text(sql)
    logger.info(f"Seed written to {seed_path}")
    openapi_path = OUT / f"{project}-openapi.json"
    openapi_path.write_text(json.dumps(_build_openapi_spec(m), indent=2))
    logger.info(f"OpenAPI spec written to {openapi_path}")

    typer.echo(f"Generated {ddl_path.name}, {seed_path.name}, and {openapi_path.name}")

def _build_openapi_spec(model: dict) -> dict:
    """Build an OpenAPI 3.0 spec from the model definition."""
    project = model.get("project", "meta-forge")
    entities = model["entities"]

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": f"{project} REST API",
            "description": f"Auto-generated API for {project}",
            "version": "1.0.0",
        },
        "servers": [{"url": "http://127.0.0.1:8000", "description": "Local dev"}],
        "paths": {},
        "components": {"schemas": {}},
    }

    for entity in entities:
        name = entity["name"]
        props = {"id": {"type": "integer", "description": "Primary key"}}

        rels = entity.get("relationships", {})
        rel_desc = [
            f"{rn}: {rv['type']} -> {rv['entity']}"
            for rn, rv in rels.items()
        ]
        schema = {"type": "object", "properties": props}
        if rel_desc:
            schema["description"] = "Relationships: " + "; ".join(rel_desc)

        spec["components"]["schemas"][name] = schema

        spec["paths"][f"/{name}/"] = {
            "get": {
                "summary": f"List all {name}",
                "operationId": f"list_{name.lower()}",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": f"#/components/schemas/{name}"},
                                }
                            }
                        },
                    }
                },
            }
        }

        spec["paths"][f"/{name}/{{id}}"] = {
            "get": {
                "summary": f"Get {name} by ID",
                "operationId": f"get_{name.lower()}",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{name}"}
                            }
                        },
                    },
                    "404": {"description": "Not found"},
                },
            }
        }

    return spec


def _clean_sql(sql: str) -> str:
    """Strip markdown code fences if the LLM ignores instructions."""
    if sql.startswith("```"):
        lines=sql.splitlines()
        cleaned=[l for l in lines if not l.strip().startswith("```")]
        return "\n".join(cleaned).strip()
    return sql

@app.command()
def deploy():
    m=load_model()
    project=m.get("project","meta-forge")
    ddl_path=OUT/f"{project}-ddl.sql"
    seed_path=OUT/f"{project}-insert.sql"
    db_path=DB_DIR/f"{project}.db"
    deploy_log=OUT/f"{project}-mf-deploy.log"
    logger.add(deploy_log)

    if not ddl_path.exists():
        logger.error(f"Schema file not found: {ddl_path}")
        typer.echo(f"Error: run 'generate' first — {ddl_path.name} missing", err=True)
        raise typer.Exit(1)
    if not seed_path.exists():
        logger.error(f"Seed file not found: {seed_path}")
        typer.echo(f"Error: run 'generate' first — {seed_path.name} missing", err=True)
        raise typer.Exit(1)

    conn=sqlite3.connect(str(db_path))
    try:
        conn.executescript(ddl_path.read_text())
        logger.info(f"Schema deployed from {ddl_path.name}")

        conn.executescript(seed_path.read_text())
        logger.info(f"Seed data imported from {seed_path.name}")

        conn.commit()
        typer.echo(f"Deployed {db_path}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Deploy failed: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        conn.close()

@app.command()
def serve_rest(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address"),
    port: int = typer.Option(8000, "--port", help="Listen port"),
):
    """Start a FastAPI REST server exposing GET endpoints for each entity."""
    from fastapi import FastAPI, HTTPException
    import uvicorn

    m = load_model()
    project = m.get("project", "meta-forge")
    db_path = DB_DIR / f"{project}.db"

    if not db_path.exists():
        msg = f"Database not found at {db_path}. Run 'deploy' first."
        typer.echo(f"Error: {msg}", err=True)
        raise typer.Exit(1)

    static_spec_path = OUT / f"{project}-openapi.json"

    rest_app = FastAPI(title=f"{project} REST API")

    def _make_list(entity_name: str, table: str):
        async def list_all():
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(f"SELECT * FROM \"{table}\"").fetchall()
                return [dict(r) for r in rows]
            except sqlite3.OperationalError as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                conn.close()

        list_all.__name__ = f"list_{entity_name.lower()}"
        return list_all

    def _make_get(entity_name: str, table: str):
        async def get_one(record_id: int):
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    f"SELECT * FROM \"{table}\" WHERE id = ?", (record_id,)
                ).fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=404, detail=f"{entity_name} #{record_id} not found"
                    )
                return dict(row)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                conn.close()

        get_one.__name__ = f"get_{entity_name.lower()}"
        return get_one

    for entity in m["entities"]:
        name = entity["name"]
        table = entity["table"]
        rest_app.add_api_route(
            f"/{name}/", _make_list(name, table), methods=["GET"]
        )
        rest_app.add_api_route(
            f"/{name}/{{record_id}}", _make_get(name, table), methods=["GET"]
        )

    @rest_app.get("/openapi/generated.json", include_in_schema=False)
    async def get_generated_openapi():
        if static_spec_path.exists():
            return json.loads(static_spec_path.read_text())
        return {"detail": "Run 'generate' first to produce the spec file"}

    typer.echo(f"REST API starting at http://{host}:{port}")
    typer.echo(f"Endpoints: {[e['name'] for e in m['entities']]}")
    uvicorn.run(rest_app, host=host, port=port)


if __name__=="__main__":
    app()
