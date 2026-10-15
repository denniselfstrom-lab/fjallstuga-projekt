import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError

klient = genai.Client(api_key="AQ.Ab8RN6LNmVMp4WfmbSk99Za53YLRxxpwsKP8mSNK-O-X5Gpvug")

def sok_fjallstugor(ort: str, lagsta_antal_baddar: int = 2) -> list[dict]:
    """Söker i stugdatabasen efter lediga stugor över julen år 2026."""
    stugregister = [
        {
            "namn": "Fjällro i Björnen",
            "ort": "Åre",
            "antal_baddar": 8,
            "veckopris_kronor": 22500,
            "period": "20 december till 27 december 2026",
            "egenskaper": ["Bastu", "Direkt anslutning till skidbacke", "Kamin"]
        },
        {
            "namn": "Mysstugan Lindvallen",
            "ort": "Sälen",
            "antal_baddar": 6,
            "veckopris_kronor": 16000,
            "period": "22 december till 27 december 2026",
            "egenskaper": ["Bastu", "Nära spår för längdskidåkning"]
        },
        {
            "namn": "Vemdalsskalets Utsikt",
            "ort": "Vemdalen",
            "antal_baddar": 4,
            "veckopris_kronor": 12500,
            "period": "21 december till 28 december 2026",
            "egenskaper": ["Öppen spis", "Tillåtet för sällskapsdjur"]
        },
        {
            "namn": "Kittelfjäll Toppstuga",
            "ort": "Kittelfjäll",
            "antal_baddar": 10,
            "veckopris_kronor": 19000,
            "period": "20 december till 27 december 2026",
            "egenskaper": ["Bastu", "Direkt anslutning till skidbacke", "Bubbelpool"]
        }
    ]

    resultat = []
    for stuga in stugregister:
        ort_matchar = ort.lower() in stuga["ort"].lower()
        baddar_racker = stuga["antal_baddar"] >= lagsta_antal_baddar
        if ort_matchar and baddar_racker:
            resultat.append(stuga)

    return resultat

instruktion_for_systemet = (
    "Du är en bokningsassistent för stugor i svenska fjällen under julen år 2026. "
    "När personen som skriver letar efter boende måste du använda sökverktyget sok_fjallstugor. "
    "Om användaren inte anger en specifik ort, fråga vilken ort de önskar eller sök brett. "
    "Återge stugans namn, ort, antal bäddar, pris i svenska kronor samt utrustning på ett tydligt sätt."
)

konversation = klient.chats.create(
    model="gemini-3.8-flash",
    config=types.GenerateContentConfig(
        system_instruction=instruktion_for_systemet,
        tools=[sok_fjallstugor],
        temperature=0.2,
    )
)

print("Programmet körs. Skriv din fråga nedan, eller skriv avsluta för att stänga.")

while True:
    anvandarens_fraga = input("\nDu: ")
    if anvandarens_fraga.strip().lower() in ["avsluta", "stopp"]:
        print("Programmet avslutas.")
        break

    # Automatisk hantering om servern har tillfällig hög belastning
    lyckades = False
    for forsok in range(3):
        try:
            svar = konversation.send_message(anvandarens_fraga)
            print(f"\nAssistenten: {svar.text}")
            lyckades = True
            break
        except ServerError:
            print("Servern är tillfälligt hårt belastad, väntar tre sekunder och försöker igen...")
            time.sleep(3)

    if not lyckades:
        print("\nKunde inte nå servern just nu på grund av hög belastning hos leverantören. Försök igen om en liten stund.")