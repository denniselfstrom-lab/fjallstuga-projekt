import os
import datetime
from google import genai
from google.genai import types

# Hämta API-nyckeln från GitHub Secrets / miljövariabel
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("Miljövariabeln GEMINI_API_KEY saknas.")

klient = genai.Client()

sokprompt = (
    "Genomför en sökning på internet efter nyligen tillagda eller lediga fjällstugor "
    "i och kring skidorter längs sträckan Romme till Östersund (t.ex. Romme, Sälen, Idre, "
    "Lofsdalen, Vemdalen, Funäsdalen, Åre, Östersund). "
    "Kriterier: Tillträde från 23 december 2026 och framåt, samt minst 6 bäddar. "
    "Leta på sidor som Stugknuten, Blocket Bostad, Airbnb eller lokala stugförmedlare. "
    "Sammanställ resultaten med: Stugnamn/Plats, Antal bäddar, Pris, Datum och Webbkälla/Länk."
)

instruktion = (
    "Du är en automatisk bevakningsagent. Använd Googles sökverktyg för att hitta verkliga "
    "och aktuella stugannonser. Leverera en ren och lättläst rapport i Markdown-format."
)

print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Startar daglig bevakning...")

respons = klient.models.generate_content(
    model="gemini-3.8-flash",
    contents=sokprompt,
    config=types.GenerateContentConfig(
        system_instruction=instruktion,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )
)

rapport = respons.text
print("\n--- DAGENS BEVAKNINGSRAPPORT ---\n")
print(rapport)

# Spara rapporten till en textfil med dagens datum
dagens_datum = datetime.date.today().isoformat()
filnamn = f"rapport_{dagens_datum}.md"
with open(filnamn, "w", encoding="utf-8") as f:
    f.write(f"# Stugbevakning {dagens_datum}\n\n")
    f.write(rapport)

print(f"\nRapport sparad till {filnamn}")