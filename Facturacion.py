import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y COLORES
# ==========================================
st.set_page_config(page_title="Facturación - Aircraft Multiservicios", page_icon="📄", layout="wide")

# Colores extraídos de tu imagen
AZUL_CORPORATIVO = colors.HexColor("#1F4E79")  # Azul oscuro del texto y líneas
AZUL_BARRA = colors.HexColor("#2E5C8A")        # Azul de las barras laterales
GRIS_FONDO = colors.HexColor("#F2F2F2")        # Gris claro de los cuadros
NEGRO = colors.HexColor("#000000")

# ==========================================
# FUNCIÓN PARA GENERAR EL PDF
# ==========================================
def generar_pdf(datos_empresa, datos_factura, datos_cliente, items, totales):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    # Estilos de texto
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'Titulo', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=AZUL_CORPORATIVO, alignment=1 # Centrado
    )
    estilo_subtitulo = ParagraphStyle(
        'Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=NEGRO, alignment=1
    )
    estilo_texto = ParagraphStyle(
        'Texto', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=NEGRO
    )
    estilo_seccion = ParagraphStyle(
        'Seccion', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=AZUL_CORPORATIVO, spaceAfter=5
    )

    # --- 1. CABECERA (Logo + Datos Empresa + Cuadro Factura) ---
    # Nota: Asegúrate de tener "logo.png" en la misma carpeta
    try:
        logo = Image("logo.png", width=1.2*inch, height=1.2*inch)
    except:
        logo = Paragraph("[Falta logo.png]", estilo_texto)

    texto_empresa = f"""
    <font color="#1F4E79" size="16"><b>{datos_empresa['nombre']}</b></font><br/>
    <font size="8">{datos_empresa['descripcion']}</font><br/>
    <font size="8"><b>NIT:</b> {datos_empresa['nit']}</font><br/>
    <font size="8"><b>Teléfono:</b> {datos_empresa['telefono']}</font><br/>
    <font size="8"><b>Correo:</b> {datos_empresa['correo']}</font>
    """
    col_empresa = Paragraph(texto_empresa, estilo_texto)

    # Cuadro de la Factura (simulando el cuadro "REPORTE TÉCNICO")
    info_factura = f"""
    <font size="12"><b>FACTURA DE VENTA</b></font><br/><br/>
    <font size="9">Número: <b>{datos_factura['numero']}</b></font><br/>
    <font size="9">Fecha: <b>{datos_factura['fecha']}</b></font>
    """
    col_factura = Paragraph(info_factura, estilo_subtitulo)
    
    # Tabla de cabecera (3 columnas)
    tabla_cabecera = Table([[logo, col_empresa, col_factura]], colWidths=[1.2*inch, 3.8*inch, 2.5*inch])
    tabla_cabecera.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (2,0), (2,0), 1, AZUL_CORPORATIVO), # Borde del cuadro de factura
        ('ALIGN', (2,0), (2,0), 'CENTER'),
        ('TOPPADDING', (2,0), (2,0), 10),
        ('BOTTOMPADDING', (2,0), (2,0), 10),
    ]))
    elements.append(tabla_cabecera)
    elements.append(Spacer(1, 20))

    # --- 2. DATOS DEL CLIENTE Y FACTURA (Simulando los dos cuadros grises) ---
    texto_cliente = f"""
    <font color="#1F4E79"><b>DATOS DEL CLIENTE</b></font><br/>
    <font size="9">Nombre: {datos_cliente['nombre']}</font><br/>
    <font size="9">NIT/CC: {datos_cliente['cedula']}</font><br/>
    <font size="9">Teléfono: {datos_cliente['telefono']}</font><br/>
    <font size="9">Dirección: {datos_cliente['direccion']}</font>
    """
    col_cliente = Paragraph(texto_cliente, estilo_texto)

    texto_pago = f"""
    <font color="#1F4E79"><b>INFORMACIÓN DE PAGO</b></font><br/>
    <font size="9">Método: {datos_factura['metodo_pago']}</font><br/>
    <font size="9">Estado: Pagado</font><br/>
    """
    col_pago = Paragraph(texto_pago, estilo_texto)

    tabla_datos = Table([[col_cliente, col_pago]], colWidths=[3.75*inch, 3.75*inch])
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), GRIS_FONDO),
        ('BACKGROUND', (1,0), (1,0), GRIS_FONDO),
        ('LINEBEFORE', (0,0), (0,0), 3, AZUL_BARRA), # Línea azul izquierda
        ('LINEBEFORE', (1,0), (1,0), 3, AZUL_BARRA), # Línea azul izquierda
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(tabla_datos)
    elements.append(Spacer(1, 20))

    # --- 3. TABLA DE ITEMS ---
    elements.append(Paragraph("DETALLE DE LA FACTURA", estilo_seccion))
    
    # Encabezados de la tabla
    data_items = [["Cant.", "Descripción", "V. Unitario", "Total"]]
    
    for item in items:
        data_items.append([
            str(item['cantidad']), 
            item['descripcion'], 
            f"${item['precio_unitario']:,.2f}", 
            f"${item['total']:,.2f}"
        ])
    
    # Agregar filas de totales
    data_items.append(["", "", "Subtotal:", f"${totales['subtotal']:,.2f}"])
    data_items.append(["", "", "IVA (19%):", f"${totales['iva']:,.2f}"])
    data_items.append(["", "", "TOTAL:", f"${totales['total']:,.2f}"])

    tabla_items = Table(data_items, colWidths=[0.6*inch, 4.0*inch, 1.4*inch, 1.5*inch])
    tabla_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), AZUL_CORPORATIVO),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-4), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LINEBELOW', (0,0), (-1,-4), 0.5, colors.grey), # Líneas entre items
        ('LINEABOVE', (0,-3), (-1,-3), 1, AZUL_CORPORATIVO), # Línea antes de totales
        ('FONTNAME', (2,-3), (2,-1), 'Helvetica-Bold'), # Bold en subtotales
        ('FONTNAME', (2,-1), (-1,-1), 'Helvetica-Bold'), # Bold en TOTAL
        ('FONTSIZE', (2,-1), (-1,-1), 11),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(tabla_items)
    elements.append(Spacer(1, 40))

    # --- 4. FIRMAS (Simulando el pie de página de tu imagen) ---
    linea_firma = "_" * 35
    texto_firmas = f"""
    <br/><br/>
    {linea_firma} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {linea_firma}<br/>
    <b>Técnico / Emisor</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Firma del Cliente</b><br/>
    {datos_empresa['nombre']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; C.C. {datos_cliente['cedula']}
    """
    elements.append(Paragraph(texto_firmas, estilo_texto))

    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFAZ DE STREAMLIT
