import streamlit as st
from datetime import datetime
from supabase_client import supabase

def client_portal(user_email: str,supabase):
    st.header("Mis Solicitudes")

    # 1. Crear ticket
    with st.expander("📝 Crear nueva solicitud"):
        templates_resp = supabase.table("task_templates").select("id,name").execute()
        template_opts = {tpl["name"]: tpl["id"] for tpl in templates_resp.data}
        template_name = st.selectbox("Tipo de tarea", (*template_opts.keys(), "Personalizada"))
        title = st.text_input("Título")
        desc = st.text_area("Descripción")
        custom_hours = None
        if template_name == "Personalizada":
            custom_hours = st.number_input("Duración estimada (h)", min_value=1)

        if st.button("Enviar"):
            user_id = st.session_state["user"].id 
            supabase.table("tickets").insert({
                "requester_id": user_id,
                "template_id": template_opts.get(template_name),
                "title": title,
                "description": desc,
                "custom_duration_hours": custom_hours,
            }).execute()
            st.success("Solicitud registrada ✅")
            st.rerun()

    # 2. Listado de tickets
    tickets = (
        supabase
        .table("tickets")
        .select("*")
        .eq("requester_id", supabase.table("users").select("id").eq("email", user_email).single().execute().data["id"])
        .order("created_at", desc=True)
        .execute()
        .data
    )
    for t in tickets:
        st.subheader(f"#{t['id'][:8]} · {t['title']}")
        st.markdown(f"**Estado:** {t['status']}")
          # ⬇️ Manejo seguro de fecha
        iso_str = t["created_at"]
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        st.caption(f"Creado: {dt:%d-%m-%Y %H:%M}")

        st.write(t["description"])
        st.divider()