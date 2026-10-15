import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google import genai
from google.genai import types

st.set_page_config(page_title="Fjällstugor Julen 2026", page_icon="🏔️", layout="wide")

st.title("🏔️ Fjällstugor Julen 2026 (Live Webbsökning)")
st.caption("Agent som söker direkt på internet efter stugor med minst 6 bäddar från 23 december 2026 längs sträckan Romme – Östersund.")

# Läs in API-nyckel
api_key = st.secrets.get("GEMINI_API_KEY", None)

def hamta_klient():
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

with st.sidebar:
    if st.button("Nollställ sökning"):
        st.session_state.messages = []
        st.rerun()

flik_sok, flik_karta = st.tabs(["💬 Sök med Live-Agent", "🗺 Skidorter & Geografi"])

# --- FLIK 1: SÖKAGENT ---
with flik_sok:
    st.subheader("Live-sökning efter stugor")
    st.info("Agenten använder Googles sökmotor för att hitta aktuella annonser, priser och länkar på webben.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for meddelande in st.session_state.messages:
        with st.chat_message(meddelande["role"]):
            st.markdown(meddelande["content"])

    if prompt := st.chat_input("Skriv din sökning, t.ex. 'Leta efter 6-bäddsstugor i Lofsdalen eller Vemdalen från 23 dec 2026'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Söker av internet efter lediga stugor..."):
                try:
                    klient = hamta_klient()
                    
                    contents = []
                    for msg in st.session_state.messages:
                        roll = "user" if msg["role"] == "user" else "model"
                        contents.append(types.Content(role=roll, parts=[types.Part.from_text(text=msg["content"])]))

                    instruktion = (
                        "Du är en stugbokningsagent specialiserad på svenska fjällen (Romme till Östersund). "
                        "Använd alltid Google Search för att hitta verifierade och aktuella stugannonser. "
                        "Krav: Minst 6 bäddar och ledigt från 23 december 2026. "
                        "Svara strukturerat med ort/skidort, stugnamn, antal bäddar, ungefärligt pris och källänk."
                    )

                    respons = klient.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=instruktion,
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                            temperature=0.2,
                        )
                    )
                    svar = respons.text
                    st.markdown(svar)
                    st.session_state.messages.append({"role": "assistant", "content": svar})
                except Exception as e:
    feltext = str(e)
    if "429" in feltext or "RESOURCE_EXHAUSTED" in feltext:
        st.warning("⏳ Sökkvoten är tillfälligt uppnådd (Google API-begränsning). Vänta 1–2 minuter och försök igen.")
    else:
        st.error(f"Ett fel uppstod vid sökningen: {e}")

# --- FLIK 2: KARTA ---
with flik_karta:
    st.subheader("Skidorter & Geografiskt område")
    
    orter = [
        {"namn": "Romme Alpin", "lat": 60.3957, "lon": 15.3524, "omrade": "Södra Dalarna"},
        {"namn": "Sälen (Lindvallen/Hundfjället)", "lat": 61.1578, "lon": 13.1979, "omrade": "Dalarna"},
        {"namn": "Idre Fjäll", "lat": 61.8906, "lon": 12.8361, "omrade": "Norra Dalarna"},
        {"namn": "Lofsdalen", "lat": 62.1154, "lon": 13.2755, "omrade": "Härjedalen"},
        {"namn": "Vemdalen (Björnrike/Vemdalsskalet)", "lat": 62.4789, "lon": 13.9744, "omrade": "Härjedalen"},
        {"namn": "Funäsdalen & Tänndalen", "lat": 62.5447, "lon": 12.5439, "omrade": "Härjedalen"},
        {"namn": "Åre & Duved", "lat": 63.3990, "lon": 13.0815, "omrade": "Jämtland"},
        {"namn": "Östersund", "lat": 63.1792, "lon": 14.6357, "omrade": "Jämtland"}
    ]
    df_orter = pd.DataFrame(orter)

    m = folium.Map(location=[61.8, 13.8], zoom_start=6)
    for _, rad in df_orter.iterrows():
        folium.Marker(
            location=[rad["lat"], rad["lon"]],
            popup=f"<b>{rad['namn']}</b><br>{rad['omrade']}",
            tooltip=rad["namn"],
            icon=folium.Icon(color="blue", icon="snowflake-o", prefix="fa")
        ).add_to(m)

    st_folium(m, width=900, height=500)