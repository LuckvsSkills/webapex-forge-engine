#!/usr/bin/env python3
"""
WebApex Forge Engine — Hoofdscript
Voert alle stappen uit in de juiste volgorde

Gebruik: python3 forge.py <spec.json> [--werk-dir /pad] [--uitvoer-dir /pad]
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)

def forge(spec_pad: str, werk_dir: Path, uitvoer_dir: Path):
    spec = laad_spec(spec_pad)
    slug = spec['bedrijf']['slug']
    naam = spec['bedrijf']['naam']

    print(f"""
╔══════════════════════════════════════╗
║       WebApex Forge Engine           ║
║       Versie 1.0                     ║
╚══════════════════════════════════════╝

Klant:   {naam}
Slug:    {slug}
Domein:  {spec['domein']['naam']}
Start:   {datetime.now().strftime('%H:%M:%S')}
""")

    start = time.time()

    # Stap 1: Templates ophalen
    from clone_templates import clone_templates
    paden = clone_templates(spec, werk_dir)
    if not paden:
        print("❌ Fout bij ophalen templates")
        sys.exit(1)

    # Paden opslaan
    paden_json = werk_dir / "paden.json"
    with open(paden_json, 'w') as f:
        json.dump({k: str(v) for k, v in paden.items()}, f, indent=2)

    # Stap 2: Project structuur bouwen
    from assemble import maak_project_structuur
    succes, project_dir = maak_project_structuur(spec, paden, uitvoer_dir)
    if not succes:
        print("❌ Fout bij assembleren")
        sys.exit(1)

    # Stap 3: Placeholders invullen
    from fill_placeholders import fill_placeholders
    fill_placeholders(spec, project_dir)

    # Stap 4: Design toepassen
    from apply_design import apply_design
    effect_repo = werk_dir / "repos" / "effect"
    apply_design(spec, project_dir, effect_repo if effect_repo.exists() else None)

    duur = round(time.time() - start, 1)

    print(f"""
╔══════════════════════════════════════╗
║       ✅ FORGE KLAAR                 ║
╚══════════════════════════════════════╝

Project:  {project_dir}
Duur:     {duur} seconden

Volgende stap — handmatig deployen:
  ./deploy.sh {project_dir} <server_ip> <ssh_user> <ssh_key> {spec['domein']['naam']}

Of automatisch als deployment geconfigureerd is.
""")

    return project_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebApex Forge Engine')
    parser.add_argument('spec', help='Pad naar website_spec.json')
    parser.add_argument('--werk-dir', default='/tmp/webapex-forge', help='Tijdelijke werkmap')
    parser.add_argument('--uitvoer-dir', default='/var/www/webapex-clients', help='Output map')

    args = parser.parse_args()

    werk_dir   = Path(args.werk_dir)
    uitvoer_dir = Path(args.uitvoer_dir)
    werk_dir.mkdir(parents=True, exist_ok=True)
    uitvoer_dir.mkdir(parents=True, exist_ok=True)

    forge(args.spec, werk_dir, uitvoer_dir)
