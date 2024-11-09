import openai
import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add more origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from specified origins
    allow_credentials=True,
    allow_methods=["*"],    # Allows all HTTP methods
    allow_headers=["*"],    # Allows all headers
)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define input models for FastAPI

class UserQuery(BaseModel):
    interogare_utilizator: str
    english: bool = False

# New Pydantic model for TimPark information extraction
class TimParkQuery(BaseModel):
    interogare_utilizator: str

# Utility Functions

def creează_prompt_extragere_engleza(input_utilizator):
    prompt = f"""
    Ești un asistent care extrage informații specifice din interogările utilizatorilor.

    **Interogarea Utilizatorului:**
    {input_utilizator}

    **Instrucțiuni:**
    Din interogarea de mai sus, extrage următoarele informații:
    - **Categorie**: Selectează o categorie din lista de mai jos care se potrivește cel mai bine cu intenția utilizatorului (alege doar o singură opțiune):
        - 'Property and Asset Management'
        - 'Public Services and Utilities Management'
        - 'Urban Planning and Development'
        - 'Governance and Administration'
        - 'Legal and Contracts'
        - 'Financial and Budget Management'
        - 'Education and Social Services'
        - 'Market Regulation and Economics'
        - 'Transportation and Infrastructure'
        - 'Environmental and Energy Management'
        - 'Health and Safety'
        - 'Culture and Tourism'
        - 'Human Resources'

    **Formatul Răspunsului:**
    Furnizează informațiile extrase în următorul format JSON:
    ```json
    {{
      "category": "Categorie"
    }}
    ```
    """
    return prompt

def creează_prompt_extragere_romana(input_utilizator):
    prompt = f"""
    Ești un asistent care extrage informații specifice din interogările utilizatorilor.

    **Interogarea Utilizatorului:**
    {input_utilizator}

    **Instrucțiuni:**
    Din interogarea de mai sus, extrage următoarele informații:
    - **Categorie**: Selectează o categorie din lista de mai jos care se potrivește cel mai bine cu intenția utilizatorului (alege doar o singură opțiune):
        - 'Managementul Proprietăților și Activelor'
        - 'Managementul Serviciilor Publice și Utilităților'
        - 'Planificare și Dezvoltare Urbană' 
        - 'Guvernanță și Administrație'
        - 'Legal și Contracte' 
        - 'Management Financiar și Bugetar'
        - 'Educație și Servicii Sociale' 
        - 'Reglementarea Pieței și Economiei'
        - 'Transport și Infrastructură' 
        - 'Managementul Mediului și Energiei'
        - 'Sănătate și Siguranță' 
        - 'Cultură și Turism' 
        - 'Resurse Umane'

    **Formatul Răspunsului:**
    Furnizează informațiile extrase în următorul format JSON:
    ```json
    {{
      "category": "Categorie"
    }}
    ```
    """
    return prompt

def obține_informații_extrase(prompt):
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": "Ești un asistent util."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4-turbo",
        temperature=0,
        top_p=0.9
    )
    message_content = response['choices'][0]['message']['content']
    return message_content

def procesează_răspunsul(text_răspuns):
    try:
        json_str = text_răspuns[text_răspuns.find('{'):text_răspuns.rfind('}')+1]
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"Eroare la decodificarea JSON: {e}")
        return None

def interoghează_date(nume_categorie, path_df):
    df = pd.read_csv(path_df)
    df_filtrat = df[df['general_categories'] == nume_categorie]
    return df_filtrat['gpt_description']

def creează_prompt_final(interogare_utilizator, text_rezultat, n=3):
    prompt = f"""Ești un asistent util.

    Utilizatorul a întrebat: "{interogare_utilizator}"

    Pe baza analizei datelor, iată concluziile: {text_rezultat}

    Te rog să furnizezi un răspuns detaliat și structurat la întrebarea utilizatorului folosind informațiile de mai sus.

    Începe prin a rezuma întrebarea utilizatorului în propriile tale cuvinte.
    Apoi, prezintă concluziile clar, folosind puncte de bullet sau paragrafe, după cum este adecvat.
    Asigură-te că abordezi direct și complet întrebarea utilizatorului.
    La final, pe baza descrierii care s-a potrivit cel mai bine pentru a răspunde la întrebarea utilizatorului, știind că concluziile au fost construite folosind acest format:
    HCL [număr]/[an] Explicație: [explicație]; Rezumat: [rezumat]
    fă o listă cu {n} exemple: HCL [număr]/[an] (astfel încât această listă să servească drept mod de a verifica dacă informațiile oferite sunt corecte sau nu).
    """
    return prompt

