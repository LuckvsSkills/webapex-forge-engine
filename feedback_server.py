#!/usr/bin/env python3
"""
WebApex Feedback API Server
Ontvangt live feedback van klanten en verwerkt via AI
Draait op poort 8090
"""

import json
import os
import re
import urllib.request
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path


KLANTEN_MAP = Path("/tmp/forge-output")
ANTHROPIC_KEY = ""

# Probeer API key ophalen
config_pad = Path.home() / ".openclaw" / "gateway.systemd.env"
if config_pad.exists():
    for line in config_pad.read_text().splitlines():
        if "ANTHROPIC_API_KEY" in line:
            ANTHROPIC_KEY = line.split("=", 1)[1].strip().strip('"')
            break


def ai_verwerk_instructie(element_info: dict) -> dict:
    """Verwerk feedback instructie via Claude"""
    if not ANTHROPIC_KEY:
        return verwerk_lokaal(element_info)

    prompt = f"""Je bent een website editor die instructies van een klant verwerkt.

Element: {element_info["element_tag"]} .{element_info.get("element_klasse", "")}
Huidige waarde: {element_info["huidige_waarde"][:200]}
Instructie van klant: {element_info["instructie"]}

Geef een JSON terug met:
{{
  "type": "tekst" of "verwijder" of "stijl",
  "nieuwe_waarde": "de nieuwe tekst of waarde",
  "uitleg": "wat je hebt veranderd"
}}

Interpreteer de instructie letterlijk en praktisch.
Als de klant een kleur wil veranderen, geef dan de hex kleurcode als nieuwe_waarde.
Als de klant tekst wil veranderen, geef dan de nieuwe tekst.
Schrijf ALLEEN het JSON object."""

    try:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            tekst = result["content"][0]["text"]
            match = re.search(r"\{[\s\S]+\}", tekst)
            if match:
                return json.loads(match.group())
    except Exception as e:
        print(f"  ⚠️  AI fout: {e}")

    return verwerk_lokaal(element_info)


def verwerk_lokaal(element_info: dict) -> dict:
    """Lokale verwerking zonder AI"""
    instructie = element_info["instructie"].lower()
    huidige = element_info["huidige_waarde"]

    if any(w in instructie for w in ["verwijder", "weg", "delete", "hide"]):
        return {"type": "verwijder", "nieuwe_waarde": "", "uitleg": "Element verwijderd"}

    # Directe tekst vervanging patronen
    for prefix in ["verander naar ", "maak ", "zet het op ", "nieuwe tekst: "]:
        if instructie.startswith(prefix):
            nieuw = element_info["instructie"][len(prefix):].strip()
            return {"type": "tekst", "nieuwe_waarde": nieuw, "uitleg": f"Tekst aangepast naar: {nieuw}"}

    return {"type": "tekst", "nieuwe_waarde": element_info["instructie"], "uitleg": "Tekst vervangen"}


def sla_wijzigingen_op(klant_id: str, wijzigingen: list):
    """Sla wijzigingen op in JSON bestand"""
    klant_map = KLANTEN_MAP / f"client-{klant_id.replace('klant-', '')}"
    if not klant_map.exists():
        # Zoek op naam
        voor_match = [d for d in KLANTEN_MAP.iterdir() if klant_id.replace("klant-", "").split("-2026")[0] in d.name]
        klant_map = voor_match[0] if voor_match else KLANTEN_MAP

    wijzigingen_pad = klant_map / "wijzigingen.json"
    bestaand = []
    if wijzigingen_pad.exists():
        bestaand = json.loads(wijzigingen_pad.read_text())

    bestaand.extend(wijzigingen)
    wijzigingen_pad.write_text(json.dumps(bestaand, indent=2, ensure_ascii=False))
    print(f"  💾 {len(wijzigingen)} wijzigingen opgeslagen voor {klant_id}")


class FeedbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Stil logging

    def stuur_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        lengte = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(lengte).decode("utf-8"))

        if self.path == "/feedback/verwerk":
            print(f"  🔧 Verwerk: {body.get('instructie', '')[:50]}")
            resultaat = ai_verwerk_instructie(body)
            self.stuur_json(resultaat)

        elif self.path == "/feedback/opslaan":
            klant_id = body.get("klant_id", "onbekend")
            wijzigingen = body.get("wijzigingen", [])
            sla_wijzigingen_op(klant_id, wijzigingen)
            # Direct patchen na opslaan
            try:
                import subprocess
                klant_map = None
                for map in Path("/tmp/forge-output").iterdir():
                    if klant_id.replace("klant-", "").split("-2026")[0] in map.name:
                        klant_map = map
                        break
                if klant_map:
                    subprocess.Popen([
                        "python3",
                        "/home/prime/arc_ai_angels/projects/website_factory/forge-engine/patch_website.py",
                        str(klant_map)
                    ])
            except Exception as e:
                print(f"  ⚠️  Auto-patch fout: {e}")
            self.stuur_json({"status": "opgeslagen", "aantal": len(wijzigingen)})

        elif self.path == "/media/stockfotos":
            zoekopdracht = body.get("zoekopdracht", "")
            try:
                import sys
                sys.path.insert(0, "/home/prime/arc_ai_angels/projects/website_factory/forge-engine")
                from media_handler import zoek_stockfotos
                fotos = zoek_stockfotos(zoekopdracht, 4)
                self.stuur_json({"fotos": fotos})
            except Exception as e:
                self.stuur_json({"error": str(e)}, 500)

        elif self.path == "/media/video":
            url = body.get("url", "")
            try:
                from media_handler import verwerk_video_url
                resultaat = verwerk_video_url(url)
                self.stuur_json(resultaat)
            except Exception as e:
                self.stuur_json({"error": str(e)}, 500)

        else:
            self.stuur_json({"error": "Onbekend endpoint"}, 404)

    def do_GET(self):
        if self.path == "/status":
            self.stuur_json({"status": "actief", "versie": "1.0"})
        else:
            self.stuur_json({"error": "Niet gevonden"}, 404)


if __name__ == "__main__":
    poort = 8090
    server = HTTPServer(("0.0.0.0", poort), FeedbackHandler)
    print(f"""
╔══════════════════════════════════════╗
║   WebApex Feedback API Server        ║
║   Poort: {poort}                        ║
╚══════════════════════════════════════╝

  ✅ Server actief op http://localhost:{poort}
  → POST /feedback/verwerk  — AI verwerking
  → POST /feedback/opslaan  — Wijzigingen opslaan
  → GET  /status            — Server status

  Ctrl+C om te stoppen
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server gestopt")
