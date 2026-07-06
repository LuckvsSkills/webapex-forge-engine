#!/usr/bin/env python3
"""
WebApex Forge — AI Content Generator
Genereert alle website content op basis van website_spec.json
Gebruikt Claude API via OpenClaw
"""

import json
import os
import re
import sys
from pathlib import Path


OPENCLAW_URL = "http://localhost:50506"


def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)


def bouw_context_prompt(spec: dict) -> str:
    b = spec['bedrijf']
    c = spec['content']
    f = spec['functionaliteit']
    sector = c.get('sector', '')
    stijl = c.get('stijl', '')
    doelen = c.get('doelen', [])
    klanten = c.get('klanten', [])

    return f"""Je bent een expert copywriter voor Nederlandse MKB websites.
Schrijf professionele, authentieke content voor de volgende website:

BEDRIJF: {b['naam']}
STAD: {b['stad']}
BESCHRIJVING: {b['beschrijving']}
SECTOR: {sector}
STIJL: {stijl}
DOELGROEP: {', '.join(klanten)}
HOOFDDOELEN: {', '.join(doelen)}
VERKOOPT PRODUCTEN: {f.get('producten_verkopen', False)}
BIEDT AFSPRAKEN: {f.get('afspraken_boeken', False)}
HEEFT BLOG: {f.get('blog', False)}

Schrijf ALLEEN JSON terug, geen uitleg of markdown.
Alle teksten in het Nederlands, professioneel maar toegankelijk.
Houd rekening met de stijl: {stijl} = {'warm en persoonlijk' if stijl == 'warm' else 'modern en professioneel' if stijl == 'modern' else 'luxe en exclusief' if stijl == 'luxe' else 'nuchter en betrouwbaar'}
"""


def genereer_content_prompt(spec: dict) -> str:
    b = spec['bedrijf']
    f = spec['functionaliteit']
    heeft_producten = f.get('producten_verkopen', False)
    heeft_booking = f.get('afspraken_boeken', False)

    return f"""Genereer alle website content voor {b['naam']}.

Geef een JSON object terug met PRECIES deze structuur:

{{
  "BEDRIJFSNAAM": "{b['naam']}",
  "HERO_BADGE": "korte badge tekst (max 4 woorden, bijv: 'Vers uit Amsterdam')",
  "HERO_HEADLINE": "krachtige headline (max 8 woorden, geen punt aan het einde)",
  "HERO_SUB": "ondertitel (1-2 zinnen, max 20 woorden)",
  "CTA_PRIMAIR": "actie knop tekst (2-4 woorden, bijv: 'Bekijk ons aanbod')",
  "CTA_SECUNDAIR": "secundaire knop (2-4 woorden, bijv: 'Over ons')",
  "HERO_AFBEELDING": "beschrijving voor stockfoto zoekopdracht (Engels, 4-6 woorden)",
  "USP_1": "uniek voordeel 1 (max 5 woorden)",
  "USP_2": "uniek voordeel 2 (max 5 woorden)",
  "USP_3": "uniek voordeel 3 (max 5 woorden)",
  "USP_4": "uniek voordeel 4 (max 5 woorden)",
  "PRODUCTEN_TITEL": "sectie titel voor producten (3-5 woorden)",
  "PRODUCT_1_NAAM": "product naam",
  "PRODUCT_1_BESCHRIJVING": "korte beschrijving (max 10 woorden)",
  "PRODUCT_1_PRIJS": "€ XX,XX",
  "PRODUCT_1_PRIJS_OUD": "€ XX,XX",
  "PRODUCT_1_BADGE": "badge tekst (bijv: 'Nieuw' of 'Bestseller')",
  "PRODUCT_2_NAAM": "product naam",
  "PRODUCT_2_BESCHRIJVING": "korte beschrijving",
  "PRODUCT_2_PRIJS": "€ XX,XX",
  "PRODUCT_2_BADGE": "badge tekst",
  "PRODUCT_3_NAAM": "product naam",
  "PRODUCT_3_BESCHRIJVING": "korte beschrijving",
  "PRODUCT_3_PRIJS": "€ XX,XX",
  "PRODUCT_4_NAAM": "product naam",
  "PRODUCT_4_BESCHRIJVING": "korte beschrijving",
  "PRODUCT_4_PRIJS": "€ XX,XX",
  "OVER_ONS_TITEL": "over ons titel (3-5 woorden)",
  "OVER_ONS_TEKST_1": "over ons tekst (2-3 zinnen, persoonlijk en authentiek)",
  "OVER_ONS_AFBEELDING": "beschrijving voor stockfoto (Engels, 4-6 woorden)",
  "CONTACT_TITEL": "contact sectie titel",
  "FOOTER_TAGLINE": "korte tagline voor footer (max 8 woorden)",
  "AGENT_NAAM": "{b['naam']} Assistent",
  "API_URL": "https://{spec['domein']['naam']}/api"
}}

Schrijf ALLEEN het JSON object, niets anders."""