# ==========================================
st.title("📄 Generador de Facturas - Aircraft Multiservicios")

# 1. Datos de la empresa (Fijos)
datos_empresa = {
    "nombre": "AIRCRAFT MULTISERVICIOS",
    "descripcion": "SISTEMAS DE CLIMATIZACIÓN Y REFRIGERACIÓN",
    "nit": "1087200869",
    "telefono": "+57 302 681 2764",
    "correo": "aircraftmultiservicios30@gmail.com"
}

# 2. Formulario de Datos Básicos
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos del Cliente")
        cliente_nombre = st.text_input("Nombre del Cliente", "Fernando Mendez")
        cliente_cedula = st.text_input("NIT / Cédula", "1087202958")
        cliente_telefono = st.text_input("Teléfono", "3186919844")
        cliente_direccion = st.text_input("Dirección", "Cl. 14 #6a-74 a 6a-118")
    with col2:
        st.subheader("Datos de la Factura")
        factura_numero = st.text_input("Número de Factura", "#F-001")
        factura_fecha = st.date_input("Fecha", datetime.now())
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Transferencia", "Tarjeta"])

# 3. Manejador de Ítems dinámico
st.subheader("Ítems de la Factura")
if "items" not in st.session_state:
    st.session_state.items = [{"cantidad": 1, "descripcion": "Mantenimiento preventivo aire acondicionado", "precio_unitario": 150000.0}]

# Función para agregar/eliminar filas
def agregar_item():
    st.session_state.items.append({"cantidad": 1, "descripcion": "", "precio_unitario": 0.0})
def eliminar_item(index):
    st.session_state.items.pop(index)

# Mostrar los ítems en pantalla
for i, item in enumerate(st.session_state.items):
    c1, c2, c3, c4 = st.columns([1, 4, 2, 1])
    item['cantidad'] = c1.number_input("Cant.", min_value=1, value=item['cantidad'], key=f"qty_{i}")
    item['descripcion'] = c2.text_input("Descripción", value=item['descripcion'], key=f"desc_{i}")
    item['precio_unitario'] = c3.number_input("V. Unitario", min_value=0.0, value=item['precio_unitario'], step=1000.0, key=f"price_{i}")
    item['total'] = item['cantidad'] * item['precio_unitario']
    c4.write(" ")
    c4.write(" ")
    if c4.button("❌", key=f"del_{i}"):
        eliminar_item(i)
        st.rerun()

col_btn1, col_btn2 = st.columns([1, 5])
col_btn1.button("➕ Agregar Ítem", on_click=agregar_item)

# Cálculos de totales
subtotal = sum(item['total'] for item in st.session_state.items)
iva = subtotal * 0.19 # 19% IVA Colombia
total = subtotal + iva

st.markdown(f"### Subtotal: ${subtotal:,.2f} | IVA (19%): ${iva:,.2f} | **Total: ${total:,.2f}**")

# 4. Generar PDF
if st.button("📥 Generar y Descargar PDF", type="primary"):
    datos_cliente = {
        "nombre": cliente_nombre,
        "cedula": cliente_cedula,
        "telefono": cliente_telefono,
        "direccion": cliente_direccion
    }
    datos_factura = {
        "numero": factura_numero,
        "fecha": factura_fecha.strftime("%d de %B, %Y"),
        "metodo_pago": metodo_pago
    }
    totales = {
        "subtotal": subtotal,
        "iva": iva,
        "total": total
    }
    
    pdf_buffer = generar_pdf(datos_empresa, datos_factura, datos_cliente, st.session_state.items, totales)
    
    st.download_button(
        label="⬇️ Descargar Factura en PDF",
        data=pdf_buffer,
        file_name=f"Factura_{factura_numero.replace('#', '')}.pdf",
        mime="application/pdf"
    )
    st.success("¡PDF generado con éxito! Haz clic en el botón de arriba para descargar.")
