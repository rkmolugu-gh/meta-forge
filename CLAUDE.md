# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MetaForge is a CLI tool (Python/Typer) that reads a YAML model definition, generates SQL DDL schemas and LLM-produced seed data, then deploys to SQLite. It follows a **model → generate → deploy** pipeline.

## Commands

```bash
pip install -r requirements.txt
cp .env.example .env    # then edit .env with your OpenAI key

python meta_forge.py validate   # parse & validate the YAML model
python meta_forge.py generate   # generate DDL + seed INSERTs (uses OpenAI)
python meta_forge.py deploy     # apply generated SQL to a SQLite database
```

Outputs land in `generated/`; databases go in `db/`.

## Architecture

```
examples/manufacturing.yaml  ──►  meta-forge.py  ──►  generated/*.sql
                                     │                    db/*.db
                                     ▼
                                  .env (OPENAI_API_KEY, etc.)
```

- **`meta-forge.py`** — single-file CLI with 3 commands (`validate`, `generate`, `deploy`). Uses Typer for CLI, ruamel.yaml for parsing, OpenAI SDK for seed data generation, sqlite3 for deployment.
- **`examples/manufacturing.yaml`** — model definition with `project` name and `entities` list. Each entity has a name, table name, and optional relationships (one-to-one, one-to-many, many-to-many).
- **`generated/`** — all output files: `{project}-ddl.sql`, `{project}-insert.sql`, deploy logs, and app logs.
- **`db/`** — SQLite databases created by the `deploy` command.
- **`.env`** — required config: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OUTPUT_DIR`.

The `generate` command sends the DDL as context to OpenAI with a prompt to produce realistic INSERT statements. If the LLM call fails, it writes a fallback SQL comment instead.
