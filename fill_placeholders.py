#!/usr/bin/env python3
"""
WebApex Forge Engine — Stap 2: Fill Placeholders
Vervangt alle {{PLACEHOLDERS}} in templates met echte klantdata
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)

def bouw_variabelen(spec: dict) -> dict:
    """Zet spec om naar een platte variabelen dict voor placeholder vervanging"""
    b = spec['bedrijf']
    d = spec['design']
    a = spec['agent']
    h = spec['hosting']
    dom = spec['domein']

    vars = {
        # Bedrijf
        'BEDRIJF_NAAM':     b['naam'],
        'WINKEL_NAAM':      b['naam'],
        'SITE_NAAM':        b['naam'],
        'PLATFORM_NAAM':    b['naam'],
        'COMMUNITY_NAAM':   b['naam'],
        'BEDRIJF_NAAM':     b['naam'],
        'BEDRIJF_SLUG':     b['slug'],
        'BEDRIJF_EMAIL':    b['email'],
        'WINKEL_EMAIL':     b['email'],
        'SITE_EMAIL':       b['email'],
        'PLATFORM_EMAIL':   b['email'],
        'BEDRIJF_TEL':      b['telefoon'],
        'TELEFOON':         b['telefoon'],
        'BEDRIJF_ADRES':    b['adres'],
        'ADRES':            b['adres'],
        'POSTCODE':         b['postcode'],
        'STAD':             b['stad'],
        'KVK':              b['kvk'],
        'BTW':              b['btw'],
        'BESCHRIJVING':     b['beschrijving'],
        'TAGLINE':          b['tagline'],
        'LOGO_URL':         b['logo_url'],
        'WINKEL_URL':       b['website_url'],
        'SITE_URL':         b['website_url'],
        'PLATFORM_URL':     b['website_url'],
        'BEDRIJF_URL':      b['website_url'],
        'COMMUNITY_URL':    b['website_url'],
        'FRONTEND_URL':     b['website_url'],

        # Initials voor admin panels
        'WINKEL_INITIAL':    b['naam'][0].upper() if b['naam'] else 'W',
        'SITE_INITIAL':      b['naam'][0].upper() if b['naam'] else 'S',
        'PLATFORM_INITIAL':  b['naam'][0].upper() if b['naam'] else 'P',
        'BEDRIJF_INITIAL':   b['naam'][0].upper() if b['naam'] else 'B',
        'COMMUNITY_INITIAL': b['naam'][0].upper() if b['naam'] else 'C',
        'ADMIN_NAAM':        'Admin',
        'ADMIN_INITIAL':     'A',

        # Database
        'DATABASE_URL':     f"postgresql://webapex:{b['slug']}_db_pass@localhost:5432/{b['slug']}_db",
        'JWT_SECRET':       os.urandom(32).hex(),
        'REDIS_URL':        'redis://localhost:6379',

        # Betaling
        'BETAAL_PROVIDER':  spec['backend'].get('betaal_provider', 'mollie'),
        'MOLLIE_API_KEY':   '{{MOLLIE_API_KEY_INVULLEN}}',
        'STRIPE_SECRET_KEY':'{{STRIPE_KEY_INVULLEN}}',

        # Email
        'SMTP_HOST':        'smtp.gmail.com',
        'SMTP_PORT':        '587',
        'SMTP_GEBRUIKER':   b['email'],
        'SMTP_WACHTWOORD':  '{{SMTP_WACHTWOORD_INVULLEN}}',

        # Storage
        'STORAGE_TYPE':     's3',
        'S3_BUCKET':        f"{b['slug']}-media",
        'S3_REGIO':         'eu-west-1',
        'S3_TOEGANG_KEY':   '{{S3_KEY_INVULLEN}}',
        'S3_GEHEIM_KEY':    '{{S3_SECRET_INVULLEN}}',

        # Agent
        'AGENT_ACTIEF':     str(a['actief']).lower(),
        'AGENT_NAAM':       a.get('naam', f"{b['naam']} Assistent"),
        'AGENT_API_URL':    f"{b['website_url']}/agent",
        'AGENT_TOKEN':      os.urandom(16).hex(),

        # Domein
        'DOMEIN':           dom['naam'],

        # Winkel specifiek
        'WINKEL_PREFIX':    b['slug'].upper()[:6],
        'BEDRIJF_PREFIX':   b['slug'].upper()[:6],
        'PLATFORM_PREFIX':  b['slug'].upper()[:6],

        # Prijzen SaaS
        'PRIJS_STARTER':    '19.00',
        'PRIJS_STARTER_JAAR': '182.40',
        'PRIJS_PRO':        '49.00',
        'PRIJS_PRO_JAAR':   '470.40',
        'PRIJS_ENTERPRISE': '149.00',
        'PRIJS_ENTERPRISE_JAAR': '1430.40',

        # Standaard waarden
        'VERZENDKOSTEN':    '4.95',
        'GRATIS_VERZENDING':'50',
        'ANNULERING_UREN':  '24',
        'HERINNERING_UREN': '24',
        'PROEF_DAGEN':      '14',
        'RATE_LIMIT':       '1000',
        'MIN_VOORRAAD':     '5',
        'COMM_PCT':         '10',
        'MIN_UITBETALING':  '50',
    }

    return vars

def vervang_in_bestand(bestand_pad: Path, variabelen: dict) -> int:
    """Vervangt alle {{PLACEHOLDER}} in een bestand. Geeft aantal vervangingen terug."""
    try:
        inhoud = bestand_pad.read_text(encoding='utf-8')
        original = inhoud
        vervangingen = 0

        for sleutel, waarde in variabelen.items():
            patroon = f"{{{{{sleutel}}}}}"
            if patroon in inhoud:
                inhoud = inhoud.replace(patroon, str(waarde))
                vervangingen += inhoud.count(str(waarde))

        # Tel resterende placeholders
        overgebleven = re.findall(r'\{\{[A-Z_0-9]+\}\}', inhoud)
        if overgebleven:
            uniek = list(set(overgebleven))
            print(f"  ⚠️  Niet ingevuld in {bestand_pad.name}: {', '.join(uniek[:5])}")

        if inhoud != original:
            bestand_pad.write_text(inhoud, encoding='utf-8')

        return len(variabelen) - len(set(overgebleven))

    except Exception as e:
        print(f"  ❌ Fout bij {bestand_pad}: {e}")
        return 0

def verwerk_map(map_pad: Path, variabelen: dict, extensies: list = None) -> int:
    """Verwerkt alle bestanden in een map recursief"""
    if extensies is None:
        extensies = ['.html', '.css', '.js', '.py', '.json', '.md', '.sql', '.env', '.yml', '.yaml']

    totaal = 0
    for bestand in map_pad.rglob('*'):
        if bestand.is_file() and bestand.suffix in extensies:
            totaal += vervang_in_bestand(bestand, variabelen)

    return totaal

def fill_placeholders(spec: dict, klant_dir: Path) -> bool:
    print("\n🔧 WebApex Forge — Stap 2: Placeholders invullen\n")

    variabelen = bouw_variabelen(spec)
    print(f"  📋 {len(variabelen)} variabelen geladen")

    onderdelen = ['frontend', 'backend', 'admin', 'agent']
    for onderdeel in onderdelen:
        pad = klant_dir / onderdeel
        if pad.exists():
            print(f"  ↻ Verwerk {onderdeel}...")
            n = verwerk_map(pad, variabelen)
            print(f"  ✅ {onderdeel}: klaar")

    print(f"\n✅ Alle placeholders ingevuld\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Gebruik: python3 fill_placeholders.py <spec.json> <klant_dir>")
        sys.exit(1)

    spec = laad_spec(sys.argv[1])
    klant_dir = Path(sys.argv[2])

    fill_placeholders(spec, klant_dir)
