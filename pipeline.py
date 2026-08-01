import os
import requests
from supabase import create_client, Client

def main():
    print("Iniciando el script...")

    # 1. Conectar a Supabase
    # GitHub Actions nos pasará estas contraseñas en secreto más tarde
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url_supabase, key_supabase)

    # 2. Conectar a la API
    # 👇👇 CAMBIA ESTO POR LA URL REAL DE TU API 👇👇
    api_url = "https://dummyjson.com/c/513d-dd56-4850-8d59" 
    print(f"Descargando datos desde: {api_url}")
    response = requests.get(api_url)
    
    # Tu API devuelve un JSON con una clave "comments"
    comentarios = response.json().get("comments", [])

    # 3. Preparar los datos para insertarlos en Supabase
    datos_a_insertar = []
    for c in comentarios:
        datos_a_insertar.append({
            "texto_comentario": c.get("text", "")
        })

    # 4. Insertar en la base de datos
    print(f"Insertando {len(datos_a_insertar)} comentarios en Supabase...")
    try:
        supabase.table("comentarios_extraidos").insert(datos_a_insertar).execute()
        print("¡Inserción completada con éxito!")
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")

if __name__ == "__main__":
    main()
