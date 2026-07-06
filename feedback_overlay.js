
(function() {
  const API = window.WEBAPEX_API_URL || "http://localhost:8090";
  const KLANT_ID = window.WEBAPEX_KLANT_ID || "onbekend";
  let modus = null; // null, "elementen", "site"
  let geselecteerd = null;
  let wijzigingen = [];

  // ============================================
  // STIJLEN
  // ============================================
  const s = document.createElement("style");
  s.textContent = `
    #wa-fab {
      position: fixed; bottom: 28px; right: 28px; z-index: 99999;
      background: linear-gradient(135deg, #c9a96e, #a07840);
      color: #000; border: none; border-radius: 999px;
      padding: 13px 24px; font-size: 0.88rem; font-weight: 800;
      cursor: pointer; box-shadow: 0 8px 24px rgba(201,169,110,0.45);
      font-family: -apple-system, sans-serif; letter-spacing: -0.02em;
      transition: all 0.25s; display: flex; align-items: center; gap: 8px;
    }
    #wa-fab:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(201,169,110,0.55); }
    #wa-fab.stop { background: linear-gradient(135deg, #ef4444, #dc2626); color: #fff; box-shadow: 0 8px 24px rgba(239,68,68,0.4); }

    #wa-keuze-panel {
      position: fixed; bottom: 88px; right: 28px; z-index: 99999;
      background: #0f0f1a; border: 1px solid rgba(201,169,110,0.3);
      border-radius: 16px; padding: 16px; width: 280px;
      box-shadow: 0 24px 48px rgba(0,0,0,0.5);
      font-family: -apple-system, sans-serif;
      display: none;
    }
    #wa-keuze-panel.zichtbaar { display: block; }
    #wa-keuze-titel { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.14em; color: rgba(201,169,110,0.7); margin-bottom: 12px; }

    .wa-keuze-btn {
      width: 100%; padding: 14px 16px; margin-bottom: 8px;
      background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px; color: #fff; font-size: 0.83rem; font-weight: 700;
      cursor: pointer; font-family: inherit; text-align: left;
      transition: all 0.2s; display: flex; align-items: center; gap: 10px;
    }
    .wa-keuze-btn:hover { background: rgba(201,169,110,0.1); border-color: rgba(201,169,110,0.3); color: #c9a96e; }
    .wa-keuze-btn:last-child { margin-bottom: 0; }
    .wa-keuze-icoon { font-size: 1.2rem; flex-shrink: 0; }
    .wa-keuze-info { display: flex; flex-direction: column; gap: 2px; }
    .wa-keuze-sub { font-size: 0.7rem; color: rgba(255,255,255,0.4); font-weight: 400; }

    #wa-balk {
      position: fixed; top: 0; left: 0; right: 0; z-index: 99998;
      background: rgba(10,10,15,0.96); backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(201,169,110,0.2);
      padding: 11px 28px; display: none;
      align-items: center; justify-content: space-between;
      font-family: -apple-system, sans-serif; font-size: 0.8rem;
    }
    #wa-balk.zichtbaar { display: flex; }
    #wa-balk-info { display: flex; align-items: center; gap: 10px; color: rgba(255,255,255,0.6); }
    #wa-balk-dot { width: 7px; height: 7px; border-radius: 50%; background: #c9a96e; animation: wa-puls 1.5s ease-in-out infinite; }
    #wa-teller { background: rgba(201,169,110,0.15); color: #c9a96e; border-radius: 999px; padding: 2px 10px; font-size: 0.7rem; font-weight: 700; display: none; }
    #wa-opslaan { background: #c9a96e; color: #000; border: none; border-radius: 8px; padding: 7px 18px; font-size: 0.78rem; font-weight: 800; cursor: pointer; font-family: inherit; transition: all 0.2s; }
    #wa-opslaan:hover { opacity: 0.88; }
    #wa-opslaan:disabled { opacity: 0.3; cursor: not-allowed; }

    @keyframes wa-puls { 0%,100%{box-shadow:0 0 0 0 rgba(201,169,110,0.4)} 50%{box-shadow:0 0 0 6px rgba(201,169,110,0)} }

    .wa-hover { outline: 2px dashed rgba(201,169,110,0.5) !important; outline-offset: 3px !important; cursor: pointer !important; }
    .wa-hover:hover { outline: 2px solid #c9a96e !important; background: rgba(201,169,110,0.05) !important; }

    #wa-popup {
      position: fixed;
      bottom: 88px;
      right: 28px;
      z-index: 99999;
      background: #0f0f1a;
      border: 1px solid rgba(201,169,110,0.35);
      border-radius: 16px;
      padding: 20px;
      width: 320px;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 24px 48px rgba(0,0,0,0.6);
      font-family: -apple-system, sans-serif;
      display: none;
    }
    #wa-popup.zichtbaar { display: block; }
    #wa-popup-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    #wa-popup-titel { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.14em; color: #c9a96e; }
    #wa-popup-x { background: rgba(255,255,255,0.07); border: none; color: rgba(255,255,255,0.5); width: 22px; height: 22px; border-radius: 6px; cursor: pointer; font-size: 0.7rem; }
    #wa-popup-x:hover { color: #fff; background: rgba(255,255,255,0.14); }
    #wa-popup-el { font-size: 0.72rem; color: rgba(255,255,255,0.35); margin-bottom: 8px; }
    #wa-popup-huidig { font-size: 0.78rem; color: rgba(255,255,255,0.55); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; font-style: italic; }
    #wa-popup-tips { font-size: 0.7rem; color: rgba(201,169,110,0.7); background: rgba(201,169,110,0.06); border: 1px solid rgba(201,169,110,0.12); border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; line-height: 1.6; }
    #wa-popup-input {
      width: 100%; background: rgba(255,255,255,0.06);
      border: 1.5px solid rgba(255,255,255,0.15); border-radius: 10px;
      padding: 10px 12px; color: #fff; font-size: 0.85rem;
      font-family: inherit; resize: none; height: 80px;
      outline: none; margin-bottom: 12px; transition: border-color 0.2s;
      display: block; box-sizing: border-box;
    }
    #wa-popup-input:focus { border-color: rgba(201,169,110,0.6); box-shadow: 0 0 0 3px rgba(201,169,110,0.08); }
    #wa-popup-input::placeholder { color: rgba(255,255,255,0.22); }
    #wa-popup-knoppen { display: grid; grid-template-columns: 1fr 2fr; gap: 8px; }
    #wa-popup-annuleer {
      background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.55);
      border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
      padding: 11px; font-size: 0.8rem; font-weight: 600;
      cursor: pointer; font-family: inherit; transition: all 0.15s;
    }
    #wa-popup-annuleer:hover { color: #fff; border-color: rgba(255,255,255,0.25); }
    #wa-popup-pas-aan {
      background: linear-gradient(135deg, #c9a96e, #a07840);
      color: #000; border: none; border-radius: 8px;
      padding: 11px; font-size: 0.85rem; font-weight: 800;
      cursor: pointer; font-family: inherit; transition: all 0.2s;
      letter-spacing: -0.01em;
    }
    #wa-popup-pas-aan:hover { opacity: 0.88; transform: translateY(-1px); }
    #wa-popup-pas-aan:disabled { opacity: 0.4; cursor: wait; transform: none; }
    #wa-popup-hint { font-size: 0.62rem; color: rgba(255,255,255,0.18); text-align: center; margin-top: 8px; }

    /* SITE VERVANGEN PANEL */
    #wa-site-panel {
      position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
      z-index: 99999; background: #0f0f1a;
      border: 1px solid rgba(201,169,110,0.3);
      border-radius: 20px; padding: 28px; width: 420px;
      box-shadow: 0 32px 64px rgba(0,0,0,0.7);
      font-family: -apple-system, sans-serif; display: none;
    }
    #wa-site-panel.zichtbaar { display: block; }
    #wa-site-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 99998; display: none; backdrop-filter: blur(4px); }
    #wa-site-overlay.zichtbaar { display: block; }
    #wa-site-titel { font-size: 1rem; font-weight: 900; letter-spacing: -0.03em; margin-bottom: 6px; }
    #wa-site-sub { font-size: 0.8rem; color: rgba(255,255,255,0.45); margin-bottom: 20px; line-height: 1.6; }
    .wa-site-optie { padding: 14px 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s; }
    .wa-site-optie:hover { background: rgba(201,169,110,0.08); border-color: rgba(201,169,110,0.25); }
    .wa-site-optie.geselecteerd { background: rgba(201,169,110,0.1); border-color: rgba(201,169,110,0.4); }
    .wa-site-optie-naam { font-size: 0.85rem; font-weight: 700; margin-bottom: 3px; }
    .wa-site-optie-desc { font-size: 0.72rem; color: rgba(255,255,255,0.4); }
    .wa-site-optie.geselecteerd .wa-site-optie-desc { color: rgba(201,169,110,0.6); }
    #wa-site-input { width: 100%; background: rgba(255,255,255,0.06); border: 1.5px solid rgba(255,255,255,0.12); border-radius: 10px; padding: 10px 12px; color: #fff; font-size: 0.85rem; font-family: inherit; resize: none; height: 80px; outline: none; margin: 14px 0; transition: border-color 0.2s; display: block; box-sizing: border-box; }
    #wa-site-input:focus { border-color: rgba(201,169,110,0.5); }
    #wa-site-input::placeholder { color: rgba(255,255,255,0.22); }
    #wa-site-knoppen { display: grid; grid-template-columns: 1fr 2fr; gap: 10px; }
    #wa-site-annuleer { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; font-size: 0.82rem; font-weight: 600; cursor: pointer; font-family: inherit; }
    #wa-site-annuleer:hover { color: #fff; }
    #wa-site-verstuur { background: linear-gradient(135deg, #c9a96e, #a07840); color: #000; border: none; border-radius: 8px; padding: 12px; font-size: 0.85rem; font-weight: 800; cursor: pointer; font-family: inherit; transition: all 0.2s; }
    #wa-site-verstuur:hover { opacity: 0.88; }

    #wa-ai-bezig { position: fixed; bottom: 88px; right: 28px; z-index: 99998; background: rgba(15,15,26,0.95); border: 1px solid rgba(201,169,110,0.2); border-radius: 12px; padding: 10px 16px; font-size: 0.75rem; font-family: inherit; color: #c9a96e; display: none; align-items: center; gap: 8px; backdrop-filter: blur(8px); }
    #wa-ai-bezig.zichtbaar { display: flex; }
    .wa-spinner { width: 14px; height: 14px; border: 2px solid rgba(201,169,110,0.2); border-top-color: #c9a96e; border-radius: 50%; animation: wa-spin 0.6s linear infinite; }
    @keyframes wa-spin { to { transform: rotate(360deg); } }

    #wa-succes { position: fixed; bottom: 88px; right: 28px; z-index: 99998; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.3); border-radius: 12px; padding: 10px 16px; font-size: 0.75rem; font-family: inherit; color: #34d399; display: none; align-items: center; gap: 8px; }
    #wa-succes.zichtbaar { display: flex; }
  `;
  document.head.appendChild(s);

  // ============================================
  // HTML
  // ============================================
  document.body.insertAdjacentHTML("beforeend", `
    <button id="wa-fab">✏️ Aanpassen</button>

    <div id="wa-keuze-panel">
      <div id="wa-keuze-titel">Wat wil je aanpassen?</div>
      <button class="wa-keuze-btn" id="wa-keuze-elementen">
        <span class="wa-keuze-icoon">🎯</span>
        <span class="wa-keuze-info">
          <span>Elementen aanpassen</span>
          <span class="wa-keuze-sub">Klik op tekst, afbeeldingen of secties om ze te wijzigen</span>
        </span>
      </button>
      <button class="wa-keuze-btn" id="wa-keuze-site">
        <span class="wa-keuze-icoon">🔄</span>
        <span class="wa-keuze-info">
          <span>Gehele website vervangen</span>
          <span class="wa-keuze-sub">Andere stijl, andere opzet of volledig nieuw design</span>
        </span>
      </button>
    </div>

    <div id="wa-balk">
      <div id="wa-balk-info">
        <div id="wa-balk-dot"></div>
        <span>Klik op een element om het aan te passen</span>
        <span id="wa-teller"></span>
      </div>
      <button id="wa-opslaan" disabled>✓ Opslaan</button>
    </div>

    <div id="wa-popup">
      <div id="wa-popup-head">
        <div id="wa-popup-titel">Wat wil je veranderen?</div>
        <button id="wa-popup-x">✕</button>
      </div>
      <div id="wa-popup-el"></div>
      <div id="wa-popup-huidig"></div>
      <div id="wa-popup-tips"></div>
      <textarea id="wa-popup-input" placeholder="Bijv: Verander naar 'Verse broden elke dag' of 'Maak het blauw' of 'Verwijder dit'"></textarea>
      <div id="wa-popup-knoppen">
        <button id="wa-popup-annuleer">Annuleer</button>
        <button id="wa-popup-pas-aan">⚡ Pas aan</button>
      </div>
      <div id="wa-popup-hint">Ctrl+Enter om snel toe te passen</div>
    </div>

    <div id="wa-site-overlay"></div>
    <div id="wa-site-panel">
      <div id="wa-site-titel">Website vervangen</div>
      <div id="wa-site-sub">Wat klopt er niet aan de huidige stijl? Wij bouwen een nieuwe versie op basis van jouw feedback.</div>
      <div class="wa-site-optie" data-waarde="De stijl past niet bij mijn merk">
        <div class="wa-site-optie-naam">🎨 Stijl past niet bij mijn merk</div>
        <div class="wa-site-optie-desc">Kleuren, typografie of algehele uitstraling klopt niet</div>
      </div>
      <div class="wa-site-optie" data-waarde="De opbouw van de pagina klopt niet">
        <div class="wa-site-optie-naam">📐 Opbouw van de pagina klopt niet</div>
        <div class="wa-site-optie-desc">Secties staan in de verkeerde volgorde of missen</div>
      </div>
      <div class="wa-site-optie" data-waarde="Ik wil een compleet andere stijl">
        <div class="wa-site-optie-naam">🔄 Ik wil een compleet andere stijl</div>
        <div class="wa-site-optie-desc">Begin opnieuw met een andere template richting</div>
      </div>
      <div class="wa-site-optie" data-waarde="De website voelt niet professioneel genoeg">
        <div class="wa-site-optie-naam">💼 Voelt niet professioneel genoeg</div>
        <div class="wa-site-optie-desc">Te simpel, te druk of niet passend bij mijn doelgroep</div>
      </div>
      <textarea id="wa-site-input" placeholder="Beschrijf wat je anders wilt zien — hoe meer detail hoe beter het resultaat..."></textarea>
      <div id="wa-site-knoppen">
        <button id="wa-site-annuleer">Annuleer</button>
        <button id="wa-site-verstuur">🔄 Nieuwe versie aanvragen</button>
      </div>
    </div>

    <div id="wa-ai-bezig"><div class="wa-spinner"></div> AI verwerkt...</div>
    <div id="wa-succes">✓ Wijziging doorgevoerd</div>
  `);

  // ============================================
  // REFERENTIES
  // ============================================
  const fab         = document.getElementById("wa-fab");
  const keuzePaneel = document.getElementById("wa-keuze-panel");
  const keuzeEl     = document.getElementById("wa-keuze-elementen");
  const keuzeSite   = document.getElementById("wa-keuze-site");
  const balk        = document.getElementById("wa-balk");
  const teller      = document.getElementById("wa-teller");
  const opslaan     = document.getElementById("wa-opslaan");
  const popup       = document.getElementById("wa-popup");
  const popupX      = document.getElementById("wa-popup-x");
  const popupEl     = document.getElementById("wa-popup-el");
  const popupHuidig = document.getElementById("wa-popup-huidig");
  const popupTips   = document.getElementById("wa-popup-tips");
  const popupInput  = document.getElementById("wa-popup-input");
  const popupAnnuleer = document.getElementById("wa-popup-annuleer");
  const popupPasAan = document.getElementById("wa-popup-pas-aan");
  const siteOverlay = document.getElementById("wa-site-overlay");
  const sitePanel   = document.getElementById("wa-site-panel");
  const siteAnnuleer = document.getElementById("wa-site-annuleer");
  const siteVerstuur = document.getElementById("wa-site-verstuur");
  const siteInput   = document.getElementById("wa-site-input");
  const aiBezig     = document.getElementById("wa-ai-bezig");
  const succes      = document.getElementById("wa-succes");

  // ============================================
  // FAB — KEUZE MENU
  // ============================================
  fab.addEventListener("click", () => {
    if (modus) {
      stopModus();
      return;
    }
    keuzePaneel.classList.toggle("zichtbaar");
  });

  keuzeEl.addEventListener("click", () => {
    keuzePaneel.classList.remove("zichtbaar");
    startElementenModus();
  });

  keuzeSite.addEventListener("click", () => {
    keuzePaneel.classList.remove("zichtbaar");
    openSitePanel();
  });

  // Klik buiten keuze paneel — met kleine delay zodat FAB click eerst verwerkt wordt
  document.addEventListener("click", (e) => {
    setTimeout(() => {
      if (!fab.contains(e.target) && !keuzePaneel.contains(e.target)) {
        keuzePaneel.classList.remove("zichtbaar");
      }
    }, 150);
  });

  // ============================================
  // STOP MODUS
  // ============================================
  function stopModus() {
    modus = null;
    fab.innerHTML = "✏️ Aanpassen";
    fab.classList.remove("stop");
    balk.classList.remove("zichtbaar");
    sluitPopup();
    document.querySelectorAll(".wa-hover").forEach(el => {
      el.classList.remove("wa-hover");
      el.removeEventListener("click", klikHandler);
    });
  }

  // ============================================
  // ELEMENTEN MODUS
  // ============================================
  function startElementenModus() {
    modus = "elementen";
    fab.innerHTML = "✕ Stop aanpassen";
    fab.classList.add("stop");
    balk.classList.add("zichtbaar");

    document.querySelectorAll("h1,h2,h3,h4,p,a,button,img").forEach(el => {
      if (el.closest("[id^='wa-']")) return;
      if (!el.innerText && el.tagName !== "IMG") return;
      el.classList.add("wa-hover");
      el.addEventListener("click", klikHandler);
    });
  }

  function klikHandler(e) {
    e.preventDefault();
    e.stopPropagation();
    geselecteerd = e.currentTarget;
    toonPopup(geselecteerd);
  }

  // ============================================
  // POPUP
  // ============================================
  function toonPopup(el) {
    const tag = el.tagName.toLowerCase();
    const huidig = tag === "img" ? "(afbeelding)" : el.innerText.trim().slice(0, 80);

    popupEl.textContent = tag + " element";
    popupHuidig.textContent = huidig ? `"${huidig}${huidig.length >= 80 ? "..." : ""}"` : "";

    // Tips per type
    const tipsMap = {
      h1: "✏️ Andere hoofdtekst  ·  🔤 Kortere versie  ·  🎯 Andere toon",
      h2: "✏️ Andere tussentitel  ·  ✂️ Maak het korter",
      p:  "✏️ Andere omschrijving  ·  ✂️ Korter  ·  ➕ Meer detail",
      a:  "✏️ Andere knoptekst  ·  🎨 Andere kleur",
      button: "✏️ Andere knoptekst  ·  🎨 Andere kleur",
      img: "🖼️ Andere afbeelding  ·  📸 Andere stijl stockfoto",
    };
    popupTips.textContent = tipsMap[tag] || "✏️ Aanpassen  ·  🗑️ Verwijderen";

    // Popup altijd rechtsonder — stabiel en altijd zichtbaar
    popup.classList.add("zichtbaar");
    popupInput.value = "";
    popupInput.focus();
  }

  function sluitPopup() {
    popup.classList.remove("zichtbaar");
    geselecteerd = null;
    popupInput.value = "";
  }

  popupX.addEventListener("click", sluitPopup);
  popupAnnuleer.addEventListener("click", sluitPopup);

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { sluitPopup(); }
    if (e.key === "Enter" && e.ctrlKey && popup.classList.contains("zichtbaar")) {
      verwerkWijziging();
    }
  });

  // ============================================
  // VERWERK WIJZIGING — DIRECT LOKAAL
  // ============================================
  async function verwerkWijziging() {
    if (!geselecteerd || !popupInput.value.trim()) return;

    const instructie = popupInput.value.trim();
    const tag = geselecteerd.tagName.toLowerCase();
    const oud = tag === "img" ? geselecteerd.src : geselecteerd.innerText.trim();

    popupPasAan.disabled = true;
    popupPasAan.textContent = "⏳";
    sluitPopup();
    aiBezig.classList.add("zichtbaar");

    // DIRECT LOKAAL VERWERKEN — geen wachten op API
    const nieuw = verwerkInstructie(instructie, oud, tag);
    pasElAan(geselecteerd, nieuw, tag);
    registreer(geselecteerd, oud, nieuw, instructie);

    // API op achtergrond proberen (geen await)
    fetch(`${API}/feedback/verwerk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ klant_id: KLANT_ID, element_tag: tag, huidige_waarde: oud, instructie }),
      signal: AbortSignal.timeout(5000)
    }).catch(() => {});

    aiBezig.classList.remove("zichtbaar");
    popupPasAan.disabled = false;
    popupPasAan.textContent = "⚡ Pas aan";
    toonSucces();
  }

  // ============================================
  // LOKALE INSTRUCTIE VERWERKING
  // ============================================
  function verwerkInstructie(instructie, oud, tag) {
    const inst = instructie.toLowerCase().trim();

    // Verwijder
    if (inst.match(/^(verwijder|weg|delete|verberg|hide)/)) return "__verwijder__";

    // Directe vervanging patronen
    const patronen = [
      /^verander naar[:\s]+(.+)/i,
      /^maak het[:\s]+(.+)/i,
      /^nieuwe tekst[:\s]+(.+)/i,
      /^zet[:\s]+(.+)/i,
      /^tekst[:\s]+(.+)/i,
    ];
    for (const p of patronen) {
      const match = instructie.match(p);
      if (match) return match[1].trim();
    }

    // Kleur aanpassingen — stijl
    if (inst.includes("blauw")) { geselecteerd.style.color = "#3b82f6"; return oud; }
    if (inst.includes("rood")) { geselecteerd.style.color = "#ef4444"; return oud; }
    if (inst.includes("groen")) { geselecteerd.style.color = "#22c55e"; return oud; }
    if (inst.includes("goud")) { geselecteerd.style.color = "#c9a96e"; return oud; }
    if (inst.includes("wit")) { geselecteerd.style.color = "#ffffff"; return oud; }
    if (inst.includes("zwart")) { geselecteerd.style.color = "#000000"; return oud; }
    if (inst.includes("groter")) { geselecteerd.style.fontSize = "120%"; return oud; }
    if (inst.includes("kleiner")) { geselecteerd.style.fontSize = "80%"; return oud; }
    if (inst.includes("vet") || inst.includes("bold")) { geselecteerd.style.fontWeight = "900"; return oud; }

    // Anders: gebruik de instructie direct als nieuwe tekst
    return instructie;
  }

  function pasElAan(el, nieuw, tag) {
    if (nieuw === "__verwijder__") {
      el.style.opacity = "0.3";
      el.style.textDecoration = "line-through";
      return;
    }
    if (tag === "img") {
      el.alt = nieuw;
    } else if (nieuw !== el.innerText) {
      el.innerText = nieuw;
    }
    // Highlight
    el.style.transition = "background 0.3s ease";
    el.style.background = "rgba(201,169,110,0.12)";
    setTimeout(() => el.style.background = "", 1500);
  }

  popupPasAan.addEventListener("click", verwerkWijziging);

  // ============================================
  // OPSLAAN
  // ============================================
  function registreer(el, oud, nieuw, instructie) {
    wijzigingen.push({ tijdstip: new Date().toISOString(), element: el.tagName, oud, nieuw, instructie });
    teller.textContent = `${wijzigingen.length} wijziging${wijzigingen.length !== 1 ? "en" : ""}`;
    teller.style.display = "inline";
    opslaan.disabled = false;
  }

  opslaan.addEventListener("click", async () => {
    opslaan.disabled = true;
    opslaan.textContent = "Opslaan...";
    try {
      await fetch(`${API}/feedback/opslaan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ klant_id: KLANT_ID, wijzigingen }),
        signal: AbortSignal.timeout(5000)
      });
    } catch(e) {
      localStorage.setItem(`wa_${KLANT_ID}`, JSON.stringify(wijzigingen));
    }
    opslaan.textContent = "✓ Opgeslagen";
    wijzigingen = [];
    teller.style.display = "none";
    setTimeout(() => { opslaan.textContent = "✓ Opslaan"; opslaan.disabled = true; }, 3000);
  });

  // ============================================
  // SITE VERVANGEN PANEL
  // ============================================
  let siteSelectie = "";

  function openSitePanel() {
    sitePanel.classList.add("zichtbaar");
    siteOverlay.classList.add("zichtbaar");
  }

  function sluitSitePanel() {
    sitePanel.classList.remove("zichtbaar");
    siteOverlay.classList.remove("zichtbaar");
    siteInput.value = "";
    siteSelectie = "";
    document.querySelectorAll(".wa-site-optie").forEach(o => o.classList.remove("geselecteerd"));
  }

  siteOverlay.addEventListener("click", sluitSitePanel);
  siteAnnuleer.addEventListener("click", sluitSitePanel);

  document.querySelectorAll(".wa-site-optie").forEach(optie => {
    optie.addEventListener("click", () => {
      document.querySelectorAll(".wa-site-optie").forEach(o => o.classList.remove("geselecteerd"));
      optie.classList.add("geselecteerd");
      siteSelectie = optie.dataset.waarde;
      siteInput.value = siteSelectie + ". ";
      siteInput.focus();
    });
  });

  siteVerstuur.addEventListener("click", async () => {
    const feedback = siteInput.value.trim();
    if (!feedback) { siteInput.focus(); return; }

    siteVerstuur.textContent = "Versturen...";
    siteVerstuur.disabled = true;

    try {
      await fetch(`${API}/feedback/opslaan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          klant_id: KLANT_ID,
          wijzigingen: [{ tijdstip: new Date().toISOString(), type: "site_vervangen", instructie: feedback }]
        }),
        signal: AbortSignal.timeout(5000)
      });
    } catch(e) {}

    sluitSitePanel();
    siteVerstuur.textContent = "🔄 Nieuwe versie aanvragen";
    siteVerstuur.disabled = false;
    toonSucces("✓ Aanvraag verstuurd — wij gaan aan de slag!");
  });

  // ============================================
  // SUCCES
  // ============================================
  function toonSucces(tekst = "✓ Wijziging doorgevoerd") {
    succes.textContent = tekst;
    succes.classList.add("zichtbaar");
    setTimeout(() => succes.classList.remove("zichtbaar"), 2500);
  }

  console.log("✅ WebApex Live Feedback v2 — klaar");
})();
