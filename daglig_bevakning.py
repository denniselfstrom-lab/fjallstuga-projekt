import os
import time
import datetime
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("Miljövariabeln GEMINI_API_KEY saknas.")

klient = genai.Client()

sokprompt = (
    "Sök på internet efter lediga fjällstugor i och omkring skidorter längs sträckan Romme till Östersund. "
    "Kriterier: Tillträde från 23 december 2026 och framåt, samt minst 6 bäddar. "
    "Sök på Stugknuten, Blocket Bostad eller lokala skidorter. "
    "Sammanställ resultaten kortfattat i Markdown med: Stugnamn/Område, Bäddar, Pris och Webbkälla."
)

instruktion = (
    "Du är en stugbevakningsagent. Sök på webben och sammanställ en kort och koncis rapport."
)

print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Startar sökning...")

respons = None
max_forsok = 3
for forsok in range(max_forsok):
    try:
        respons = klient.models.generate_content(
            model="gemini-3.8-flash",
            contents=sokprompt,
            config=types.GenerateContentConfig(
                system_instruction=instruktion,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
            )
        )
        break
    except ClientError as e:
        if "429" in str(e) and forsok < max_forsok - 1:
            print(f"Kvoten nådd (429). Väntar 60 sekunder före nytt försök ({forsok + 1}/{max_forsok})...")
            time.sleep(60)
        else:
            raise e
    except ServerError:
        time.sleep(5)

if not respons:
    raise RuntimeError("Kunde inte generera rapport efter upprepade försök.")

rapport = respons.text
print("\n--- RAPPORT ---\n")
print(rapport)

dagens_datum = datetime.date.today().isoformat()
filnamn = f"rapport_{dagens_datum}.md"
with open(filnamn, "w", encoding="utf-8") as f:
    f.write(f"# Stugbevakning {dagens_datum}\n\n{rapport}")

print(f"\nRapport sparad till {filnamn}")