# New Utility Functions for TimPark

def creează_prompt_final_timpark(interogare_utilizator, text_rezultat, n=2):
    prompt = f"""
    Ești un asistent care va răspunde la o întrebare folosind informații despre hotărâri ale consiliului local (HCL), furnizate într-un format JSON cu câmpurile: "Titlu", "Explicație", "Referințe HCL Anterioare", "Rezumat".

    **Întrebare utilizator**: "{interogare_utilizator}"
    
    **Informații despre HCL-uri**: {text_rezultat}

    Instrucțiuni pentru răspuns:
    1. **Rezumați întrebarea** în propriile tale cuvinte.
    2. **Prezentați un răspuns structurat și detaliat**, concentrându-vă pe ordine cronologică, cu accent pe hotărârile recente (anul 2024 și ulterior).
    3. **Formulați concluziile** clar și concis, folosind puncte de bullet sau paragrafe, abordând complet întrebarea utilizatorului.
    4. **La final**, listați cele mai relevante {n} exemple de HCL-uri în formatul:  
       - HCL: nr.[nr]/[an] si un json: "Titlu", "Explicație"

    Această listă va ajuta la verificarea corectitudinii informațiilor oferite.
    """
    return prompt


# Existing Endpoint

@app.post("/extrage_informatii/")
async def extrage_informatii(query: UserQuery):
    interogare_utilizator = query.interogare_utilizator
    english = query.english

    path_df = 'all_hcl_general_categories_and_summary.csv' if english else 'all_hcl_general_categories_and_summary_romanian.csv'
    prompt = creează_prompt_extragere_engleza(interogare_utilizator) if english else creează_prompt_extragere_romana(interogare_utilizator)
    
    text_răspuns = obține_informații_extrase(prompt)
    date_extrase = procesează_răspunsul(text_răspuns)

    if date_extrase is None or 'category' not in date_extrase:
        raise HTTPException(status_code=400, detail="Nu s-a putut extrage categoria. Verifică interogarea și încearcă din nou.")
    
    rezultate_text = interoghează_date(date_extrase['category'], path_df)
    n_rezultate = 5
    rezultate_text = rezultate_text.head(n_rezultate).tolist()
    rezultate_concatenate = "\n\n".join(rezultate_text)
    prompt_final = creează_prompt_final(interogare_utilizator, rezultate_concatenate, n=3)
    răspuns_final = obține_informații_extrase(prompt_final)

    raspuns_formatat = formatare_raspuns(răspuns_final)
    return {"raspuns_final": raspuns_formatat}

# New Endpoint for TimPark Information Extraction

@app.post("/extrage_timpark_informatii/")
async def extrage_timpark_informatii(query: TimParkQuery):
    interogare_utilizator = query.interogare_utilizator

    # Define the path to the TimPark-specific CSV
    path_df = 'hcl_timpark_json_generated_with_gpt_gpt_desc_added.csv'

    # Load the TimPark CSV
    if not os.path.exists(path_df):
        raise HTTPException(status_code=500, detail="Fișierul de date TimPark nu a fost găsit.")

    df = pd.read_csv(path_df)
    rezultate_text = df['gpt_description'].dropna().tolist()

    # Concatenate the results
    rezultate_concatenate = "\n\n".join(rezultate_text)

    # Create the final prompt
    prompt_final = creează_prompt_final_timpark(interogare_utilizator, rezultate_concatenate, n=2)
    răspuns_final = obține_informații_extrase(prompt_final)

    raspuns_formatat = formatare_raspuns(răspuns_final)
    return {"raspuns_final": raspuns_formatat}

import re

def formatare_raspuns(text_raspuns: str) -> str:
    """
    Formatează textul răspunsului astfel încât fiecare secțiune
    începută și încheiată cu '**' să fie într-un paragraf nou,
    separate printr-un rând liber.
    
    Args:
        text_raspuns (str): Textul răspunsului original.
    
    Returns:
        str: Textul răspunsului formatat.
    """
    # Definește un pattern pentru a găsi secțiunile marcate cu **
    pattern = r'(\*\*[^*]+\*\*:)'
    
    # Adaugă două rânduri libere înainte de fiecare secțiune
    text_formatat = re.sub(pattern, r'\n\n\1', text_raspuns)
    
    # Elimină eventualele rânduri libere de la început
    text_formatat = text_formatat.lstrip('\n')
    
    return text_formatat




# Main entry point to run the server directly from code
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
