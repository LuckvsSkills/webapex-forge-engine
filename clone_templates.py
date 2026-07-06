#!/usr/bin/env python3
"""
WebApex Forge Engine — Stap 1: Clone Templates
Haalt de juiste templates op van GitHub op basis van website_spec.json
"""

import json
import os
import subprocess
import sys
from pathlib import Path

GITHUB_BASE = "https://github.com/LuckvsSkills"

REPOS = {
    "frontend":   "arc-template-library",
    "backend":    "arc-backend-templates",
    "admin":      "arc-admin-templates",
    "agent":      "arc-agent-templates",
    "effect":     "arc-effect-templates",
    "components": "arc-component-library",
}

def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)

def run(cmd: str, cwd: str = None) -> bool:
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Fout: {result.stderr}")
        return False
    return True

def clone_of_update(repo_naam: str, pad: Path) -> bool:
    url = f"{GITHUB_BASE}/{repo_naam}.git"
    if pad.exists():
        print(f"  ↻ Update {repo_naam}")
        return run("git pull", cwd=str(pad))
    else:
        print(f"  ↓ Clone {repo_naam}")
        return run(f"git clone {url} {pad}")

def clone_templates(spec: dict, werk_dir: Path) -> dict:
    print("\n🔧 WebApex Forge — Stap 1: Templates ophalen\n")

    paden = {}

    # Frontend template
    frontend_type = spec['frontend']['template']
    frontend_versie = spec['frontend']['versie']
    frontend_basis_type = spec['frontend']['type']

    frontend_repo = werk_dir / "repos" / "frontend"
    if clone_of_update(REPOS['frontend'], frontend_repo):
        template_pad = frontend_repo / frontend_versie / f"{frontend_basis_type}-{frontend_versie}"
        if template_pad.exists():
            paden['frontend'] = template_pad
            print(f"  ✅ Frontend: {frontend_type}")
        else:
            print(f"  ❌ Template niet gevonden: {template_pad}")
            return {}

    # Backend template
    backend_type = spec['backend']['type']
    backend_repo = werk_dir / "repos" / "backend"
    if clone_of_update(REPOS['backend'], backend_repo):
        backend_pad = backend_repo / backend_type
        if backend_pad.exists():
            paden['backend'] = backend_pad
            print(f"  ✅ Backend: {backend_type}")
        else:
            print(f"  ❌ Backend niet gevonden: {backend_pad}")
            return {}

    # Admin template
    admin_repo = werk_dir / "repos" / "admin"
    if clone_of_update(REPOS['admin'], admin_repo):
        admin_pad = admin_repo / backend_type
        if admin_pad.exists():
            paden['admin'] = admin_pad
            print(f"  ✅ Admin: {backend_type}")

    # Agent template (optioneel)
    if spec['agent']['actief']:
        agent_type = spec['agent']['type']
        agent_basis = agent_type.replace('agent-', '')
        agent_repo = werk_dir / "repos" / "agent"
        if clone_of_update(REPOS['agent'], agent_repo):
            agent_pad = agent_repo / agent_basis
            if agent_pad.exists():
                paden['agent'] = agent_pad
                print(f"  ✅ Agent: {agent_type}")

    # Effect overlay (optioneel)
    effect_code = spec['design'].get('effect_overlay')
    if effect_code:
        effect_repo = werk_dir / "repos" / "effect"
        if clone_of_update(REPOS['effect'], effect_repo):
            effect_pad = effect_repo / effect_code
            if effect_pad.exists():
                paden['effect'] = effect_pad
                print(f"  ✅ Effect: {effect_code}")

    # Component library
    comp_repo = werk_dir / "repos" / "components"
    if clone_of_update(REPOS['components'], comp_repo):
        paden['components'] = comp_repo
        print(f"  ✅ Componenten geladen")

    print(f"\n✅ Alle templates opgehaald ({len(paden)} onderdelen)\n")
    return paden

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Gebruik: python3 clone_templates.py <spec.json> <werk_dir>")
        sys.exit(1)

    spec = laad_spec(sys.argv[1])
    werk_dir = Path(sys.argv[2])
    werk_dir.mkdir(parents=True, exist_ok=True)

    paden = clone_templates(spec, werk_dir)

    # Sla paden op voor volgende stap
    paden_output = {k: str(v) for k, v in paden.items()}
    with open(werk_dir / "paden.json", 'w') as f:
        json.dump(paden_output, f, indent=2)

    print(f"📁 Paden opgeslagen in {werk_dir}/paden.json")
