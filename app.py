import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Directorio BNI", page_icon="📇", layout="centered")

st.title("📇 Directorio BNI")

# URL de tu Google Sheet limpia y corregida
SHEET_URL = "https://docs.google.com/spreadsheets/d/15SjZZq4urwMP8eH8q44JnjyVNRKR_DThF0bN9FWHs1A/edit?usp=sharing"

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["ID", "Nombre", "Empresa", "Especialidad", "Tecnologias", "Pais", "Palabras_Clave"])

def save_data(df):
    conn.update(spreadsheet=SHEET_URL, data=df)
    st.cache_data.clear()

# Navegación entre pestañas
tab1, tab2 = st.tabs(["🔍 Buscar y Editar", "➕ Agregar Miembro"])

df = get_data()

with tab1:
    search_term = st.text_input("Buscar por palabra clave, especialidad, tecnología o país:", placeholder="Ej: Fortinet, Veeam, Perú, Cloud...")
    
    if not df.empty:
        if search_term:
            term = search_term.lower()
            filtered_df = df[
                df["Nombre"].astype(str).str.lower().str.contains(term) |
                df["Empresa"].astype(str).str.lower().str.contains(term) |
                df["Especialidad"].astype(str).str.lower().str.contains(term) |
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
                    u_nombre = st.text_input("Nombre", value=str(row["Nombre"]))
                    u_empresa = st.text_input("Empresa", value=str(row["Empresa"]))
                    u_especialidad = st.text_input("Especialidad", value=str(row["Especialidad"]))
                    u_tecnologias = st.text_input("Tecnologías", value=str(row["Tecnologias"]))
                    u_pais = st.text_input("País", value=str(row["Pais"]))
                    u_palabras = st.text_area("Palabras Clave", value=str(row["Palabras_Clave"]))
                    
                    if st.form_submit_button("Guardar Cambios"):
                        df.loc[idx, ["Nombre", "Empresa", "Especialidad", "Tecnologias", "Pais", "Palabras_Clave"]] = [
                            u_nombre, u_empresa, u_especialidad, u_tecnologias, u_pais, u_palabras
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
