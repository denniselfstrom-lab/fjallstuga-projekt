import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Fjällstugor Julen 2026",
    page_icon="🏔️",
    layout="wide"
)

st.title("🏔️ Fjällstugor Julen 2026 (Manuell Sökagent)")
st.caption("Agent för stugor längs sträckan Romme – Östersund (minst 6 bäddar, incheckning från 23 december 2026).")

api_key = st.secrets.get("GEMINI_API_KEY", None)

def get_gemini_client():
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

ORTER = [
    {"namn": "Romme Alpin", "lat": 60.3957, "lon": 15.3524, "omrade": "Södra Dalarna", "info": "Närmast från Mälardalen."},
    {"namn": "Sälen (Lindvallen/Hundfjället)", "lat": 61.1578, "lon": 13.1979, "omrade": "Dalarna", "info": "Stort utbud av stugor."},
    {"namn": "Idre Fjäll", "lat": 61.8906, "lon": 12.8361, "omrade": "Norra Dalarna", "info": "Snösäkert med v    {"namn": "Idre F    {"namn": "Lofsdalen",    {": 62.115    {"namn": "Idre Fjäll", "lHärjedalen", "info": "Familjevänligt och lugnt."},
                             nrike/Skalet)", "lat": 6                             nrike/Härjed                      ska                rymli                             nrike/Skalet)", "lat": 6         62                             nrike/Skalet)", "lat": 6                             nrike/Härjed                      ska   t":                             nrike/Skalet)", "", "                   örsta            "},
                             nrike/Skalet) "l                        "Jämtland",                              nrike/Skalet) "l                        "Jämtland",                              nrike/Skalet) "�                             nrike/Skalet) "l                        "Jämtland",                              nrike/Skalet) "l        j ett eller flera områden, eller sök över hela sträckan Romme–Östersund. Inga anrop görs förrän du trycker på knappen.")

    col1, col2 = st.columns([2, 1])
    with col1:
        valda_orter = st.multiselect(
            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifikaer            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifika            "Filtrera på specifikaer            "Filtr "
            "Filtrera på speskidort            "          "2. Antal bäddar "
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
                    confi                    confi                    confi                    confi ste                    confi                    confi (google_search=types.GoogleSearch())],
                        temperature=0.2,
                    )
                )

                st.session_state["senaste_resultat"] = respons.text

            except Except on as e:
                                                                                                   text:
                    s                    s                    är t                    s          ��2                    s                    s                    är t          elte                    s                    s                    är t                    s  tt t                    s                    s                    är t                    s          ��kni                 if "senaste_resultat" in st.session_state:
        st.divider()
        st.subheader("📋 Sökresultat")
        st.subheader("📋 Sökreate[        st.subheader("📋 Sökreate[        st.subheader("📋 Sökreate[        st.subheader("📋 Sökreate[        st.subheader("📋 Sökreate[        st.subheader("📋 Sökreate[       ca        st.subheader("📋 Sökreate[for         st.subheaderterrows():
        folium.Marker(
            location=[rad["lat"], rad["lon"]],
                                          r>{rad['omrade']}<br><i>{rad['info']}</i>",
            tooltip=rad["namn"],
            icon=folium.Icon(color="darkblue", icon="snowflake-o", prefix="fa")
        ).add_to(karta)

    st_folium(karta, width=950, height=500)
    st.dataframe(df_orter[["namn", "omrade", "info"]], hide_index=True, use_container_width=True)
