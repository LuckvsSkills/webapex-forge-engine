#!/usr/bin/env python3
"""
WebApex — Wizard naar Forge Spec Converter
Zet wizard antwoorden om naar een website_spec.json voor de Forge engine
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path


# ============================================
# TEMPLATE MAPPING
# ============================================
TEMPLATE_MAP = {
    "glossier":  {"id": "glossier-v1",  "type": "bedrijf",    "versie": "v1"},
    "gymshark":  {"id": "gymshark-v1",  "type": "ecommerce",  "versie": "v1"},
    "stripe":    {"id": "stripe-v1",    "type": "saas",       "versie": "v1"},
    "linear":    {"id": "linear-v1",    "type": "saas",       "versie": "v1"},
    "notion":    {"id": "notion-v1",    "type": "content",    "versie": "v1"},
    "resy":      {"id": "resy-v1",      "type": "booking",    "versie": "v1"},
    "mailchimp": {"id": "mailchimp-v1", "type": "bedrijf",    "versie": "v1"},
    "basecamp":  {"id": "basecamp-v1",  "type": "bedrijf",    "versie": "v1"},
    "monograph": {"id": "monograph-v1", "type": "portfolio",  "versie": "v1"},
    "airtable":  {"id": "airtable-v1",  "type": "saas",       "versie": "v1"},
}

DESIGN_MAP = {
    "glossier":  {"kleurpalet": "roze",   "lettertype": "serif",      "button_stijl": "rond",   "effect": "E1-aurora"},
    "gymshark":  {"kleurpalet": "donker", "lettertype": "bold",        "button_stijl": "scherp", "effect": "E2-kinetic"},
    "stripe":    {"kleurpalet": "blauw",  "lettertype": "modern",      "button_stijl": "licht",  "effect": "E2-kinetic"},
    "linear":    {"kleurpalet": "dark",   "lettertype": "modern",      "button_stijl": "licht",  "effect": "E3-depth"},
    "notion":    {"kleurpalet": "wit",    "lettertype": "sans",        "button_stijl": "licht",  "effect": "E5-minimal"},
    "resy":      {"kleurpalet": "goud",   "lettertype": "serif",       "button_stijl": "scherp", "effect": "E3-depth"},
    "mailchimp": {"kleurpalet": "geel",   "lettertype": "vriendelijk", "button_stijl": "rond",   "effect": "E1-aurora"},
    "basecamp":  {"kleurpalet": "groen",  "lettertype": "sans",        "button_stijl": "licht",  "effect": "E5-minimal"},
    "monograph": {"kleurpalet": "zwart",  "lettertype": "serif",       "button_stijl": "scherp", "effect": "E5-minimal"},
    "airtable":  {"kleurpalet": "paars",  "lettertype": "modern",      "button_stijl": "licht",  "effect": "E7-magnetic"},
}

BACKEND_MAP = {
    "kopen":     "ecommerce",
    "afspraak":  "booking",
    "ontdekken": "content",
    "meedoen":   "community",
    "gebruiken": "saas",
}

AGENT_MAP = {
    "agent_standaard": {"niveau": "standaard", "taken": ["content", "bestellingen", "email"]},
    "agent_pro":       {"niveau": "pro",       "taken": ["content", "bestellingen", "email", "seo", "social", "leveranciers"]},
    "geen":            {"niveau": "geen",      "taken": []},
}

PAKKET_PRIJZEN = {
    "snel_basis":    {"setup": 249,  "maand": 52},
    "snel_plus":     {"setup": 199,  "maand": 69},
    "slim_pakket":   {"setup": 499,  "maand": 79},
    "slim_deluxe":   {"setup": 479,  "maand": 109},
    "studio_pakket": {"setup": 1499, "maand": 149},
    "studio_deluxe": {"setup": 1399, "maand": 179},
}

EXTRA_PRIJZEN = {
    "seo_pro":       19,
    "ai_zichtbaar":  15,
    "social_media":  29,
    "onderhoud":     49,
    "backup":        9,
    "logo":          0,
    "google_biz":    0,
    "product_invoer":0,
}


def slugify(naam: str) -> str:
    naam = naam.lower()
    naam = re.sub(r'[^a-z0-9\s-]', '', naam)
    naam = re.sub(r'\s+', '-', naam.strip())
    return naam


def bepaal_backend(activiteiten: list) -> dict:
    if not activiteiten:
        return {"type": "bedrijf", "combinatie": None}
    
    backends = [BACKEND_MAP.get(a, "bedrijf") for a in activiteiten]
    backends = list(dict.fromkeys(backends))  # dedup volgorde bewaren
    
    if len(backends) == 1:
        return {"type": backends[0], "combinatie": None}
    else:
        return {"type": backends[0], "combinatie": backends}


def bepaal_functionaliteit(activiteiten: list, doelen: list) -> dict:
    acts = activiteiten or []
    doelen = doelen or []
    
    return {
        "producten_verkopen":  "kopen" in acts or "omzet" in doelen,
        "afspraken_boeken":    "afspraak" in acts or "afspraken" in doelen,
        "blog":                "ontdekken" in acts,
        "leden_systeem":       "meedoen" in acts or "community" in doelen,
        "reviews":             True,
        "nieuwsbrief":         True,
        "contactformulier":    True,
        "zoekfunctie":         "kopen" in acts or "ontdekken" in acts,
        "meerdere_talen":      False,
    }


def bereken_prijzen(pakket_id: str, agent_id: str, extras: list, fotos: str) -> dict:
    pk = PAKKET_PRIJZEN.get(pakket_id, {"setup": 499, "maand": 79})
    setup = pk["setup"]
    maand = pk["maand"]
    
    # Agent prijs
    if agent_id == "agent_standaard":
        maand += 29.99
    elif agent_id == "agent_pro":
        maand += 49.99
    
    # Foto's eenmalig
    if fotos == "stock":
        setup += 49
    elif fotos == "ai":
        setup += 99
    
    # Extra maandelijkse services
    for extra in (extras or []):
        maand += EXTRA_PRIJZEN.get(extra, 0)
    
    return {
        "pakket":             pakket_id,
        "setup_eenmalig":     round(setup, 2),
        "hosting_maandelijks": pk["maand"],
        "agent_maandelijks":  29.99 if agent_id == "agent_standaard" else (49.99 if agent_id == "agent_pro" else 0),
        "extras_maandelijks": round(maand - pk["maand"] - (29.99 if agent_id == "agent_standaard" else (49.99 if agent_id == "agent_pro" else 0)), 2),
        "totaal_eerste_maand": round(setup + maand, 2),
        "totaal_maandelijks":  round(maand, 2),
    }


def wizard_naar_spec(wizard_data: dict) -> dict:
    """
    Hoofdfunctie: zet wizard antwoorden om naar Forge spec
    
    wizard_data verwacht:
    {
        "pakket_id": "slim_pakket",
        "bedrijf": { route, naam, email, stad, domein, kvk, ... },
        "vragen": { sector, stijl, doelen, klanten, uitstraling, huisstijl, activiteiten },
        "stijl": "glossier" of "verrassing",
        "services": { fotos, agent, extras }
    }
    """
    
    bedrijf   = wizard_data.get("bedrijf", {})
    vragen    = wizard_data.get("vragen", {})
    stijl_id  = wizard_data.get("stijl", "stripe")
    services  = wizard_data.get("services", {})
    pakket_id = wizard_data.get("pakket_id", "slim_pakket")
    
    # Bedrijfsnaam uit juiste route
    route = bedrijf.get("route", "beschrijf")
    if route == "verrassing":
        naam = bedrijf.get("bedrijfsnaam", "Mijn Bedrijf")
        branche = bedrijf.get("branche", "")
        beschrijving = f"{naam} — {branche}"
        if bedrijf.get("uniek"):
            beschrijving += f". {bedrijf['uniek']}"
    else:
        naam = bedrijf.get("naam", "Mijn Bedrijf")
        beschrijving = bedrijf.get("tekst", "") or bedrijf.get("aanvulling", "")
    
    email  = bedrijf.get("email", "")
    stad   = bedrijf.get("stad", "")
    domein = bedrijf.get("domein", slugify(naam) + ".nl")
    kvk    = bedrijf.get("kvk", "")
    slug   = slugify(naam)
    
    # Template
    if stijl_id == "verrassing" or stijl_id not in TEMPLATE_MAP:
        stijl_id = "stripe"  # default fallback
    
    template    = TEMPLATE_MAP[stijl_id]
    design_conf = DESIGN_MAP[stijl_id]
    
    # Backend
    activiteiten = vragen.get("activiteiten", [])
    backend      = bepaal_backend(activiteiten)
    
    # Functionaliteit
    doelen       = vragen.get("doelen", [])
    functie      = bepaal_functionaliteit(activiteiten, doelen)
    
    # Agent
    agent_id     = services.get("agent", "geen")
    # Check of agent inbegrepen is in pakket
    inbegrepen_agents = {
        "snel_plus":     "agent_standaard",
        "slim_pakket":   "agent_standaard",
        "slim_deluxe":   "agent_pro",
        "studio_pakket": "agent_pro",
        "studio_deluxe": "agent_pro",
    }
    if pakket_id in inbegrepen_agents:
        agent_id = inbegrepen_agents[pakket_id]
    
    agent_conf = AGENT_MAP.get(agent_id, AGENT_MAP["geen"])
    
    # Extras
    extras = services.get("extras", [])
    fotos  = services.get("fotos", "later")
    
    # Prijzen
    prijzen = bereken_prijzen(pakket_id, agent_id, extras, fotos)
    
    # Klant ID
    klant_id = f"klant-{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    spec = {
        "meta": {
            "spec_versie":   "1.0",
            "aangemaakt_op": datetime.now().isoformat(),
            "klant_id":      klant_id,
            "project_naam":  naam,
            "wizard_versie": "6.6",
        },
        "bedrijf": {
            "naam":          naam,
            "slug":          slug,
            "email":         email,
            "telefoon":      bedrijf.get("telefoon", ""),
            "adres":         "",
            "postcode":      "",
            "stad":          stad,
            "kvk":           kvk,
            "btw":           "",
            "beschrijving":  beschrijving,
            "tagline":       f"Welkom bij {naam}",
            "logo_url":      "",
            "website_url":   f"https://{domein}",
        },
        "frontend": {
            "template":  template["id"],
            "versie":    template["versie"],
            "type":      template["type"],
            "stijl_naam": stijl_id,
        },
        "design": {
            "niveau":        "standaard" if "slim" in pakket_id else ("basis" if "snel" in pakket_id else "premium"),
            "kleurpalet":    design_conf["kleurpalet"],
            "lettertype":    design_conf["lettertype"],
            "button_stijl":  design_conf["button_stijl"],
            "effect_overlay":design_conf["effect"],
            "custom_accent": None,
            "dark_mode":     False,
        },
        "backend": {
            "type":            backend["type"],
            "combinatie":      backend["combinatie"],
            "database":        "postgresql",
            "betaal_provider": "mollie",
        },
        "functionaliteit": functie,
        "agent": {
            "actief":  agent_conf["niveau"] != "geen",
            "type":    f"agent-{backend['type']}",
            "naam":    f"{naam} Agent",
            "niveau":  agent_conf["niveau"],
            "taken":   agent_conf["taken"],
        },
        "hosting": {
            "niveau":      "starter" if "snel" in pakket_id else ("standaard" if "slim" in pakket_id else "premium"),
            "provider":    "transip",
            "server_ip":   "",
            "ssh_user":    "",
            "ssh_key_path":"",
        },
        "domein": {
            "naam":      domein,
            "registrar": "transip",
            "ssl":       True,
        },
        "content": {
            "fotos_type":    fotos,
            "fotos_urls":    [],
            "eigen_teksten": False,
            "taal":          "nl",
            "sector":        vragen.get("sector", ""),
            "stijl":         vragen.get("stijl", ""),
            "doelen":        doelen,
            "klanten":       vragen.get("klanten", []),
        },
        "extra_services": {
            "seo_pro":        "seo_pro" in extras,
            "ai_zichtbaar":   "ai_zichtbaar" in extras,
            "social_media":   "social_media" in extras,
            "onderhoud":      "onderhoud" in extras,
            "backup":         "backup" in extras,
            "logo_ontwerp":   "logo" in extras,
            "google_biz":     "google_biz" in extras,
            "product_invoer": "product_invoer" in extras,
        },
        "prijzen": prijzen,
    }
    
    return spec


def sla_spec_op(spec: dict, uitvoer_map: str = ".") -> str:
    """Slaat spec op als JSON bestand, geeft pad terug"""
    slug = spec["bedrijf"]["slug"]
    klant_id = spec["meta"]["klant_id"]
    bestandsnaam = f"{klant_id}.json"
    pad = Path(uitvoer_map) / bestandsnaam
    pad.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pad, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    return str(pad)


if __name__ == "__main__":
    # Test met voorbeeld data
    test_data = {
        "pakket_id": "slim_pakket",
        "bedrijf": {
            "route": "beschrijf",
            "naam": "Bakkerij De Vries",
            "email": "info@bakkerijdevries.nl",
            "stad": "Amsterdam",
            "domein": "bakkerijdevries.nl",
            "kvk": "12345678",
            "telefoon": "020-1234567",
            "tekst": "Wij zijn een biologische bakkerij in Amsterdam-West met verse producten en online bestellingen"
        },
        "vragen": {
            "activiteiten": ["kopen", "afspraak"],
            "sector": "food",
            "stijl": "warm",
            "doelen": ["omzet", "bereikbaar"],
            "klanten": ["lokaal", "nationaal"],
            "uitstraling": ["vertrouwen", "persoonlijk"],
            "huisstijl": "nee"
        },
        "stijl": "glossier",
        "services": {
            "fotos": "stock",
            "agent": "agent_standaard",
            "extras": ["seo_pro", "google_biz"]
        }
    }
    
    spec = wizard_naar_spec(test_data)
    pad = sla_spec_op(spec, "/tmp")
    print(f"✅ Test spec opgeslagen: {pad}")
    print(json.dumps(spec, indent=2, ensure_ascii=False)[:500] + "...")
