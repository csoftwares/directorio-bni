import streamlit as st
import sqlite3
import pandas as pd

# Configuración de la aplicación
st.set_page_config(page_title="Directorio BNI", page_icon="📇", layout="centered")

# --- CONEXIÓN A BASE DE DATOS LOCAL (SQLite) ---
def init_db():
    conn = sqlite3.connect('bni_contactos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            correo TEXT,
            telefono TEXT,
            empresa TEXT,
            pais TEXT,
            dedicacion TEXT,
            explicacion TEXT,
            palabras_clave TEXT
        )
    ''')
    conn.commit()
    conn.close()

def obtener_miembros():
    conn = sqlite3.connect('bni_contactos.db')
    df = pd.read_sql_query("SELECT * FROM miembros", conn)
    conn.close()
    return df

def agregar_miembro(nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave):
    conn = sqlite3.connect('bni_contactos.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO miembros (nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave))
    conn.commit()
    conn.close()

def actualizar_miembro(id_miembro, nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave):
    conn = sqlite3.connect('bni_contactos.db')
    c = conn.cursor()
    c.execute('''
        UPDATE miembros 
        SET nombre=?, correo=?, telefono=?, empresa=?, pais=?, dedicacion=?, explicacion=?, palabras_clave=?
        WHERE id=?
    ''', (nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave, id_miembro))
    conn.commit()
    conn.close()

# Inicializar DB
init_db()

# Cargar miembros iniciales si la base de datos está vacía
df_actual = obtener_miembros()
if df_actual.empty:
    agregar_miembro(
        "Oscar Martinez", "oscar@nexcloud.pe", "+51 900 000 001", "Nexcloud", "Perú",
        "Servicios en Nube (Google Cloud, Workspace) y Backups (Veeam)",
        "Especialistas en soluciones multinube, respaldo de datos con Veeam y migración de correo o servidores hacia Google Cloud.",
        "google workspace veeam cloud backup migracion nube peru nexcloud"
    )
    agregar_miembro(
        "Hector Cerapio", "hector@netleadcloud.com", "+51 900 000 002", "netlead cloud", "Perú / Colombia",
        "Redes, Virtualización, Switch, Firewall y Ciberseguridad",
        "Servicios e implementación de infraestructura HP Aruba, Fortinet, Clearpass y NAT. Cobertura en Perú y operación propia en Colombia, enfocado en sectores Retail, Salud y Finanzas.",
        "virtualizacion switch firewall nat aruba fortinet redes alta disponibilidad colombia peru netlead"
    )
    df_actual = obtener_miembros()

# --- INTERFAZ GRÁFICA ---
st.title("📇 Directorio BNI")

tab1, tab2 = st.tabs(["🔍 Buscar y Editar", "➕ Agregar Miembro"])

# ----------------- TAB 1: BUSCADOR Y EDICIÓN -----------------
with tab1:
    busqueda = st.text_input("Buscar por palabra clave, especialidad, tecnología o país:", placeholder="Ej: Fortinet, Veeam, Perú, Cloud...")
    
    miembros_list = obtener_miembros().to_dict(orient='records')
    resultados = []
    
    if busqueda:
        termino = busqueda.lower()
        for m in miembros_list:
            cadena_completa = f"{m['nombre']} {m['correo']} {m['telefono']} {m['empresa']} {m['pais']} {m['dedicacion']} {m['explicacion']} {m['palabras_clave']}".lower()
            if termino in cadena_completa:
                resultados.append(m)
    else:
        resultados = miembros_list

    st.caption(f"Contactos encontrados: {len(resultados)}")
    st.divider()

    for m in resultados:
        with st.expander(f"🔴 **{m['nombre']}** — {m['empresa']} ({m['pais']})"):
            st.markdown(f"**A qué se dedica:** {m['dedicacion']}")
            st.markdown(f"**Explicación:** {m['explicacion']}")
            st.markdown(f"📧 **Correo:** {m['correo']}")
            st.markdown(f"📞 **Teléfono:** {m['telefono']}")
            st.markdown(f"🏷️ **Palabras clave:** {m['palabras_clave']}")
            
            # --- FORMULARIO DE EDICIÓN DESPLEGABLE ---
            with st.popover("✏️ Editar este registro"):
                with st.form(f"edit_form_{m['id']}", clear_on_submit=False):
                    edit_nombre = st.text_input("Nombre completo", value=m['nombre'])
                    edit_correo = st.text_input("Correo electrónico", value=m['correo'])
                    edit_telefono = st.text_input("Teléfono / WhatsApp", value=m['telefono'])
                    edit_empresa = st.text_input("Empresa", value=m['empresa'])
                    edit_pais = st.text_input("País", value=m['pais'])
                    edit_dedicacion = st.text_input("A qué se dedica", value=m['dedicacion'])
                    edit_explicacion = st.text_area("Explicación", value=m['explicacion'])
                    edit_palabras_clave = st.text_input("Palabras clave", value=m['palabras_clave'])
                    
                    btn_actualizar = st.form_submit_button("Guardar Cambios")
                    
                    if btn_actualizar:
                        actualizar_miembro(
                            m['id'], edit_nombre, edit_correo, edit_telefono, 
                            edit_empresa, edit_pais, edit_dedicacion, edit_explicacion, edit_palabras_clave
                        )
                        st.success("¡Registro actualizado correctamente!")
                        st.rerun()

# ----------------- TAB 2: AGREGAR NUEVO -----------------
with tab2:
    st.subheader("Registrar un nuevo miembro")
    with st.form("form_nuevo", clear_on_submit=True):
        nombre = st.text_input("Nombre completo *")
        correo = st.text_input("Correo electrónico")
        telefono = st.text_input("Teléfono / WhatsApp")
        empresa = st.text_input("Empresa *")
        pais = st.text_input("País *", value="Perú")
        dedicacion = st.text_input("A qué se dedica (Resumen corto) *")
        explicacion = st.text_area("Pequeña explicación de sus servicios *")
        palabras_clave = st.text_input("Palabras clave para buscarlo (separadas por espacio)")

        guardar = st.form_submit_button("Guardar Miembro")

        if guardar:
            if nombre and empresa and dedicacion:
                agregar_miembro(nombre, correo, telefono, empresa, pais, dedicacion, explicacion, palabras_clave)
                st.success(f"¡{nombre} guardado con éxito!")
                st.rerun()
            else:
                st.error("Por favor completa al menos los campos con *")