def roep_claude_aan(system_prompt: str, user_prompt: str, agent: str = "cortexia") -> str:
    """Roept Claude aan via OpenClaw gateway"""
    try:
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "agent": agent,
            "berichten": [
                {"rol": "system", "inhoud": system_prompt},
                {"rol": "user", "inhoud": user_prompt}
            ],
            "max_tokens": 2000,
            "temperatuur": 0.7
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{OPENCLAW_URL}/v1/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('antwoord', result.get('content', ''))

    except Exception as e:
        print(f"  ⚠️  OpenClaw niet beschikbaar: {e}")
        return None


def roep_claude_direct_aan(system_prompt: str, user_prompt: str) -> str:
    """Directe Claude API aanroep als fallback"""
    try:
        import urllib.request

        # Probeer API key uit omgeving
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            # Probeer uit OpenClaw config
            config_pad = Path.home() / '.openclaw' / 'gateway.systemd.env'
            if config_pad.exists():
                for line in config_pad.read_text().splitlines():
                    if 'ANTHROPIC_API_KEY' in line:
                        api_key = line.split('=', 1)[1].strip().strip('"')
                        break

        if not api_key:
            return None

        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['content'][0]['text']

    except Exception as e:
        print(f"  ⚠️  Claude API fout: {e}")
        return None


def genereer_fallback_content(spec: dict) -> dict:
    """Genereer basis content zonder AI als fallback"""
    b = spec['bedrijf']
    naam = b['naam']
    stad = b['stad']
    sector = spec['content'].get('sector', 'bedrijf')
    heeft_producten = spec['functionaliteit'].get('producten_verkopen', False)
    heeft_booking = spec['functionaliteit'].get('afspraken_boeken', False)

    cta = "Maak een afspraak" if heeft_booking else "Bekijk ons aanbod" if heeft_producten else "Neem contact op"
    usp1 = "Gratis bezorging" if heeft_producten else "Snel geholpen"

    return {
        "BEDRIJFSNAAM": naam,
        "HERO_BADGE": f"Gevestigd in {stad}",
        "HERO_HEADLINE": f"Welkom bij {naam}",
        "HERO_SUB": f"Wij staan klaar voor u in {stad}. Kwaliteit en service staan bij ons centraal.",
        "CTA_PRIMAIR": cta,
        "CTA_SECUNDAIR": "Over ons",
        "HERO_AFBEELDING": f"{sector} business professional Amsterdam",
        "USP_1": usp1,
        "USP_2": "Persoonlijke service",
        "USP_3": "Veilig betalen",
        "USP_4": "Altijd bereikbaar",
        "PRODUCTEN_TITEL": "Ons aanbod",
        "PRODUCT_1_NAAM": "Product 1",
        "PRODUCT_1_BESCHRIJVING": "Kwaliteitsproduct voor elke gelegenheid",
        "PRODUCT_1_PRIJS": "€ 19,95",
        "PRODUCT_1_PRIJS_OUD": "€ 24,95",
        "PRODUCT_1_BADGE": "Bestseller",
        "PRODUCT_2_NAAM": "Product 2",
        "PRODUCT_2_BESCHRIJVING": "Populair bij onze klanten",
        "PRODUCT_2_PRIJS": "€ 14,95",
        "PRODUCT_2_BADGE": "Nieuw",
        "PRODUCT_3_NAAM": "Product 3",
        "PRODUCT_3_BESCHRIJVING": "Uitstekende kwaliteit",
        "PRODUCT_3_PRIJS": "€ 9,95",
        "PRODUCT_4_NAAM": "Product 4",
        "PRODUCT_4_BESCHRIJVING": "Onmisbaar in elke collectie",
        "PRODUCT_4_PRIJS": "€ 29,95",
        "OVER_ONS_TITEL": f"Over {naam}",
        "OVER_ONS_TEKST_1": f"{naam} is een gepassioneerd bedrijf gevestigd in {stad}. Wij zetten ons elke dag in voor de beste kwaliteit en service voor onze klanten.",
        "OVER_ONS_AFBEELDING": f"small business owner {stad} Netherlands",
        "CONTACT_TITEL": "Neem contact op",
        "FOOTER_TAGLINE": f"Kwaliteit en service in {stad}",
        "AGENT_NAAM": f"{naam} Assistent",
        "API_URL": f"https://{spec['domein']['naam']}/api",
        "SMTP_WACHTWOORD_INVULLEN": "VERVANG_MET_SMTP_WACHTWOORD",
        "S3_SECRET_INVULLEN": "VERVANG_MET_S3_SECRET",
        "STRIPE_KEY_INVULLEN": "VERVANG_MET_STRIPE_KEY",
        "S3_KEY_INVULLEN": "VERVANG_MET_S3_KEY",
        "MOLLIE_API_KEY_INVULLEN": "VERVANG_MET_MOLLIE_KEY",
        "OPEN_BESTELLINGEN": "0",
        "V2_STUKS": "0",
        "P3_NAAM": "Product 3",
        "K1_EMAIL": b['email'],
        "KPI3_WAARDE": "0",
        "EMAIL": b['email'],
        "OVER_ONS_TEKST_2": f"Kom gerust langs in {stad} of neem contact op via onze website. Wij helpen je graag verder.",
        "OVER_ONS_CTA": "Neem contact op",
        "STAT_1_GETAL": "500+",
        "STAT_1_LABEL": "Tevreden klanten",
        "STAT_2_GETAL": "10+",
        "STAT_2_LABEL": "Jaar ervaring",
        "STAT_3_GETAL": "100%",
        "STAT_3_LABEL": "Kwaliteitsgarantie",
        "CTA_HEADLINE": f"Klaar om te starten met {naam}?",
        "CTA_SUB": "Neem vandaag nog contact op en ontdek wat wij voor jou kunnen betekenen.",
        "CTA_KNOP": "Contact opnemen",
        "DIENSTEN_TITEL": "Onze diensten",
        "DIENST_1_ICON": "⭐",
        "DIENST_1_NAAM": "Kwaliteit",
        "DIENST_1_TEKST": "Wij staan voor de hoogste kwaliteit in alles wat wij doen.",
        "DIENST_2_ICON": "🤝",
        "DIENST_2_NAAM": "Service",
        "DIENST_2_TEKST": "Persoonlijke service en aandacht voor elke klant.",
        "DIENST_3_ICON": "⚡",
        "DIENST_3_NAAM": "Snelheid",
        "DIENST_3_TEKST": "Snel en efficiënt geholpen zonder in te leveren op kwaliteit.",
        "CATEGORIE_1": "Categorie 1",
        "CATEGORIE_2": "Categorie 2",
        "CATEGORIE_3": "Categorie 3",
        "FOOTER_BESCHRIJVING": f"{naam} — Gevestigd in {stad}. Kwaliteit en service staan bij ons centraal.",
    }


