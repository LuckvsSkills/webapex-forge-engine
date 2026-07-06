#!/usr/bin/env python3
"""
WebApex Agent Personalizer
Kopieert de agent blauwdruk en personaliseert voor specifieke klant
Onderdeel van het automatische uitrol process
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


BLAUWDRUK_PAD = Path("/home/prime/arc_ai_angels/projects/website_factory/agent-blauwdruk")
CLIENTS_PAD   = Path("/var/www/clients")


def maak_telegram_bot(bedrijfsnaam: str) -> dict:
    """
    Maak een nieuwe Telegram bot aan via BotFather
    In productie: automatisch via Telegram API
    Nu: instructies genereren voor handmatige aanmaak
    """
    slug = bedrijfsnaam.lower().replace(" ", "_").replace("-", "_")
    bot_naam = f"{slug}_webapex_bot"

    print(f"  📱 Telegram bot naam: @{bot_naam}")
    print(f"  → Maak aan via @BotFather: /newbot")
    print(f"  → Bot naam: {bedrijfsnaam} Agent")
    print(f"  → Username: {bot_naam}")

    return {
        "bot_naam": bot_naam,
        "bot_token": "HANDMATIG_IN_TE_VULLEN",
        "chat_id":   "HANDMATIG_IN_TE_VULLEN"
    }


def personaliseer_agent(spec: dict, klant_map: Path) -> Path:
    """
    Kopieert blauwdruk en vult alle placeholders in
    """
    agent_map = klant_map / "openclaw" / "agent"
    agent_map.mkdir(parents=True, exist_ok=True)

    b = spec['bedrijf']
    d = spec['domein']

    # Telegram bot
    telegram = maak_telegram_bot(b['naam'])

    # Alle placeholders
    variabelen = {
        "{{BEDRIJF_NAAM}}":       b['naam'],
        "{{EIGENAAR_NAAM}}":      b.get('naam', b['naam']),
        "{{EIGENAAR_EMAIL}}":     b['email'],
        "{{EIGENAAR_TELEFOON}}":  b.get('telefoon', ''),
        "{{BEDRIJF_STAD}}":       b.get('stad', ''),
        "{{KVK}}":                b.get('kvk', ''),
        "{{WEBSITE_URL}}":        f"https://{d['naam']}",
        "{{ADMIN_URL}}":          f"https://{d['naam']}/admin",
        "{{API_URL}}":            f"https://{d['naam']}/api",
        "{{WEBSITE_TYPE}}":       spec['backend']['type'],
        "{{PAKKET_NAAM}}":        spec['prijzen']['pakket'],
        "{{AGENT_NAAM}}":         f"{b['naam'].split()[0]} Agent",
        "{{TELEGRAM_CHAT_ID}}":   telegram['chat_id'],
        "{{TELEGRAM_BOT_TOKEN}}": telegram['bot_token'],
        "{{DATUM_AANGEMAAKT}}":   datetime.now().strftime('%Y-%m-%d %H:%M'),
        "{{COMM_STIJL}}":         "Professioneel maar toegankelijk",
        "{{KLANT_NOTITIES}}":     b.get('beschrijving', ''),
    }

    # Kopieer en personaliseer elk bestand
    for bron in BLAUWDRUK_PAD.iterdir():
        doel = agent_map / bron.name
        inhoud = bron.read_text(encoding='utf-8')

        for placeholder, waarde in variabelen.items():
            inhoud = inhoud.replace(placeholder, str(waarde))

        doel.write_text(inhoud, encoding='utf-8')
        print(f"  ✅ {bron.name} gepersonaliseerd")

    # Sla telegram config op
    telegram_conf = agent_map.parent / "telegram.json"
    telegram_conf.write_text(json.dumps(telegram, indent=2))

    print(f"\n  ✅ Agent aangemaakt in: {agent_map}")
    print(f"  📱 Telegram bot: @{telegram['bot_naam']}")
    print(f"  ⚠️  Vul telegram bot token in: {telegram_conf}")

    return agent_map


def maak_cronjobs(agent_map: Path, klant_slug: str):
    """Activeer cronjobs voor de agent"""
    forge_json = agent_map / "forge.json"
    if not forge_json.exists():
        return

    config = json.loads(forge_json.read_text())
    cronjobs = config.get("cronjobs", [])

    print(f"\n  ⏰ Cronjobs aanmaken voor {klant_slug}:")
    for job in cronjobs:
        print(f"    → {job['naam']}: {job['tijd']}")

    # In productie: installeer echte crontab
    cron_script = agent_map.parent / "start_agent.sh"
    cron_script.write_text(f"""#!/bin/bash
# WebApex Agent Cronjobs voor {klant_slug}
# Automatisch gegenereerd door agent_personalizer.py

AGENT_DIR="{agent_map}"
LOG_DIR="{agent_map.parent}/logs"

mkdir -p $LOG_DIR

echo "✅ Agent gestart voor {klant_slug}"
echo "📁 Agent map: $AGENT_DIR"
echo "📝 Logs: $LOG_DIR"

# Voeg toe aan crontab:
# 0 6  * * * python3 $AGENT_DIR/../run_agent.py ochtend >> $LOG_DIR/ochtend.log 2>&1
# 0 12 * * * python3 $AGENT_DIR/../run_agent.py middag  >> $LOG_DIR/middag.log  2>&1
# 0 18 * * * python3 $AGENT_DIR/../run_agent.py avond   >> $LOG_DIR/avond.log   2>&1
# 0 23 * * * python3 $AGENT_DIR/../run_agent.py nacht   >> $LOG_DIR/nacht.log   2>&1
""")
    cron_script.chmod(0o755)
    print(f"  ✅ Start script aangemaakt: {cron_script}")


def volledig_agent_setup(spec: dict, klant_map: Path):
    """Complete agent setup voor nieuwe klant"""
    print(f"\n🤖 Agent setup voor: {spec['bedrijf']['naam']}\n")

    agent_map = personaliseer_agent(spec, klant_map)
    klant_slug = spec['bedrijf']['slug']
    maak_cronjobs(agent_map, klant_slug)

    print(f"""
╔══════════════════════════════════════╗
║   ✅ AGENT SETUP KLAAR               ║
╚══════════════════════════════════════╝

Klant:   {spec['bedrijf']['naam']}
Agent:   {spec['bedrijf']['naam'].split()[0]} Agent
Map:     {agent_map}

VOLGENDE STAPPEN:
1. Maak Telegram bot aan via @BotFather
2. Vul token in: {agent_map.parent}/telegram.json
3. Klant stuurt /start naar de bot
4. Agent is actief!
""")


if __name__ == "__main__":
    # Test met bakkerij spec
    test_spec = json.loads(
        open('/tmp/klant-bakkerij-de-vries-20260706065320.json').read()
    )
    test_map = Path('/tmp/forge-output/client-bakkerij-de-vries')
    volledig_agent_setup(test_spec, test_map)
