import streamlit as st
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError

st.set_page_config(page_title="Fjällstugeagenten Jul 2026", page_icon="🏔️", layout="wide")

st.title("🏔️ Fjällstugor Julen 2026 (Live Webbsökning)")
st.caption("Agent som söker direkt på internet efter stugor med minst 6 bäddar från 23 december 2026 längs sträckan Romme – Östersund.")

# API-nyckelhantering med säker hantering
try:
    api_nyckel = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6LNmVMp4WfmbSk99Za53YLRxxpwsKP8mSNK-O-X5Gpvug")
except Exception:
    api_nyckel = "AQ.Ab8RN6LNmVMp4WfmbSk99Za53YLRxxpwsKP8mSNK-O-X5Gpvug"

# Referenskoordinater för skidorter och områden längs sträckan Romme till Östersund
skidorter_karta = [
    {"namn": "Romme Alpin", "omrade": "Södra Dalarna", "latitude": 60.3956, "longitude": 15.3526},
    {"namn": "Bjursås Berg & Sjö", "omrade": "Falun", "latitude": 60.7412, "longitude": 15.4419},
    {"namn": "Orsa Grönklitt", "omrade": "Siljansbygden", "latitude": 61.2132, "longitude": 14.5321},
    {"namn": "Kläppen", "omrade": "Sälenfjällen", "latitude": 61.0315, "longitude": 13.3421},
    {"namn": "Lindvallen / Högfjället", "omrade": "Sälenfjällen", "latitude": 61.1601, "longitude": 13.1970},
    {"namn": "Tandådalen / Hundfjället", "omrade": "Sälenfjällen", "latitude": 61.1812, "longitude": 13.0019},
    {"namn": "Stöten", "omrade": "Sälenfjällen", "latitude": 61.2671, "longitude": 12.8912},
    {"namn": "Idre Fjäll & Himmelfjäll", "omrade": "Norra Dalarna", "latitude": 61.8892, "longitude": 12.8315},
    {"namn": "Fjätervålen", "omrade": "Norra Dalarna", "latitude": 61.9312, "longitude": 12.9814},
    {"namn": "Lofsdalen", "omrade": "Härjedalen", "latitude": 62.1121, "longitude": 13.2798},
    {"namn": "Vemdalsskalet / Björnrike", "omrade": "Härjedalen", "latitude": 62.4795, "longitude": 13.9782},
    {"namn": "Klövsjö / Storhogna", "omrade": "Härjedalen", "latitude": 62.5273, "longitude": 14.1952},
    {"namn": "Funäsfjällen (Funäsdalen/Ramundberget/Tänndalen)", "omrade": "Härjedalen", "latitude": 62.5463, "longitude": 12.5432},
    {"namn": "Bydalsfjällen", "omrade": "Södra Jämtland", "latitude": 63.1521, "longitude": 13.6712},
    {"namn": "Trillevallen / Edsåsdalen", "omrade": "Södra Årefjällen", "latitude": 63.2981, "longitude": 13.1612},
    {"namn": "Åre / Duved", "omrade": "Åredalen", "latitude": 63.3980, "longitude": 13.1250},
    {"namn": "Östersund / Frösön", "omrade": "Storsjöbygden", "latitude": 63.1792, "longitude": 14.5977}
]

# Gränssnitt med två flikar
flik_chatt, flik_karta = st.tabs(["💬 Sök med Live-Agent", "🗺️ Skidorter & Geografi"])

with flik_karta:
    st.subheader("Områden och skidorter som agenten bevakar")
    st.caption("Sträckan sträcker sig från södra Dalarna upp till Jämtland.")
    
    kartdata = [{"latitude": s["latitude"], "longitude": s["longitude"]} for s in skidorter_karta]
    st.map(kartdata, zoom=5)

    st.subheader("Bevakade orter i systemet")
    kolumn1, kolumn2 = st.columns(2)
    for index, ort in enumerate(skidorter_karta):
        vald_kolumn = kolumn1 if index % 2 == 0 else kolumn2
        with vald_kolumn:
            st.markdown(f"• **{ort['namn']}** ({ort['omrade']})")

with flik_chatt:
    st.subheader("Live-sökning efter stugor")
    st.info("Agenten använder Googles sökmotor för att hitta aktuella annonser, priser och länkar på webben.")

    klient = genai.Client(api_key=api_nyckel)

    instruktion = (
        "Du är en specialiserad assistent som söker efter lediga fjällstugor på internet över julen 2026. "
        "Det geografiska sökområdet är i och omkring skidorter längs sträckan Romme till Östersund i Sverige. "
        "Familjens specifika krav är: ankomst från 23 december 2026 och framåt, samt minst 6 bäddar. "
        "När användaren ber om stugor måste du använda Googles sökverktyg för att hitta verkliga annonser, "
        "bokningssidor eller information från källor som Stugknuten, Blocket, Skistar, Airbnb eller lokala stugförmedlare. "
        "Presentera resultaten strukturerat med stugnamn/typ, exakt ort, antal bäddar, uppskattat pris och direktlänk eller källa."
    )

    # Initiera chattsessionen med Google Search som verktyg
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = klient.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=instruktion,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            )
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Rensa-knapp för att nollställa konversationen
    if st.sidebar.button("Nollställ sökning"):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state["chat_session"]
        st.rerun()

    for meddelande in st.session_state.messages:
        with st.chat_message(meddelande["role"]):
            st.markdown(meddelande["content"])

    if prompt := st.chat_input("Skriv din sökning, t.ex. 'Leta efter 6-bäddsstugor i Lofsdalen eller Vemdalen från 23 dec 2026'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            meddelande_placeholder = st.empty()
            lyckades = False
            for forsok in range(3):
                try:
                    respons = st.session_state.chat_session.send_message(prompt)
                    meddelande_placeholder.markdown(respons.text)
                    st.session_state.messages.append({"role": "assistant", "content": respons.text})
                    lyckades = True
                    break
                except ServerError:
                    time.sleep(2)
            
            if not lyckades:
                felmeddelande = "Tjänsten har tillfälligt hög belastning. Försök att skicka frågan igen."
                meddelande_placeholder.markdown(felmeddelande)
                st.session_state.messages.append({"role": "assistant", "content": felmeddelande})