import streamlit as st
from supabase_client import supabase          # conexión global
from pages.clients import client_portal       # 👉 tu módulo cliente
from pages.admin import admin_dashboard       # 👉 tu módulo admin
st.set_page_config(page_title="Plataforma de Tickets", layout="wide")




# -------------------------
# 1. LOGIN lateral (demo)
# -------------------------
if "user" not in st.session_state:
    with st.sidebar:
        st.subheader("Iniciar sesión")
        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                if res.user:
                    st.session_state.user = res.user      # guarda la sesión
                    st.success("✅ Inicio de sesión correcto")
                    st.rerun()               # recarga la página
                else:
                    st.error("Credenciales incorrectas")
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()  # evitamos que cargue el resto de la página

# -------------------------
# 2. Perfil + routing
# -------------------------
uid = st.session_state.user.id
profile = (
    supabase.table("users")
    .select("id, email, role, full_name")
    .eq("id", uid)
    .single()
    .execute()
    .data
)

if not profile:
    st.error("Tu perfil aún no existe. Avísale al administrador.")
    st.stop()

# Mensaje de bienvenida
st.sidebar.success(f"Sesión: {profile['full_name']} · {profile['role']}")

# Enruta según rol
if profile["role"] == "admin":
    admin_dashboard(supabase)                     # pasa supabase dentro del módulo
else:
    client_portal(profile["email"], supabase)
