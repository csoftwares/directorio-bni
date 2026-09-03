import streamlit as st
import pandas as pd
import requests

# Configuración de página
st.set_page_config(page_title="Directorio BNI", page_icon="📇", layout="centered")

st.title("📇 Directorio BNI")

# URL de la API de Apps Script que creaste
API_URL = "https://script.google.com/macros/s/AKfycby8VODPUFgD1ignbPwmRzWX6N1wdq4U_B1OZz3n4ABYLATmv6c6PfEOfBip4y5U-cp5nQ/exec"

def clean_val(val):
    if pd.isna(val) or val is None or str(val).strip().lower() in ["nan", "none", "null"]:
        return ""
    return str(val).strip()

@st.cache_data(ttl=5)
def get_data():
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df.dropna(how="all")
        elif len(data) == 1:
            return pd.DataFrame(columns=data[0])
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
    return pd.DataFrame(columns=["ID", "Nombre", "Empresa", "Especialidad", "Telefono", "Email", "Tecnologias", "Pais", "Palabras_Clave"])

def save_data(df):
    data_to_send = [df.columns.tolist()] + df.fillna("").values.tolist()
    try:
        res = requests.post(API_URL, json=data_to_send, timeout=15)
        if res.status_code == 200:
            st.cache_data.clear()
            return True
        else:
            st.error("Error al guardar en Google Sheets.")
            return False
    except Exception as e:
        st.error(f"Error de conexión al guardar: {e}")
        return False

# Cargar Datos
df = get_data()

tab1, tab2 = st.tabs(["🔍 Buscar y Editar", "➕ Agregar Miembro"])

# ---------------------------------------------------------
# TAB 1: BUSCAR Y EDITAR
# ---------------------------------------------------------
with tab1:
    search_term = st.text_input(
        "Buscar por palabra clave, especialidad, teléfono, email, tecnología o país:",
        placeholder="Ej: Fortinet, Veeam, +57..., correo@..."
    )
    
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
            nombre = clean_val(row.get("Nombre"))
            empresa = clean_val(row.get("Empresa"))
            pais = clean_val(row.get("Pais"))
            telefono = clean_val(row.get("Telefono"))
            
            # Construir título limpio del expander
            header_str = f"🔴 {nombre}"
            if empresa:
                header_str += f" — {empresa}"
            if pais:
                header_str += f" ({pais})"
            
            with st.expander(header_str):
                # Botón directo de WhatsApp si hay teléfono
                if telefono:
                    num_clean = "".join(filter(str.isdigit, telefono))
                    if num_clean:
                        st.markdown(f"[💬 Abrir Chat de WhatsApp](https://wa.me/{num_clean})", unsafe_allow_html=True)
                
                with st.form(key=f"edit_form_{idx}"):
                    u_nombre = st.text_input("Nombre completo", value=nombre)
                    u_empresa = st.text_input("Empresa", value=empresa)
                    u_especialidad = st.text_input("Especialidad", value=clean_val(row.get("Especialidad")))
                    u_telefono = st.text_input("Teléfono / WhatsApp", value=telefono)
                    u_email = st.text_input("Correo Electrónico", value=clean_val(row.get("Email")))
                    u_tecnologias = st.text_input("Tecnologías", value=clean_val(row.get("Tecnologias")))
                    u_pais = st.text_input("País", value=pais)
                    u_palabras = st.text_area("Palabras Clave / Etiquetas", value=clean_val(row.get("Palabras_Clave")))
                    
                    if st.form_submit_button("💾 Guardar Cambios"):
                        df.loc[idx, ["Nombre", "Empresa", "Especialidad", "Telefono", "Email", "Tecnologias", "Pais", "Palabras_Clave"]] = [
                            u_nombre, u_empresa, u_especialidad, u_telefono, u_email, u_tecnologias, u_pais, u_palabras
                        ]
                        if save_data(df):
                            st.success("¡Registro actualizado con éxito!")
                            st.rerun()
    else:
        st.info("No hay miembros registrados aún.")

# ---------------------------------------------------------
# TAB 2: AGREGAR NUEVO MIEMBRO
# ---------------------------------------------------------
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
        
        if st.form_submit_button("➕ Guardar Miembro"):
            if n_nombre.strip():
                try:
                    max_id = pd.to_numeric(df["ID"], errors="coerce").max()
                    new_id = int(max_id + 1) if pd.notna(max_id) else 1
                except Exception:
                    new_id = 1
                    
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
                if save_data(updated_df):
                    st.success(f"¡Miembro '{n_nombre}' agregado con éxito!")
                    st.rerun()
            else:
                st.error("El nombre completo es un campo obligatorio.")
