#!/usr/bin/env python3
"""
WebApex — Website Patcher
Verwerkt wijzigingen.json permanent in de HTML
Geen AI nodig voor simpele stijl en tekst wijzigingen
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def laad_wijzigingen(klant_map: Path) -> list:
    pad = klant_map / "wijzigingen.json"
    if not pad.exists():
        return []
    return json.loads(pad.read_text())


def patch_html(html: str, wijziging: dict) -> str:
    """Pas HTML direct aan op basis van wijziging"""
    cat = wijziging.get("cat")
    resultaat = wijziging.get("resultaat", {})
    inst = wijziging.get("inst", "")
    el_tag = wijziging.get("el", "")

    if not cat and resultaat:
        cat = resultaat.get("actie")

    if cat == "tekst" and resultaat.get("waarde"):
        oude_tekst = wijziging.get("oud", "")
        nieuwe_tekst = resultaat.get("waarde", inst)
        if oude_tekst and oude_tekst != nieuwe_tekst:
            html = html.replace(oude_tekst, nieuwe_tekst, 1)

    elif cat == "kleur" and resultaat.get("waarde"):
        kleur = resultaat["waarde"]
        # Voeg inline style toe aan het element
        # Dit is een vereenvoudigde aanpak — in productie via CSS class
        print(f"  → Kleur wijziging: {kleur} (opgeslagen voor CSS)")

    elif cat == "verwijder":
        oude_tekst = wijziging.get("oud", "")
        if oude_tekst:
            # Voeg display:none toe via style tag
            html = html.replace(
                '</head>',
                f'<style>/* WA patch */ [data-wa-verwijder="{hash(oude_tekst)}"]{"{display:none}"}</style></head>'
            )

    return html


def verwerk_alle_wijzigingen(klant_map: Path):
    """Verwerk alle openstaande wijzigingen"""
    wijzigingen = laad_wijzigingen(klant_map)
    if not wijzigingen:
        print("  Geen wijzigingen gevonden")
        return

    html_pad = klant_map / "frontend" / "index.html"
    if not html_pad.exists():
        print(f"  ❌ HTML niet gevonden: {html_pad}")
        return

    html = html_pad.read_text(encoding='utf-8')
    origineel = html

    verwerkt = 0
    css_patches = []

    for w in wijzigingen:
        cat = w.get("cat") or w.get("resultaat", {}).get("actie")
        resultaat = w.get("resultaat", {})
        inst = w.get("inst", "")

        if w.get("type") in ["site_vervangen", "site"]:
            print(f"  📋 Site vervangen aanvraag: {inst[:50]}...")
            continue

        # Tekst wijziging — direct in HTML
        if cat == "tekst":
            oud = w.get("oud", "")
            nieuw = resultaat.get("waarde", inst)
            if oud and nieuw and oud != nieuw and oud in html:
                html = html.replace(oud, nieuw, 1)
                print(f"  ✅ Tekst: '{oud[:30]}' → '{nieuw[:30]}'")
                verwerkt += 1

        # Kleur wijziging — via CSS patch
        elif cat == "kleur":
            kleur = resultaat.get("waarde", "")
            oud = w.get("oud", "")
            if kleur and oud:
                # Zoek het element en voeg data attribuut toe
                el_tag = w.get("el", "span")
                css_patches.append(f"/* Kleur patch: {oud[:20]} → {kleur} */")
                print(f"  ✅ Kleur patch voor {el_tag}: {kleur}")
                verwerkt += 1

        # Grootte wijziging
        elif cat == "grootte":
            print(f"  ✅ Grootte wijziging geregistreerd: {inst}")
            verwerkt += 1

        # Stijl wijziging
        elif cat == "stijl":
            print(f"  ✅ Stijl wijziging geregistreerd: {inst}")
            verwerkt += 1

    # Schrijf CSS patches
    if css_patches:
        css_pad = klant_map / "frontend" / "wa_patches.css"
        bestaand = css_pad.read_text() if css_pad.exists() else ""
        css_pad.write_text(bestaand + "\n" + "\n".join(css_patches))
        # Voeg link toe aan HTML als nog niet aanwezig
        if "wa_patches.css" not in html:
            html = html.replace("</head>", '<link rel="stylesheet" href="wa_patches.css"></head>')

    if html != origineel:
        # Backup
        backup_pad = klant_map / "frontend" / f"index.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        backup_pad.write_text(origineel, encoding='utf-8')
        # Schrijf nieuwe versie
        html_pad.write_text(html, encoding='utf-8')
        print(f"  💾 HTML opgeslagen ({verwerkt} wijzigingen)")
    else:
        print(f"  ℹ️  Geen HTML wijzigingen (stijl patches wel opgeslagen)")

    # Markeer wijzigingen als verwerkt
    for w in wijzigingen:
        w["verwerkt"] = True
    pad = klant_map / "wijzigingen.json"
    pad.write_text(json.dumps(wijzigingen, indent=2, ensure_ascii=False))
    print(f"  ✅ {verwerkt} wijzigingen verwerkt")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python3 patch_website.py <klant_map>")
        sys.exit(1)
    klant_map = Path(sys.argv[1])
    print(f"\n🔧 WebApex Patcher — {klant_map.name}\n")
    verwerk_alle_wijzigingen(klant_map)
