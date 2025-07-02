# pages/admin.py
import streamlit as st

def admin_dashboard(supabase):
    st.header("Panel de Administración")
    st.info("Las tarjetas se agrupan por estado. Pulsa el botón para avanzar al siguiente.")

    # -----------------------------
    # 0. Datos de sesión del admin
    # -----------------------------
    admin_uid = st.session_state.user.id         # guardado en el login
    statuses   = ["Ingresada", "En_Curso", "Finalizada"]
    cols       = st.columns(len(statuses))

    # -----------------------------
    # 1. Traer tickets + solicitante
    #    ¡incluimos id y full_name!
    # -----------------------------
    data = (
        supabase
        .table("tickets")
        .select("id,title,description,status,created_at,users!inner(id,full_name)")
        .order("created_at")
        .execute()
        .data
    )

    def next_status(current: str) -> str:
        idx = statuses.index(current)
        return statuses[min(idx + 1, len(statuses) - 1)]

    # -----------------------------
    # 2. Render de columnas Kanban
    # -----------------------------
    for status, col in zip(statuses, cols):
        col.subheader(status)

        for t in filter(lambda x: x["status"] == status, data):
            full_name = t["users"]["full_name"]      # siempre presente por !inner
            with col.container(border=True):
                col.markdown(f"**{t['title']}**")
                col.write(t["description"])
                col.caption(f"Solicitante: {full_name}")

                if status != "Finalizada":
                    if col.button("➡️ Avanzar", key=t["id"]):
                        new_status = next_status(status)

                        # 2.1 Actualizar ticket
                        supabase.table("tickets") \
                                .update({"status": new_status}) \
                                .eq("id", t["id"]) \
                                .execute()

                        # 2.2 Insertar en historial con el UID del admin
                        supabase.table("ticket_status_history").insert({
                            "ticket_id":        t["id"],
                            "status":           new_status,
                            "changed_by_user_id": admin_uid,
                        }).execute()

                        st.success(f"Ticket #{t['id'][:8]} → {new_status}")
                        st.rerun()  # Streamlit ≥ 1.32
