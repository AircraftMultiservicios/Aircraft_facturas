import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURACIÓN DE LA EMPRESA ---
NOMBRE_EMPRESA = "AIRCRAFT MULTISERVICIOS"
SLOGAN = "SISTEMAS DE CLIMATIZACIÓN Y REFRIGERACIÓN"
NIT = "1087200869"
TELEFONO = "+57 302 681 2764"
CORREO = "aircraftmultiservicios30@gmail.com"
ARCHIVO_CONTADOR = "contador_cotizaciones.txt"

# --- FUNCIONES DE SOPORTE ---
def obtener_siguiente_numero():
    if not os.path.exists(ARCHIVO_CONTADOR):
        return 1
    with open(ARCHIVO_CONTADOR, "r") as f:
        try:
            return int(f.read().strip())
        except:
            return 1

def incrementar_contador(numero):
    with open(ARCHIVO_CONTADOR, "w") as f:
        f.write(str(numero + 1))

# --- GENERADOR DE PDF ---
def generar_pdf_cotizacion(items, total_neto, numero_cot):
    pdf = FPDF(format='Letter')
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    # --- ENCABEZADO ---
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    try:
        if os.path.exists(ruta_logo):
            pdf.image(ruta_logo, x=12, y=10, w=22)
    except:
        pass

    # Datos Empresa (Izquierda)
    pdf.set_xy(12, 35)
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 80, 180)
    pdf.cell(0, 6, "AIRCRAFT", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "MULTISERVICIOS", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Arial", "", 7)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 4, SLOGAN, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Arial", "B", 7)
    pdf.cell(0, 4, f"NIT: {NIT}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 7)
    pdf.cell(0, 4, f"Teléfono: {TELEFONO}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4, f"Correo: {CORREO}", new_x="LMARGIN", new_y="NEXT")

    # Recuadro Cotización (Derecha)
    pdf.set_xy(120, 10)
    pdf.set_draw_color(200, 200, 200)
    pdf.cell(75, 32, "", border=1)
    pdf.set_xy(120, 12)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(75, 6, "COTIZACIÓN", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_draw_color(30, 80, 180)
    pdf.set_line_width(0.5)
    pdf.line(125, 19, 190, 19)
    
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(120, 21)
    pdf.cell(75, 5, f"Número: #2026-{numero_cot:03d}", align="C", new_x="LMARGIN", new_y="NEXT")
    fecha_actual = datetime.now().strftime("%d de %B, %Y")
    meses = {"January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril", "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto", "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"}
    for k, v in meses.items():
        fecha_actual = fecha_actual.replace(k, v)
    pdf.cell(75, 5, f"Fecha: {fecha_actual}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(75, 5, "Validez: 15 días calendario", align="C", new_x="LMARGIN", new_y="NEXT")

    # Título Tabla
    pdf.set_xy(12, 60)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(30, 80, 180)
    pdf.cell(0, 5, "DETALLE DEL PRESUPUESTO", new_x="LMARGIN", new_y="NEXT")
    
    # --- TABLA DE ITEMS ---
    pdf.set_xy(12, 66)
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(30, 80, 180)
    pdf.set_draw_color(30, 80, 180)
    
    # Encabezados
    pdf.cell(10, 7, "ÍTEM", border=1, fill=True, align="C")
    pdf.cell(88, 7, "DESCRIPCIÓN DEL MATERIAL / SERVICIO", border=1, fill=True, align="C")
    pdf.cell(12, 7, "CANT.", border=1, fill=True, align="C")
    pdf.cell(18, 7, "UNIDAD", border=1, fill=True, align="C")
    pdf.cell(22, 7, "UNITARIO", border=1, fill=True, align="C")
    pdf.cell(23, 7, "TOTAL", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    # Filas
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_font("Arial", "", 7)
    
    for i, item in enumerate(items, start=1):
        lineas = item['descripcion'].split('\n')
        altura_fila = max(8, (len(lineas) * 4) + 2) 
        
        x_actual = pdf.get_x()
        y_actual = pdf.get_y()

        pdf.cell(10, altura_fila, str(i), border=1, align="C")
        pdf.cell(88, altura_fila, "", border=1)
        pdf.set_xy(x_actual + 12, y_actual + 1)
        
        es_primera = True
        for linea in lineas:
            if linea.strip():
                if not es_primera and linea.strip().startswith('-'):
                    # AQUI ESTA EL TRUCO: Usamos la viñeta y codificamos en latin-1
                    pdf.cell(4, 4, chr(149).encode('latin-1').decode('latin-1'), align="C") 
                    pdf.cell(0, 4, linea.strip()[1:].strip().encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.cell(0, 4, linea.strip().encode('latin-1', 'replace').decode('latin-1'), new_x="LMARGIN", new_y="NEXT")
                es_primera = False
                
        pdf.set_xy(x_actual + 98, y_actual)
        pdf.cell(12, altura_fila, str(item['cantidad']), border=1, align="C")
        pdf.cell(18, altura_fila, item['unidad'], border=1, align="C")
        pdf.cell(22, altura_fila, f"${item['precio']:,.0f}".replace(",", "."), border=1, align="R")
        pdf.cell(23, altura_fila, f"${item['total']:,.0f}".replace(",", "."), border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    # --- TOTALES ---
    pdf.ln(3)
    x_totales = 125
    pdf.set_x(x_totales)
    pdf.set_font("Arial", "", 8)
    pdf.cell(40, 7, "Subtotal:", border=1, align="L")
    pdf.cell(30, 7, f"${total_neto:,.0f}".replace(",", "."), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(x_totales)
    pdf.cell(40, 7, "Impuestos (IVA 0%):", border=1, align="L")
    pdf.cell(30, 7, "$0", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(x_totales)
    pdf.set_text_color(30, 80, 180)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(40, 7, "Total Neto:", border=1, align="L")
    pdf.cell(30, 7, f"${total_neto:,.0f}".replace(",", "."), border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    # --- CONDICIONES COMERCIALES ---
    pdf.set_y(215)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(245, 245, 245)
    
    pdf.set_fill_color(30, 80, 180)
    pdf.cell(2, 35, "", fill=True)
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_x(14)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, " CONDICIONES COMERCIALES", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(14)
    pdf.set_font("Arial", "", 7)
    condiciones = [
        ("• Forma de Pago: ", "Anticipo establecido para la compra de materiales y saldo restante contra entrega a satisfacción de los trabajos realizados."),
        ("• Tiempo de Ejecución: ", "A convenir y programar de manera conjunta tras la confirmación formal del servicio."),
        ("• Garantía: ", "Aplica garantía sobre el servicio técnico y la mano de obra especializada brindada."),
        ("• Exclusiones: ", "No se contemplan obras civiles mayores, resanes de pintura profundos ni acometidas eléctricas externas al alcance mencionado.")
    ]
    
    for titulo, texto in condiciones:
        # Codificamos también las condiciones para evitar el error de caracteres
        titulo_seguro = titulo.encode('latin-1', 'replace').decode('latin-1')
        texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", "B", 7)
        pdf.cell(28, 5, titulo_seguro, new_x="RIGHT")
        pdf.set_font("Arial", "", 7)
        pdf.multi_cell(0, 5, texto_seguro, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(14)

    return bytes(pdf.output())

# --- INTERFAZ GRÁFICA (STREAMLIT) ---
st.set_page_config(page_title="Cotizador - AIRCRAFT", page_icon="❄️", layout="wide")

st.title("❄️ Generador de Cotizaciones")
st.subheader("AIRCRAFT MULTISERVICIOS")

if 'items_cotizacion' not in st.session_state:
    st.session_state.items_cotizacion = []

st.write("### Añadir Material o Servicio")

with st.form("form_item", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 1, 1, 2])
    with col1:
        # El truco: le decimos al usuario que empiece con "- " para que salga la viñeta
        desc = st.text_area("Descripción (Escribe '-' y un espacio para cada viñeta)", height=100, placeholder="- Ítem 1\n- Ítem 2\n- Ítem 3")
    with col2:
        cant = st.number_input("Cant.", min_value=1, step=1)
    with col3:
        unidad = st.selectbox("Unidad", ["Global", "Servicio", "Und", "Metro", "Caja"])
    with col4:
        precio = st.number_input("Precio Unitario ($)", min_value=0, step=1000)
    
    agregar = st.form_submit_button("➕ Añadir a la cotización", type="primary")

if agregar:
    if desc:
        total_item = cant * precio
        st.session_state.items_cotizacion.append({
            "descripcion": desc, 
            "cantidad": cant, 
            "unidad": unidad,
            "precio": precio,
            "total": total_item
        })
    else:
        st.error("Escribe una descripción.")

# Mostrar lista y Totales
if st.session_state.items_cotizacion:
    st.write("### Ítems agregados")
    total_general = 0
    
    for i, item in enumerate(st.session_state.items_cotizacion):
        total_general += item['total']
        desc_web = item['descripcion'].replace('\n', ' | ')
        if len(desc_web) > 80: desc_web = desc_web[:80] + "..."
        st.write(f"**{i+1}.** {desc_web} — *{item['cantidad']} {item['unidad']} x ${item['precio']:,.0f}* = **${item['total']:,.0f}**")
    
    st.write(f"## Total Neto: ${total_general:,.0f}")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Borrar todo"):
            st.session_state.items_cotizacion = []
            st.rerun()
            
    with col_btn2:
        if st.button("Generar Cotización PDF", type="primary"):
            numero_actual = obtener_siguiente_numero()
            
            pdf_bytes = generar_pdf_cotizacion(st.session_state.items_cotizacion, total_general, numero_actual)
            incrementar_contador(numero_actual)
            
            st.success("✅ PDF Generado con éxito. Todo en una sola página.")
            st.download_button(
                label="⬇️ Descargar Cotización PDF",
                data=pdf_bytes,
                file_name=f"Cotizacion_{numero_actual:03d}.pdf",
                mime="application/pdf"
            )
else:
    st.info("Aún no has agregado ítems a la cotización.")
