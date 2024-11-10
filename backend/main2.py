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


def creează_prompt_extragere_romana(input_utilizator):
    prompt = f"""
    Ești un asistent care analizează o interogare si care va mapa subiectul aceste interogari intr-o categorie din cele de mai jos
    Obiectivul este de a sugera o categorie relevanta in care ar trebui sa se integreze subiectul interogarii date.

    **Interogarea Utilizatorului:**
    {input_utilizator}

    **Instrucțiuni:**
    Din interogarea de mai sus, extrage următoarele informații:
    - **Categorie**: Selectează o categorie din lista de mai jos care se potrivește cel mai bine cu intenția utilizatorului, folosește descrierea fiecărei categorii ca ghid pentru a identifica cea mai potrivită categorie, alege doar o singură opțiune:
        - 'Managementul Proprietăților și Activelor' - Decizii care implică administrarea, întreținerea sau modificarea proprietăților și bunurilor publice.
        - 'Managementul Serviciilor Publice și Utilităților' - Hotărâri referitoare la servicii publice esențiale, precum apă, energie, colectarea deșeurilor etc.
        - 'Planificare și Dezvoltare Urbană' - Măsuri pentru dezvoltarea urbanistică, inclusiv planuri de construcție și zonare.
        - 'Guvernanță și Administrație' - Decizii privind organizarea, reglementarea și funcționarea administrației publice locale.
        - 'Legal și Contracte' - Aspecte juridice și contractuale, inclusiv litigii și reglementări.
        - 'Management Financiar și Bugetar' - Hotărâri privind bugetul și gestiunea financiară a resurselor publice.
        - 'Educație și Servicii Sociale' - Decizii în domeniul educației, sănătății, și al serviciilor sociale.
        - 'Reglementarea Pieței și Economiei' - Măsuri pentru reglementarea pieței, economiei locale și comerciale.
        - 'Transport și Infrastructură' - Hotărâri legate de transport public, drumuri și infrastructura locală.
        - 'Managementul Mediului și Energiei' - Decizii referitoare la protecția mediului, sustenabilitate și energie.
        - 'Sănătate și Siguranță' - Hotărâri legate de sănătatea publică și siguranța cetățenilor.
        - 'Cultură și Turism' - Inițiative care sprijină cultura, arta, și turismul.
        - 'Resurse Umane' - Aspecte legate de personalul administrației publice.
        - 'Sistem de parcare, Timpark' - Decizii privind reglementarea și administrarea sistemului de parcari Timpark.
        - 'Reabilitare Blocuri' - Hotărâri privind proiectele de reabilitare a blocurilor de locuințe.

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

def interoghează_date_gen(nume_categorie, path_df):
    df = pd.read_csv(path_df)
    
    df_filtrat = df[df['general_categories'] == nume_categorie]
    rezultate_text = df_filtrat['gpt_description']
    lista_hcl_categorie = df_filtrat['hcl_id']
    # print(rezultate_text)
    sorted_hcl = lista_hcl_categorie.sort_values(
    key=lambda x: x.str.split('/').apply(lambda y: (int(y[1]), int(y[0]))),
    ascending=False
    )
    return rezultate_text, sorted_hcl

def creează_prompt_final(interogare_utilizator, text_rezultat, n=2):
    prompt = f"""Ești un asistent care va răspunde la o întrebare folosind informații despre hotărâri ale consiliului local (HCL), furnizate într-un format JSON cu câmpurile: "Categorie", "Explicație", "Rezumat".

    **Întrebare utilizator**: "{interogare_utilizator}"

    **Informații despre HCL-uri**: {text_rezultat}

    Te rog să furnizezi un răspuns detaliat și structurat la întrebarea utilizatorului folosind informațiile de mai sus.

    Instrucțiuni pentru răspuns:
    1. **Rezumați întrebarea** în propriile tale cuvinte.
    2. **Prezentați un răspuns structurat și detaliat**, concentrându-vă pe ordine cronologică, cu accent pe hotărârile recente (anul 2024 și ulterior).
    3. **Formulați concluziile** clar și concis, folosind puncte de bullet sau paragrafe, abordând complet întrebarea utilizatorului.
    4. **La final**, listați cele mai relevante {n} exemple de HCL-uri în formatul:  
       - HCL: nr.[nr]/[an] si un json: "Categorie", "Explicație", "Rezumat".

    Această listă va ajuta la verificarea corectitudinii informațiilor oferite.
    """
    return prompt

# New Utility Functions for TimPark

def creează_prompt_final_timpark(interogare_utilizator, text_rezultat, n=3):
    prompt = f"""
    Ești un asistent care va răspunde la o întrebare folosind informații despre hotărâri ale consiliului local (HCL), furnizate într-un format 'HCL: nr.[nr]/[an]','Articole:','Motivatie:'

    **Întrebare utilizator**: "{interogare_utilizator}"
    
    **Informații despre HCL-uri**: {text_rezultat}

    Instrucțiuni pentru răspuns:
    1. **Rezumați întrebarea** în propriile tale cuvinte.
    2. **Prezentați un răspuns structurat și detaliat**, concentrându-vă pe ordine cronologică, cu accent pe hotărârile recente (anul 2024 și ulterior).
    3. **Formulați concluziile** clar și concis, folosind puncte de bullet sau paragrafe, abordând complet întrebarea utilizatorului.
    4. **La final**, listați cele mai relevante {n} exemple de HCL-uri în formatul:  
       - HCL: nr.[nr]/[an]

    Această listă va ajuta la verificarea corectitudinii informațiilor oferite.
    """
    return prompt
# Existing Endpoint

@app.post("/extrage_informatii/")
async def extrage_informatii(query: UserQuery):
    interogare_utilizator = query.interogare_utilizator
   

    path_df = 'all_summarized_hcl_gpt_desc_added_with_general_categ.csv'
    prompt = creează_prompt_extragere_romana(interogare_utilizator)
    
    text_răspuns = obține_informații_extrase(prompt)
    date_extrase = procesează_răspunsul(text_răspuns)

    if date_extrase is None or 'category' not in date_extrase:
        raise HTTPException(status_code=400, detail="Nu s-a putut extrage categoria. Verifică interogarea și încearcă din nou.")
    
    rezultate_text,sorted_hcl = interoghează_date_gen(date_extrase['category'], path_df)
    rezultate_text = rezultate_text.tolist()
    rezultate_concatenate = "\n\n".join(rezultate_text)
    prompt_final = creează_prompt_final(interogare_utilizator, rezultate_concatenate, n=2)

    răspuns_final = obține_informații_extrase(prompt_final)
    
    răspuns_final = "**Categorie:**:" + date_extrase['category'] + "\n"+"**HCL-uri care apartin Categoriei:**" + "\n" + sorted_hcl.head(5).to_string(index=False)+ "\n" + răspuns_final +"\n"
    return {
        "raspuns_final": răspuns_final
    }


# New Endpoint for TimPark Information Extraction

@app.post("/extrage_timpark_informatii/")
async def extrage_timpark_informatii(query: TimParkQuery):
    interogare_utilizator = query.interogare_utilizator

    # Define the path to the TimPark-specific CSV
    path_df = 'all_hcl_timpark_with_articole_motivatie_original_as_gpt_desc.csv'

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

    return {"raspuns_final": răspuns_final}

import re


# Main entry point to run the server directly from code
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
