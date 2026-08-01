import os
import re
import requests
from supabase import create_client, Client
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 1. Función de limpieza (la misma que usamos para entrenar)
def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r'http\S+|www\.\S+', ' ', texto)
    texto = re.sub(r'@\w+', ' ', texto)
    texto = re.sub(r'#\w+', ' ', texto)
    texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)
    texto = re.sub(r'(.)\1{2,}', r'\1', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def main():
    print("Iniciando el pipeline con IA...")

    # 2. Conectar a Supabase
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url_supabase, key_supabase)

    # 3. Descargar y cargar el modelo de Hugging Face
    # 👇👇 CAMBIA ESTO POR TU USUARIO Y NOMBRE DE MODELO 👇👇
    HF_MODEL = "jonybaq001/modelo-odio-no-odio" 
    print(f"Descargando modelo desde Hugging Face: {HF_MODEL} (esto puede tardar un minuto)...")
    
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    modelo = AutoModelForSequenceClassification.from_pretrained(HF_MODEL)
    modelo.eval() # Poner en modo predicción
    print("¡Modelo cargado en memoria!")

    # 4. Conectar a la API y obtener comentarios
    api_url = "https://dummyjson.com/c/513d-dd56-4850-8d59" # ¡CAMBIA ESTO POR TU API REAL!
    print(f"Descargando comentarios desde: {api_url}")
    response = requests.get(api_url)
    comentarios = response.json().get("comments", [])

    # 5. Analizar cada comentario con la IA
    datos_a_insertar = []
    for c in comentarios:
        texto_original = c.get("text", "")
        texto_limpio = limpiar_texto(texto_original)
        
        # Si el texto está vacío después de limpiar, lo saltamos
        if not texto_limpio:
            continue
            
        # Tokenizar y predecir
        inputs = tokenizer(texto_limpio, truncation=True, padding='max_length', max_length=64, return_token_type_ids=False, return_tensors='pt')
        
        with torch.no_grad():
            logits = modelo(**inputs).logits[0]
            prediccion = torch.argmax(logits).item() # 0 = No Odio, 1 = Odio
            
        es_odio = bool(prediccion) # Convertimos 1/0 a True/False para la base de datos
        
        datos_a_insertar.append({
            "texto_comentario": texto_original,
            "es_odio": es_odio
        })

    print(f"IA ha analizado {len(datos_a_insertar)} comentarios. Insertando en Supabase...")

    # 6. Insertar en la base de datos
    try:
        supabase.table("comentarios_extraidos").insert(datos_a_insertar).execute()
        print("¡Inserción completada con éxito!")
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")

if __name__ == "__main__":
    main()
