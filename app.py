import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Directorio BNI", page_icon="📇", layout="centered")

st.title("📇 Directorio BNI")

SHEET_URL = "https://docs.google.com/spreadsheets/d/15SjZZq4urwMP8eH8q44JnjyVNRKR_DThF0bN9FWHs1A/edit?usp=sharing"

# Conexión nativa de Streamlit a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        df = df.dropna(how="all")
        # Asegurar columnas obligatorias
        expected_cols = ["ID", "Nombre", "Empresa", "Especialidad", "Telefono", "Email", "Tecnologias", "Pais", "Palabras_Clave"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=["ID", "Nombre", "Empresa", "Especialidad", "Telefono", "Email", "Tecnologias", "Pais", "Palabras_Clave"])

def save_data(df):
    conn.update(spreadsheet=SHEET_URL, data=df)
    st.cache_data.clear()

tab1, tab2 = st.tabs(["🔍 Buscar y Editar", "➕ Agregar Miembro"])

df = get_data()

with tab1:
    search_term = st.text_input("Buscar por palabra clave, especialidad, teléfono, email, tecnología o país:", placeholder="Ej: Fortinet, Veeam, +57..., correo@...)")
    
    if not df.empty:
        if search_term:
            term = search_term.lower()
            filtered_df = df[
                df["Nombre"].astype(str).str.lower().str.contains(term) |
                df["Empresa"].astype(str).str.lower().str.contains(term) |
                df["Especialidad"].astype(str).str.lower().str.contains(term) |
                df["Telefono"].astype(str).str.lower().str.contains(term) |
                df["Email"].astype(str).str.lower().str.contains(term) |
                df["Tecnologias"].astype(str).str.lower().str.contains(term) |
                df["Pais"].astype(str).str.lower().str.contains(term) |
                df["Palabras_Clave"].astype(str).str.lower().str.contains(term)
            ]
        else:
            filtered_df = df

        st.caption(f"Contactos encontrados: {len(filtered_df)}")
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🔴 {row['Nombre']} — {row['Empresa']} ({row['Pais']})"):
                with st.form(key=f"edit_form_{idx}"):
                    u_nombre = st.text_input("Nombre", value=str(row.get("Nombre", "")))
                    u_empresa = st.text_input("Empresa", value=str(row.get("Empresa", "")))
                    u_especialidad = st.text_input("Especialidad", value=str(row.get("Especialidad", "")))
                    u_telefono = st.text_input("Teléfono / WhatsApp", value=str(row.get("Telefono", "")))
                    u_email = st.text_input("Correo Electrónico", value=str(row.get("Email", "")))
                    u_tecnologias = st.text_input("Tecnologías", value=str(row.get("Tecnologias", "")))
                    u_pais = st.text_input("País", value=str(row.get("Pais", "")))
                    u_palabras = st.text_area("Palabras Clave", value=str(row.get("Palabras_Clave", "")))
                    
                    if st.form_submit_button("Guardar Cambios"):
                        df.loc[idx, ["Nombre", "Empresa", "Especialidad", "Telefono", "Email", "Tecnologias", "Pais", "Palabras_Clave"]] = [
                            u_nombre, u_empresa, u_especialidad, u_telefono, u_email, u_tecnologias, u_pais, u_palabras
                        ]
                        save_data(df)
                        st.success("¡Registro actualizado!")
                        st.rerun()
    else:
        st.info("No hay miembros registrados aún.")

with tab2:
    st.subheader("Agregar Nuevo Miembro")
    with st.form(key="add_form"):
        n_nombre = st.text_input("Nombre completo *")
        n_empresa = st.text_input("Empresa")
        n_especialidad = st.text_input("Especialidad")
        n_telefono = st.text_input("Teléfono / WhatsApp")
        n_email = st.text_input("Correo Electrónico")
        n_tecnologias = st.text_input("Tecnologías / Servicios")
        n_pais = st.text_input("País")
        n_palabras = st.text_area("Palabras Clave / Etiquetas")
        
        if st.form_submit_button("Guardar Miembro"):
            if n_nombre.strip():
                new_id = int(df["ID"].max() + 1) if not df.empty and "ID" in df.columns and pd.notna(df["ID"].max()) else 1
                new_row = pd.DataFrame([{
                    "ID": new_id,
                    "Nombre": n_nombre,
                    "Empresa": n_empresa,
                    "Especialidad": n_especialidad,
                    "Telefono": n_telefono,
                    "Email": n_email,
                    "Tecnologias": n_tecnologias,
                    "Pais": n_pais,
                    "Palabras_Clave": n_palabras
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                save_data(updated_df)
                st.success(f"¡Miembro '{n_nombre}' agregado con éxito!")
                st.rerun()
            else:
                st.error("El nombre es obligatorio.")
