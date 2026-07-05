#!/usr/bin/env python3
"""
WebApex Forge Engine — Stap 3: Apply Design
Past kleurpalet, lettertype, button stijl en effect overlay toe op frontend
"""

import json
import shutil
import sys
from pathlib import Path

DESIGN_CONFIGS_PAD = Path(__file__).parent / "design-configs.json"

def laad_spec(spec_pad: str) -> dict:
    with open(spec_pad, 'r', encoding='utf-8') as f:
        return json.load(f)

def laad_design_configs() -> dict:
    if DESIGN_CONFIGS_PAD.exists():
        with open(DESIGN_CONFIGS_PAD, 'r') as f:
            return json.load(f)
    return {}

def pas_kleuren_toe(html_pad: Path, palet: dict) -> bool:
    """Overschrijft CSS variabelen in :root van het HTML bestand"""
    try:
        inhoud = html_pad.read_text(encoding='utf-8')

        css_vars = '\n'.join([f"    {k}: {v};" for k, v in palet.items() if k.startswith('--')])
        override = f"""
    /* WebApex Design Override */
{css_vars}"""

        if ':root{' in inhoud:
            inhoud = inhoud.replace(':root{', f':root{{{override}', 1)
        elif ':root {' in inhoud:
            inhoud = inhoud.replace(':root {', f':root {{{override}', 1)
        else:
            style_inject = f"<style>:root{{{override}}}</style>"
            inhoud = inhoud.replace('</head>', f'{style_inject}\n</head>', 1)

        html_pad.write_text(inhoud, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  ❌ Kleur fout: {e}")
        return False

def pas_lettertype_toe(html_pad: Path, lettertype: dict) -> bool:
    """Voegt Google Font toe en past font-family aan"""
    try:
        inhoud = html_pad.read_text(encoding='utf-8')

        google_font = lettertype.get('google_font')
        if google_font:
            font_link = f'<link rel="preconnect" href="https://fonts.googleapis.com">\n    <link href="https://fonts.googleapis.com/css2?family={google_font}:wght@400;600;700;800;900&display=swap" rel="stylesheet">'
            if 'fonts.googleapis.com' not in inhoud:
                inhoud = inhoud.replace('</head>', f'{font_link}\n</head>', 1)

        family = lettertype.get('family', '')
        if family:
            font_override = f"<style>body, * {{ font-family: {family} !important; }}</style>"
            inhoud = inhoud.replace('</head>', f'{font_override}\n</head>', 1)

        html_pad.write_text(inhoud, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  ❌ Font fout: {e}")
        return False

def pas_button_stijl_toe(html_pad: Path, radius: str) -> bool:
    """Past border-radius aan voor knoppen"""
    try:
        inhoud = html_pad.read_text(encoding='utf-8')
        override = f"<style>[class*='btn']{{ border-radius: {radius} !important; }}</style>"
        inhoud = inhoud.replace('</head>', f'{override}\n</head>', 1)
        html_pad.write_text(inhoud, encoding='utf-8')
        return True
    except:
        return False

def pas_effect_toe(frontend_dir: Path, effect_pad: Path) -> bool:
    """Kopieert effect bestanden en voegt links toe aan HTML"""
    try:
        # Kopieer effect bestanden
        for bestand in effect_pad.iterdir():
            if bestand.suffix in ['.js', '.css']:
                shutil.copy2(bestand, frontend_dir / bestand.name)

        # Voeg links toe aan index.html
        html = frontend_dir / 'index.html'
        if not html.exists():
            return False

        inhoud = html.read_text(encoding='utf-8')

        effect_css = effect_pad / 'effect.css'
        effect_js  = effect_pad / 'effect.js'

        if effect_css.exists() and 'effect.css' not in inhoud:
            inhoud = inhoud.replace('</head>', '<link rel="stylesheet" href="effect.css">\n</head>', 1)

        if effect_js.exists() and 'effect.js' not in inhoud:
            inhoud = inhoud.replace('</body>', '<script src="effect.js"></script>\n</body>', 1)

        html.write_text(inhoud, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  ❌ Effect fout: {e}")
        return False

def apply_design(spec: dict, klant_dir: Path, effect_repo_pad: Path = None) -> bool:
    print("\n🎨 WebApex Forge — Stap 3: Design toepassen\n")

    design = spec['design']
    niveau = design.get('niveau', 'basic')

    if niveau == 'basic':
        print("  ℹ️  Basic niveau — geen design aanpassingen")
        return True

    configs = laad_design_configs()
    frontend_html = klant_dir / 'frontend' / 'index.html'

    if not frontend_html.exists():
        print(f"  ❌ Frontend HTML niet gevonden: {frontend_html}")
        return False

    # Kleurpalet
    palet_naam = design.get('kleurpalet', 'ocean')
    palet = configs.get('kleurpaletten', {}).get(palet_naam, {})
    if palet:
        pas_kleuren_toe(frontend_html, palet)
        print(f"  ✅ Kleurpalet: {palet_naam}")

    # Lettertype
    font_naam = design.get('lettertype', 'modern')
    font = configs.get('lettertypen', {}).get(font_naam, {})
    if font:
        pas_lettertype_toe(frontend_html, font)
        print(f"  ✅ Lettertype: {font_naam}")

    # Button stijl
    btn_naam = design.get('button_stijl', 'medium')
    btn = configs.get('button_stijlen', {}).get(btn_naam, {})
    if btn:
        radius = btn.get('border-radius', '8px')
        pas_button_stijl_toe(frontend_html, radius)
        print(f"  ✅ Button stijl: {btn_naam}")

    # Effect overlay
    effect_code = design.get('effect_overlay')
    if effect_code and effect_repo_pad:
        effect_pad = effect_repo_pad / effect_code
        if effect_pad.exists():
            pas_effect_toe(klant_dir / 'frontend', effect_pad)
            print(f"  ✅ Effect overlay: {effect_code}")

    print(f"\n✅ Design toegepast\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Gebruik: python3 apply_design.py <spec.json> <klant_dir> [effect_repo_pad]")
        sys.exit(1)

    spec = laad_spec(sys.argv[1])
    klant_dir = Path(sys.argv[2])
    effect_repo = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    apply_design(spec, klant_dir, effect_repo)
