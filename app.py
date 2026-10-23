import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google import genai
from google.genai import types
from duckduckgo_search import DDGS

st.set_page_config(
    page_title="Fjällstugor Julen 2026",
    page_icon="🏔️",
    layout="wide"
)

st.title("🏔️ Fjällstugor Julen 2026 (DDG + Gemini)")
st.caption("Fristående stugsökning från Romme till Östersund (minst 6 bäddar, från 23 december 2026).")

import os

api_key = st.secrets.get("GEMINI_API_KEY", None)

def get_gemini_client():
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY saknas i Streamlit Secrets.")
        st.stop()
    
    ren_nyckel = str(api_key).strip().strip('"').strip("'")
    os.environ["GEMINI_API_KEY"] = ren_nyckel
    return genai.Client(api_key=ren_nyckel)

def sok_stugor_webb(orter_lista, extra):
    ddg_resultat = []
    med_orter = orter_lista if orter_lista else ["Sälen", "Idre Fjäll", "Lofsdalen", "Vemdalen", "Åre"]
    
    with DDGS() as ddgs:
        for ort in med_orter[:3]:
            query = f"hyra stuga {ort} julen 2026 6 bäddar 23 december site:stugknuten.com OR site:blocket.se OR site:skistar.com"
            try:
                traffar = list(ddgs.text(query, max_results=3))
                for t in traffar:
                    ddg_resultat.append(f"Ort: {ort}\nTitel: {t.get('title')}\nLänk: {t.get('href')}\nInnehåll: {t.get('body')}\n")
            except Exception:
                continue

    if not ddg_resultat:
        return "Inga direkta träffar hittades via webbsökningen. Använd de officiella bokningsportalerna."
    return "\n---\n".join(ddg_resultat)

ORTER = [
    {"namn": "Romme Alpin", "lat": 60.3957, "lon": 15.3524, "omrade": "Södra Dalarna", "info": "Närmast från Mälardalen."},
    {"namn": "Sälen (Lindvallen/Hundfjället)", "lat": 61.1578, "lon": 13.1979, "omrade": "Dalarna", "info": "Stort utbud av stugor."},
    {"namn": "Idre Fjäll", "lat": 61.8906, "lon": 12.8361, "omrade": "Norra Dalarna", "info": "Snösäkert med varierad åkning."},
    {"namn": "Lofsdalen", "lat": 62.1154, "lon": 13.2755, "omrade": "Härjedalen", "info": "Familjevänligt och lugnt."},
    {"namn": "Vemdalen (Björnrike/Skalet)", "lat": 62.4789, "lon": 13.9744, "omrade": "Härjedalen", "info": "Klassiska fjällbyar med rymliga stugor."},
    {"namn": "Funäsdalen & Tänndalen", "lat": 62.5447, "lon": 12.5439, "omrade": "Härjedalen", "info": "Rejäla fjäll och fina spår."},
    {"namn": "Åre & Duved", "lat": 63.3990, "lon": 13.0815, "omrade": "Jämtland", "info": "Sveriges största skidsystem."},
    {"namn": "Östersund", "lat": 63.1792, "lon": 14.6357, "omrade": "Jämtland", "info": "Stadsmiljö nära fjäll och vinteraktiviteter."}
]
df_orter = pd.DataFrame(ORTER)

flik_sok, flik_karta = st.tabs(["🔍 Manuell Sökning", "🗺 Skidorter & Geografi"])

with flik_sok:
    st.subheader("Starta stugsökning manuellt")
    st.write("Välj skidorter och starta webbsökningen med ett klick. Inga anrop sker automatiskt.")

    col1, col2 = st.columns([2, 1])
    with col1:
        valda_orter = st.multiselect(
            "Välj skidorter (lämna tomt för att söka i huvudorterna):",
            options=df_orter["namn"].tolist(),
            default=[]
        )
    with col2:
        extra_krav = st.text_input("Övriga önskemål (t.ex. bastu, ski-in/ski-out):", value="")

    starta_sokning = st.button("🚀 Kör stugsökning via DuckDuckGo nu", type="primary", use_container_width=True)

    if starta_sokning:
        with st.spinner("1/2: Söker på webben via DuckDuckGo..."):
            webbdata = sok_stugor_webb(valda_orter, extra_krav)

        with st.spinner("2/2: Gemini analyserar och sammanställer träffarna..."):
            klient = get_gemini_client()

            system_prompt = (
                "Du är en stugförmedlingsassistent för de svenska fjällen. "
                "Analysera det tillhandahållna sökresultatet från webben. "
                "Kriterier: Ledigt från 23 december 2026, minst 6 bäddar. "
                "Skapa en sammanställning för varje stuga med: "
                "1. Namn på stugan / Område "
                "2. Antal bäddar "
                "3. Pris eller prisuppskattning "
                "4. Direkt klickbar Markdown-länk hämtad ur sökresultatet (t.ex. [Öppna annons](URL)). "
                "Om specifika annonser saknas i texten, ge rekommendationer och länkar till ortens bokningssida."
            )

            anfragan = (
                f"Valda orter: {valda_orter}\n"
                f"Extra krav: {extra_krav}\n\n"
                f"Webbdata från DuckDuckGo:\n{webbdata}"
            )

            modeller = ["gemini-3.8-flash", "gemini-2.5-flash"]
            respons = None
            senaste_fel = None

            for modell_namn in modeller:
                try:
                    respons = klient.models.generate_content(
                        model=modell_namn,
                        contents=anfragan,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            tools=[],
                            temperature=0.2,
                        )
                    )
                    break
                except Exception as e:
                    senaste_fel = e
                    continue

            if respons:
                st.session_state["senaste_resultat"] = respons.text
            else:
                st.error(f"Kunde inte nå AI-tjänsten just nu: {senaste_fel}. Vänta en kort stund och klicka igen.")

    if "senaste_resultat" in st.session_state:
        st.divider()
        st.subheader("📋 Sökresultat")
        st.markdown(st.session_state["senaste_resultat"])

with flik_karta:
    st.subheader("Geografisk översikt: Romme till Östersund")
    karta = folium.Map(location=[61.9, 14.0], zoom_start=6)
    for _, rad in df_orter.iterrows():
        folium.Marker(
            location=[rad["lat"], rad["lon"]],
            popup=f"<b>{rad['namn']}</b><br>{rad['omrade']}<br><i>{rad['info']}</i>",
            tooltip=rad["namn"],
            icon=folium.Icon(color="darkblue", icon="snowflake-o", prefix="fa")
        ).add_to(karta)

    st_folium(karta, width=950, height=500)
    st.dataframe(df_orter[["namn", "omrade", "info"]], hide_index=True, use_container_width=True)