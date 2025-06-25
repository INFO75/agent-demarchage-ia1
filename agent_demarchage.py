
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration Twilio
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
client = Client(account_sid, auth_token)

# Authentification Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
gc = gspread.authorize(creds)

# Ouverture du fichier Google Sheet
sheet = gc.open("BaseProspects").sheet1
data = pd.DataFrame(sheet.get_all_records())

# Filtrage : entreprise sans site web
data_filtered = data[data['site'].isnull() | (data['site'] == '')]

# Script vocal généré par GPT
def generer_script(nom_entreprise):
    prompt = f"Crée un script de démarchage téléphonique pour proposer à l'entreprise '{nom_entreprise}' un site web professionnel, avec un ton sérieux, engageant et adapté à un premier contact commercial."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Appel automatique avec Twilio (message vocal)
def appeler_et_lire(numero, texte):
    appel = client.calls.create(
        twiml=f'<Response><Say voice="alice" language="fr-FR">{texte}</Say></Response>',
        to=numero,
        from_=twilio_number
    )
    print(f"Appel lancé vers {numero} : {appel.sid}")

# Boucle sur chaque prospect
for index, row in data_filtered.iterrows():
    nom = row['nom']
    tel = row['telephone']
    if tel:
        script = generer_script(nom)
        appeler_et_lire(tel, script)
