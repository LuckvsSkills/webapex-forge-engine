# WebApex — Klant Aanpassingen Proces

## Overzicht
KLANT OPENT PREVIEW URL
↓
✏️ Aanpassen knop
↓
┌─────┴──────┐
↓            ↓
Elementen    Gehele site
aanpassen    vervangen
↓            ↓
Direct       Aanvraag
zichtbaar    naar ons
↓
Opgeslagen
↓
Patcher verwerkt
↓
Permanent in HTML

---

## Laag 1 — Directe aanpassingen (geen tokens)

### Wat de klant kan aanpassen:

| Categorie | Voorbeelden | Hoe |
|-----------|-------------|-----|
| Tekst | Andere headline, omschrijving | Direct in browser |
| Tekstkleur | Blauw, rood, goud, #hex | CSS style |
| Achtergrond | Kleur van sectie of element | CSS style |
| Grootte | Groter, kleiner, 150% | CSS font-size |
| Stijl | Vetgedrukt, cursief, onderstreept | CSS font-weight |
| Verwijder | Element verbergen | CSS display:none |
| Afbeelding | Andere stockfoto of upload | Zie media flow |
| Video | Andere video URL of upload | Zie media flow |

### Stroom:

Klant klikt op element
Popup: kies categorie
Klant kiest optie of typt instructie
Browser past DIRECT aan (zichtbaar)
Wijziging → wijzigingen.json
Patcher verwerkt → permanent in HTML
Geen tokens gebruikt


---

## Laag 2 — AI aanpassingen (tokens, max 3/sessie)

### Wanneer AI nodig is:

| Verzoek | Waarom AI |
|---------|-----------|
| "Schrijf een betere over ons tekst" | Content generatie |
| "Maak deze tekst professioneler" | Tekst verbetering |
| "Vertaal naar Engels" | Vertaling |
| "Genereer nieuwe productnamen" | Content generatie |
| "Schrijf een SEO beschrijving" | Content generatie |

### Stroom:

Klant typt complex verzoek
Systeem herkent: AI nodig
Check: max 3 AI verzoeken bereikt?
→ Ja: "Aanvraag ingediend — 24u"
→ Nee: Claude aanroepen (Haiku = goedkoop)
Resultaat direct tonen
Opgeslagen + verwerkt


### Kosten schatting:
Claude Haiku = ~$0.001 per aanvraag
Max 3/sessie = $0.003 per klant sessie
Gemiddeld 10 sessies per maand = $0.03/maand per klant
100 klanten = $3/maand totaal
→ Verwaarloosbaar

---

## Laag 3 — Media aanpassingen

### Afbeeldingen:
OPTIE A — Stockfoto vervangen
Klant: "Andere afbeelding" → klik op afbeelding
→ Popup: zoek stockfoto (wij zoeken via Unsplash API)
→ Preview 4 opties
→ Klant kiest → direct zichtbaar
→ Gratis (Unsplash free tier)
OPTIE B — Eigen foto uploaden
Klant: "Upload eigen foto"
→ File picker opent
→ Upload naar /uploads/ op server
→ Afbeelding URL vervangen in HTML
→ Gratis
OPTIE C — AI foto genereren
Klant: "Genereer afbeelding van..."
→ Naar AI image API (Stable Diffusion/DALL-E)
→ Kosten: ~$0.04 per afbeelding
→ Max 2 per sessie

### Video:
OPTIE A — YouTube/Vimeo URL
Klant: plakt YouTube link
→ Wij zetten om naar embed code
→ Vervangt placeholder of bestaande video
→ Gratis
OPTIE B — Eigen video uploaden
Klant: uploadt MP4
→ Sla op in /uploads/videos/
→ Video tag updaten in HTML
→ Gratis (opslagkosten server)

---

## Laag 4 — Gehele site vervangen

### Wanneer:
Klant is niet tevreden met:

Algehele stijl/uitstraling
Opbouw van de pagina
Template keuze


### Stroom:

Klant kiest "Gehele website vervangen"
Kiest reden + beschrijving
Aanvraag → onze database
Wij ontvangen notificatie (email/Telegram)
Wij beoordelen:
→ Binnen pakket gratis? (1x per jaar)
→ Extra: €99 redesign fee
Wij draaien Forge opnieuw met nieuwe template
Klant krijgt nieuwe preview URL
Klant keurt goed → live


---

## Technische Stroom — Volledig
BROWSER (klant)
↓ wijziging
feedback_overlay.js
↓ POST /feedback/verwerk of /feedback/opslaan
feedback_server.py (poort 8090)
↓ opslaan
wijzigingen.json
↓ trigger (direct of via cron)
patch_website.py
↓ verwerkt
index.html (permanent)
↓
Website herstart (docker-compose restart)
↓
Klant ziet permanente wijziging

---

## Token Budget per Klant
Snel pakket:    5 AI verzoeken/maand
Slim pakket:   15 AI verzoeken/maand
Studio pakket: onbeperkt (kosten verrekend)
AI Agent Standaard: 50 agent taken/maand
AI Agent Pro:      200 agent taken/maand

---

## Te Bouwen (volgorde)
✅ feedback_overlay.js     — klant UI
✅ feedback_server.py      — API
✅ patch_website.py        — permanente verwerking
✅ wizard_to_spec.py       — wizard → forge
⏳ media_handler.py        — afbeelding/video upload
⏳ stockfoto_zoeker.py     — Unsplash integratie
⏳ ai_rewrite.py           — complexe tekst verzoeken
⏳ notificatie_service.py  — email/Telegram alerts
⏳ token_budget.py         — budget bewaking
⏳ site_vervang_flow.py    — volledige site vervangen