def parseer_json_antwoord(tekst: str) -> dict:
    """Haal JSON uit Claude antwoord, ook als er extra tekst omheen zit"""
    if not tekst:
        return {}

    # Probeer direct
    try:
        return json.loads(tekst)
    except:
        pass

    # Probeer JSON blok te vinden
    match = re.search(r'\{[\s\S]+\}', tekst)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return {}


def genereer_ai_content(spec: dict) -> dict:
    """Hoofdfunctie: genereer content via AI of fallback"""
    print("\n🤖 WebApex Forge — AI Content Generatie\n")

    system_prompt = bouw_context_prompt(spec)
    user_prompt = genereer_content_prompt(spec)

    # Probeer eerst OpenClaw
    print("  → Probeer OpenClaw...")
    antwoord = roep_claude_aan(system_prompt, user_prompt)

    if not antwoord:
        # Fallback naar directe Claude API
        print("  → Probeer Claude API direct...")
        antwoord = roep_claude_direct_aan(system_prompt, user_prompt)

    if antwoord:
        content = parseer_json_antwoord(antwoord)
        if content:
            print(f"  ✅ AI content gegenereerd ({len(content)} velden)")
            # Voeg altijd fallback toe voor technische velden
            fallback = genereer_fallback_content(spec)
            for k, v in fallback.items():
                if k not in content:
                    content[k] = v
            return content
        else:
            print("  ⚠️  JSON parsing mislukt — gebruik fallback")
    else:
        print("  ⚠️  AI niet bereikbaar — gebruik fallback content")

    content = genereer_fallback_content(spec)
    print(f"  ✅ Fallback content gegenereerd ({len(content)} velden)")
    return content


def pas_content_toe(uitvoer_map: Path, content: dict) -> int:
    """Vervang alle resterende placeholders in de gegenereerde website"""
    teller = 0

    for bestand in uitvoer_map.rglob('*'):
        if not bestand.is_file():
            continue
        if bestand.suffix not in ['.html', '.css', '.js', '.json', '.md', '.txt', '.env', '.py', '.yml', '.yaml']:
            continue

        try:
            tekst = bestand.read_text(encoding='utf-8', errors='ignore')
            origineel = tekst

            for placeholder, waarde in content.items():
                if isinstance(waarde, str):
                    tekst = tekst.replace(f'{{{{{placeholder}}}}}', waarde)

            if tekst != origineel:
                bestand.write_text(tekst, encoding='utf-8')
                teller += 1
        except Exception as e:
            pass

    return teller


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Gebruik: python3 ai_content_generator.py <spec.json> <uitvoer_map>")
        sys.exit(1)

    spec_pad = sys.argv[1]
    uitvoer_map = Path(sys.argv[2])

    spec = laad_spec(spec_pad)
    content = genereer_ai_content(spec)

    bijgewerkt = pas_content_toe(uitvoer_map, content)
    print(f"\n  ✅ {bijgewerkt} bestanden bijgewerkt met AI content")

    # Sla content op voor referentie
    content_pad = uitvoer_map / "ai_content.json"
    with open(content_pad, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"  📄 Content opgeslagen: {content_pad}")
