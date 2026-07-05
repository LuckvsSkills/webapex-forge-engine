#!/usr/bin/env python3
"""
WebApex Forge Engine — Stap 4: Assemble
Combineert alle onderdelen tot een complete klant website structuur
"""

import json
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)

def laad_paden(paden_pad: str) -> dict:
    with open(paden_pad, 'r') as f:
        return {k: Path(v) for k, v in json.load(f).items()}

def kopieer_map(bron: Path, doel: Path, negeer: list = None) -> int:
    """Kopieert een map recursief, geeft aantal bestanden terug"""
    if negeer is None:
        negeer = ['.git', '__pycache__', '.env', 'node_modules']

    doel.mkdir(parents=True, exist_ok=True)
    teller = 0

    for item in bron.iterdir():
        if item.name in negeer:
            continue
        doel_item = doel / item.name
        if item.is_dir():
            teller += kopieer_map(item, doel_item, negeer)
        else:
            shutil.copy2(item, doel_item)
            teller += 1

    return teller

def maak_env_bestand(spec: dict, backend_dir: Path) -> bool:
    """Maakt .env bestand op basis van spec"""
    b = spec['bedrijf']
    slug = b['slug']

    env_voorbeeld = backend_dir / '.env.example'
    env_bestand   = backend_dir / '.env'

    if env_voorbeeld.exists():
        inhoud = env_voorbeeld.read_text()
    else:
        inhoud = ""

    vervangingen = {
        'postgresql://gebruiker:wachtwoord@localhost:5432/': f'postgresql://webapex:{slug}_db_pass@localhost:5432/',
        'webshop_db': f'{slug}_db',
        'booking_db': f'{slug}_db',
        'content_db': f'{slug}_db',
        'saas_db':    f'{slug}_db',
        'marketplace_db': f'{slug}_db',
        'community_db':   f'{slug}_db',
    }

    for oud, nieuw in vervangingen.items():
        inhoud = inhoud.replace(oud, nieuw)

    env_bestand.write_text(inhoud)
    print(f"  ✅ .env aangemaakt")
    return True

def maak_project_structuur(spec: dict, paden: dict, uitvoer_dir: Path) -> bool:
    print("\n🔧 WebApex Forge — Stap 4: Assembleren\n")

    slug = spec['bedrijf']['slug']
    project_dir = uitvoer_dir / f"client-{slug}"
    project_dir.mkdir(parents=True, exist_ok=True)

    # Frontend kopiëren
    if 'frontend' in paden:
        frontend_doel = project_dir / 'frontend'
        n = kopieer_map(paden['frontend'], frontend_doel)
        print(f"  ✅ Frontend gekopieerd ({n} bestanden)")

    # Backend kopiëren
    if 'backend' in paden:
        backend_doel = project_dir / 'backend'
        n = kopieer_map(paden['backend'], backend_doel)
        maak_env_bestand(spec, backend_doel)
        print(f"  ✅ Backend gekopieerd ({n} bestanden)")

    # Admin kopiëren
    if 'admin' in paden:
        admin_doel = project_dir / 'admin'
        n = kopieer_map(paden['admin'], admin_doel)
        print(f"  ✅ Admin gekopieerd ({n} bestanden)")

    # Agent kopiëren
    if 'agent' in paden and spec['agent']['actief']:
        agent_doel = project_dir / 'agent'
        n = kopieer_map(paden['agent'], agent_doel)
        print(f"  ✅ Agent gekopieerd ({n} bestanden)")

    # Spec opslaan in project
    spec_copy = project_dir / 'website_spec.json'
    with open(spec_copy, 'w') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    # Docker compose voor geheel project
    docker_compose = f"""version: '3.9'

services:
  frontend:
    image: nginx:alpine
    container_name: {slug}_frontend
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - {slug}_netwerk

  backend:
    build: ./backend
    container_name: {slug}_backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - database
    networks:
      - {slug}_netwerk

  database:
    image: postgres:15-alpine
    container_name: {slug}_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: {slug}_db
      POSTGRES_USER: webapex
      POSTGRES_PASSWORD: ${{DB_WACHTWOORD}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    networks:
      - {slug}_netwerk

  redis:
    image: redis:7-alpine
    container_name: {slug}_cache
    restart: unless-stopped
    networks:
      - {slug}_netwerk

volumes:
  postgres_data:

networks:
  {slug}_netwerk:
    driver: bridge
"""
    (project_dir / 'docker-compose.yml').write_text(docker_compose)

    # Nginx config
    nginx_conf = f"""server {{
    listen 80;
    server_name {spec['domein']['naam']} www.{spec['domein']['naam']};
    root /usr/share/nginx/html;
    index index.html;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    location /api/ {{
        proxy_pass http://{slug}_backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    location /admin/ {{
        alias /usr/share/nginx/html/admin/;
        try_files $uri $uri/ /admin/index.html;
    }}
}}
"""
    (project_dir / 'nginx.conf').write_text(nginx_conf)

    # README voor klant
    readme = f"""# {spec['bedrijf']['naam']} — Website

Gegenereerd door WebApex op {datetime.now().strftime('%d-%m-%Y %H:%M')}

## Structuur
- /frontend  — De website (HTML/CSS/JS)
- /backend   — De API server (FastAPI/Python)
- /admin     — Het beheer dashboard
- /agent     — AI assistent configuratie

## Starten
```bash
docker-compose up -d
```

## URLs
- Website:  http://{spec['domein']['naam']}
- Admin:    http://{spec['domein']['naam']}/admin
- API docs: http://{spec['domein']['naam']}/api/docs

## Support
support@webapex.nl
"""
    (project_dir / 'README.md').write_text(readme)

    print(f"\n✅ Project geassembleerd in: {project_dir}\n")
    return True, project_dir

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Gebruik: python3 assemble.py <spec.json> <paden.json> <uitvoer_dir>")
        sys.exit(1)

    spec   = laad_spec(sys.argv[1])
    paden  = laad_paden(sys.argv[2])
    uitvoer = Path(sys.argv[3])

    maak_project_structuur(spec, paden, uitvoer)
