import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google import genai
from google.genai import types

# Sidkonfiguration
st.set_page_config(
    page_title="Fjällstugor Julen 2026",
    page_icon="🏔️",
    layout="wide"
)

st.title("🏔️ Fjällstugor Julen 2026 (Manuell Sökagent)")
st.caption("Agent för stugor längs sträckan Romme – Östersund (minst 6 bäddar, incheckning från 23 december 2026).")

# Hämta API-nyckel säkert från Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY", None)

def get_gemini_client():
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

# Skidortsdata
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

# Flikar i gränssnittet
flik_sok, flik_karta = st.tabs(["🔍 Manuell Sökning", "🗺 Skidorter & Geografi"])

# --- FLIK 1: MANUELL SÖKNING ---
with flik_sok:
    st.subheader("Starta stugsökning manuellt")
    st.write("Välj ett eller flera områden, eller sök över hela sträckan Romme–Östersund. Inga anrop görs förrän du trycker på knappen.")

    col1, col2 = st.columns([2, 1])
    with col1:
        valda_orter = st.multiselect(
            "Filtrera på specifika orter (lämna tomt för att söka över alla):",
            options=df_orter["namn"].tolist(),
            default=[]
        )
    with col2:
        extra_krav = st.text_input("Övriga önskemål (t.ex. bastu, ski-in/ski-out):", value="")

    # Huvudknappen för att starta sökningen
    starta_sokning = st.button("🚀 Kör komplett stugsökning nu", type="primary", use_container_width=True)

    if starta_sokning:
        omradestext = ", ".join(valda_orter) if valda_orter else "alla skidorter längs sträckan Romme till Östersund (inklusive Sälen, Idre, Lofsdalen, Vemdalen, Åre)"
        kravtext = f" Extra önskemål: {extra_krav}." if extra_krav else ""

        prompt = (
            f"Sök på internet efter lediga fjällstugor för julen 2026 i följande områden: {omradestext}. "
            f"Krav: Minst 6 bäddar och ledigt från 23 december 2026.{kravtext} "
            "För varje stuga du hittar ska du ange: "
            "1. Stugnamn och skidort/område "
            "2. Antal bäddar "
            "3. Pris/vecka (eller uppskattat pris) "
            "4. Källänk: Skapa en klickbar Markdown-länk till den specifika annonsen (t.ex. [Öppna annons](URL)). "
            "Om specifik annonslänk saknas, länka till ortens officiella stugförmedling."
        )

        with st.spinner("Söker live på webben efter lediga stugor... Detta tar cirka 10–20 sekunder."):
            try:
                klient = get_gemini_client()

                system_prompt = (
                    "Du är en expert på stuguthyrning i de svenska fjällen. "
                    "Använd Google Search för att hämta aktuella och verifierade stugor. "
                    "Formatera alltid svaret strukturerat med tydliga rubriker och klickbara länkar."
                )

                respons = klient.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.2,
                    )
                )

                # Spara och visa resultatet
                st.session_state["senaste_resultat"] = respons.text

            except Exception as e:
                feltext = str(e)
                if "429" in feltext or "RESOURCE_EXHAUSTED" in feltext:
                    st.warning("⏳ Sökkvoten hos Google API är tillfälligt uppnådd. Vänta 1–2 minuter innan du trycker på knappen igen.")
                elif "404" in feltext:
                    st.error("Modellkonfigurationsfel: Kontrollera att modellen är satt till gemini-3.8-flash.")
                else:
                    st.error(f"Ett fel uppstod vid sökningen: {e}")

    # Visa senaste sökresultat om det finns sparat i sessionen
    if "senaste_resultat" in st.session_state:
        st.divider()
        st.subheader("📋 Sökresultat")
        st.markdown(st.session_state["senaste_resultat"])

# --- FLIK 2: KARTA & SKIDORTER ---
with flik_karta:
    st.subheader("Geografisk översikt: Romme till Östersund")
    st.write("Klicka på en skidort för att se information.")

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