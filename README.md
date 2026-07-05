# WebApex Forge Engine

Het assemblage brein van WebApex.
Forge kloont de juiste templates, vult placeholders in en deployt de complete website.

## Workflow
1. clone_templates.py    — haalt juiste repos op van GitHub
2. fill_placeholders.py  — vervangt {{PLACEHOLDERS}} met klantdata
3. apply_design.py       — past kleuren, fonts en effect overlay toe
4. assemble.py           — combineert frontend + backend + admin + agent
5. deploy.sh             — deployt op hosting via Docker

## Input
Een website_spec.json gegenereerd door de WebApex wizard

## Output
Een volledig werkende website op de hosting van de klant
