# main_debug.py
import streamlit as st
from supabase import create_client

st.title("🛠️ Test Streamlit + Supabase")

url = st.secrets.get("supabase_url")
key = st.secrets.get("supabase_anon_key")
st.write("URL:", url)

if not url or not key:
    st.error("No hay secretos")
    st.stop()

sb = create_client(url, key)

try:
    res = sb.table("task_templates").select("*").execute()
    st.success("Conexión OK")
    st.json(res.data)
except Exception as e:
    st.error(f"Error consultando Supabase: {e}")
