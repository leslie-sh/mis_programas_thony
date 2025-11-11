import flet as ft
import sqlite3
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Definición de colores hex para usar en lugar de ft.colors
RED = "#ef5350"
RED_400 = "#ef5350"
GREEN = "#66bb6a"
GREEN_400 = "#66bb6a"
BLUE_GREY_100 = "#cfd8dc"
BLUE = "#2196f3"
ORANGE = "#fb8c00"

# --- Funciones base de datos ya definidas antes ---
def crear_base_datos():
    conn = sqlite3.connect("faznet.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            contraseña TEXT,
            correo TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            especialidad TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            tecnico TEXT NOT NULL,
            tipo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            observaciones TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Abierto',
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- Vista principal (dashboard) con botones para abrir cada módulo ---
def vista_principal(page: ft.Page):
    page.title = "FAST-NET - Panel Principal"
    page.views.clear()

    def abrir_gestion_clientes(e):
        page.go("/clientes")

    def abrir_gestion_tecnicos(e):
        page.go("/tecnicos")

    def abrir_registro_servicio(e):
        page.go("/registro_servicio")

    def abrir_ver_servicios(e):
        page.go("/ver_servicios")

    def abrir_soporte_tickets(e):
        page.go("/tickets")

    def abrir_reportes(e):
        page.go("/reportes")

    def cerrar_sesion(e):
        page.client_storage.remove("usuario")
        page.go("/")

    column = ft.Column([
        ft.Text(f"Bienvenido, {page.client_storage.get('usuario')}", size=20, weight="bold"),
        ft.ElevatedButton("Gestión de Clientes", on_click=abrir_gestion_clientes),
        ft.ElevatedButton("Gestión de Técnicos", on_click=abrir_gestion_tecnicos),
        ft.ElevatedButton("Registrar Servicio", on_click=abrir_registro_servicio),
        ft.ElevatedButton("Ver Servicios", on_click=abrir_ver_servicios),
        ft.ElevatedButton("Soporte Técnico (Tickets)", on_click=abrir_soporte_tickets),
        ft.ElevatedButton("Generar Reportes", on_click=abrir_reportes),
        ft.ElevatedButton("📘 Ver Tutorial", on_click=lambda e: page.go("/tutorial")),
        ft.ElevatedButton("Cerrar Sesión", on_click=cerrar_sesion, bgcolor=RED_400)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    page.views.append(ft.View("/main", [ft.Container(content=column, alignment=ft.alignment.center)]))
    page.update()

# --- Gestión Clientes ---
def gestion_clientes(page: ft.Page):
    page.title = "Gestión de Clientes"
    page.views.clear()

    nombre = ft.TextField(label="Nombre del Cliente", width=300)
    correo = ft.TextField(label="Correo Electrónico", width=300)
    telefono = ft.TextField(label="Teléfono", width=300)

    lista_clientes = ft.ListView(expand=True, spacing=5, padding=10)

    def cargar_clientes():
        lista_clientes.controls.clear()
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, correo, telefono FROM clientes")
        for id_, nom, cor, tel in cursor.fetchall():
            lista_clientes.controls.append(
                ft.Text(f"{nom} | {cor} | {tel}")
            )
        conn.close()
        page.update()

    def guardar_cliente(e):
        if not nombre.value or not correo.value or not telefono.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (?, ?, ?)", (nombre.value, correo.value, telefono.value))
        conn.commit()
        conn.close()
        nombre.value = ""
        correo.value = ""
        telefono.value = ""
        page.snack_bar = ft.SnackBar(ft.Text("Cliente registrado"), bgcolor=GREEN)
        page.snack_bar.open = True
        cargar_clientes()

    btn_guardar = ft.ElevatedButton("Agregar Cliente", on_click=guardar_cliente)
    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        nombre, correo, telefono, btn_guardar, lista_clientes, btn_volver
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.append(ft.View("/clientes", [ft.Container(content=column, alignment=ft.alignment.center, padding=20, expand=True)]))
    cargar_clientes()
    page.update()

# --- Gestión Técnicos ---
def gestion_tecnicos(page: ft.Page):
    page.title = "Gestión de Técnicos"
    page.views.clear()

    nombre = ft.TextField(label="Nombre del Técnico", width=300)
    especialidad = ft.TextField(label="Especialidad", width=300)

    lista_tecnicos = ft.ListView(expand=True, spacing=5, padding=10)

    def cargar_tecnicos():
        lista_tecnicos.controls.clear()
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, especialidad FROM tecnicos")
        for id_, nom, esp in cursor.fetchall():
            lista_tecnicos.controls.append(ft.Text(f"{nom} | {esp}"))
        conn.close()
        page.update()

    def guardar_tecnico(e):
        if not nombre.value or not especialidad.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tecnicos (nombre, especialidad) VALUES (?, ?)", (nombre.value, especialidad.value))
        conn.commit()
        conn.close()
        nombre.value = ""
        especialidad.value = ""
        page.snack_bar = ft.SnackBar(ft.Text("Técnico registrado"), bgcolor=GREEN)
        page.snack_bar.open = True
        cargar_tecnicos()

    btn_guardar = ft.ElevatedButton("Agregar Técnico", on_click=guardar_tecnico)
    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        nombre, especialidad, btn_guardar, lista_tecnicos, btn_volver
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.append(ft.View("/tecnicos", [ft.Container(content=column, alignment=ft.alignment.center, padding=20, expand=True)]))
    cargar_tecnicos()
    page.update()

# --- Registro de Servicio ---
def registro_servicio(page: ft.Page):
    page.title = "Registrar Servicio"
    page.views.clear()

    conn = sqlite3.connect("faznet.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM clientes")
    clientes = [fila[0] for fila in cursor.fetchall()]
    cursor.execute("SELECT nombre FROM tecnicos")
    tecnicos = [fila[0] for fila in cursor.fetchall()]
    conn.close()

    combo_cliente = ft.Dropdown(label="Cliente", options=[ft.dropdown.Option(c) for c in clientes], width=300)
    combo_tecnico = ft.Dropdown(label="Técnico", options=[ft.dropdown.Option(t) for t in tecnicos], width=300)

    tipos_servicio = [
        "Soporte Técnico", "Redes y Conectividad", "Servicios en la Nube",
        "Seguridad Informática", "Venta de Equipos", "Consultoría", "Mantenimiento", "Desarrollo de Software"
    ]
    combo_tipo = ft.Dropdown(label="Tipo de Servicio", options=[ft.dropdown.Option(t) for t in tipos_servicio], width=300)

    fecha = ft.TextField(label="Fecha (YYYY-MM-DD)", value=str(date.today()), width=300)
    observaciones = ft.TextField(label="Observaciones", multiline=True, width=300, height=80)

    def guardar(e):
        if not combo_cliente.value or not combo_tecnico.value or not combo_tipo.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos obligatorios"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO servicios (cliente, tecnico, tipo, fecha, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (combo_cliente.value, combo_tecnico.value, combo_tipo.value, fecha.value, observaciones.value))
        conn.commit()
        conn.close()
        page.snack_bar = ft.SnackBar(ft.Text("Servicio registrado"), bgcolor=GREEN)
        page.snack_bar.open = True
        page.go("/main")

    btn_guardar = ft.ElevatedButton("Guardar Servicio", on_click=guardar)
    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        combo_cliente, combo_tecnico, combo_tipo, fecha, observaciones,
        btn_guardar, btn_volver
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.append(ft.View("/registro_servicio", [ft.Container(content=column, alignment=ft.alignment.center, padding=20, expand=True)]))
    page.update()

# --- Ver Servicios ---
def ver_servicios(page: ft.Page):
    page.title = "Historial de Servicios"
    page.views.clear()

    lista_servicios = ft.ListView(expand=True, spacing=5, padding=10)

    def cargar_servicios():
        lista_servicios.controls.clear()
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cliente, tecnico, tipo, fecha, observaciones FROM servicios ORDER BY id DESC")
        for cliente, tecnico, tipo, fecha, obs in cursor.fetchall():
            texto = f"{fecha} | {cliente} | {tecnico} | {tipo} | {obs}"
            lista_servicios.controls.append(ft.Text(texto, selectable=True))
        conn.close()
        page.update()

    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        lista_servicios,
        btn_volver
    ], expand=True)

    page.views.append(ft.View("/ver_servicios", [ft.Container(content=column, padding=20, expand=True)]))
    cargar_servicios()
    page.update()

# --- Soporte Técnico (Tickets) ---
def soporte_tickets(page: ft.Page):
    page.title = "Soporte Técnico - Tickets"
    page.views.clear()

    cliente = ft.TextField(label="Cliente", width=300)
    descripcion = ft.TextField(label="Descripción del problema", multiline=True, width=300, height=80)
    lista_tickets = ft.ListView(expand=True, spacing=5, padding=10)

    def cargar_tickets():
        lista_tickets.controls.clear()
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente, descripcion, estado, fecha FROM tickets ORDER BY id DESC")
        for id_, cli, desc, estado, fecha in cursor.fetchall():
            estado_icono = "✅" if estado == "Cerrado" else "🟡"
            texto = f"#{id_} {estado_icono} {cli} | {desc[:30]}... | {fecha}"
            lista_tickets.controls.append(ft.Text(texto, selectable=True))
        conn.close()
        page.update()

    def guardar_ticket(e):
        if not cliente.value or not descripcion.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO tickets (cliente, descripcion, estado, fecha) VALUES (?, ?, 'Abierto', ?)", (cliente.value, descripcion.value, ahora))
        conn.commit()
        conn.close()
        cliente.value = ""
        descripcion.value = ""
        page.snack_bar = ft.SnackBar(ft.Text("Ticket registrado"), bgcolor=GREEN)
        page.snack_bar.open = True
        cargar_tickets()

    def cerrar_ticket(e):
        seleccion = lista_tickets.selected_index
        if seleccion is None or seleccion < 0 or seleccion >= len(lista_tickets.controls):
            page.snack_bar = ft.SnackBar(ft.Text("Selecciona un ticket"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        texto = lista_tickets.controls[seleccion].text
        ticket_id = int(texto.split(" ")[0][1:])
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET estado='Cerrado' WHERE id=?", (ticket_id,))
        conn.commit()
        conn.close()
        page.snack_bar = ft.SnackBar(ft.Text("Ticket cerrado"), bgcolor=GREEN)
        page.snack_bar.open = True
        cargar_tickets()

    btn_guardar = ft.ElevatedButton("Registrar Ticket", on_click=guardar_ticket)
    btn_cerrar = ft.ElevatedButton("Cerrar Ticket Seleccionado", on_click=cerrar_ticket)
    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        cliente, descripcion, btn_guardar, btn_cerrar, lista_tickets, btn_volver
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.append(ft.View("/tickets", [ft.Container(content=column, alignment=ft.alignment.center, padding=20, expand=True)]))
    cargar_tickets()
    page.update()

def ver_tutorial(page: ft.Page):
    page.title = "Tutorial de Uso - FAST-NET"
    page.views.clear()

    pasos = [
        "1. Inicia sesión con tu usuario y contraseña.",
        "2. Si no tienes cuenta, regístrate usando 'Registrar nuevo usuario'.",
        "3. En el menú principal puedes:",
        "- ➕ Agregar clientes y técnicos.",
        "- 🛠️ Registrar un servicio técnico indicando cliente, técnico y fecha.",
        "- 📋 Ver el historial de servicios realizados.",
        "- 🧾 Gestionar tickets de soporte técnico y cerrarlos cuando se resuelvan.",
        "- 🖨️ Generar reportes PDF de clientes registrados.",
        "- 🔐 Recuperar contraseña si la olvidaste desde el login.",
        "4. Usa el botón 'Cerrar sesión' para salir del sistema.",
        "Gracias por usar FAST-NET."
    ]

    contenido = ft.Column(
        [ft.Text("📘 Tutorial de Uso", size=24, weight="bold")] +
        [ft.Text(p) for p in pasos] +
        [ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.views.append(
        ft.View("/tutorial", [
            ft.Container(content=contenido, alignment=ft.alignment.center, padding=30)
        ])
    )
    page.update()


# --- Reportes (Clientes) ---
def generar_reportes(page: ft.Page):
    page.title = "Generar Reportes"
    page.views.clear()

    def generar_pdf(e):
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, correo, telefono FROM clientes")
        clientes = cursor.fetchall()
        conn.close()

        if not clientes:
            page.snack_bar = ft.SnackBar(ft.Text("No hay clientes para generar reporte"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return

        archivo_pdf = "reporte_clientes.pdf"
        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 750, "Reporte de Clientes - FAST-NET")

        y = 720
        c.setFont("Helvetica", 12)
        for cliente in clientes:
            texto = f"Nombre: {cliente[0]} | Correo: {cliente[1]} | Teléfono: {cliente[2]}"
            c.drawString(40, y, texto)
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
                c.setFont("Helvetica", 12)

        c.save()
        page.snack_bar = ft.SnackBar(ft.Text(f"Reporte guardado en {os.path.abspath(archivo_pdf)}"), bgcolor=GREEN)
        page.snack_bar.open = True
        page.update()

    btn_generar = ft.ElevatedButton("Generar Reporte PDF", on_click=generar_pdf)
    btn_volver = ft.TextButton("Volver al menú", on_click=lambda e: page.go("/main"))

    column = ft.Column([
        ft.Text("Generar reporte de todos los clientes registrados"),
        btn_generar,
        btn_volver
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.append(ft.View("/reportes", [ft.Container(content=column, alignment=ft.alignment.center, padding=20)]))
    page.update()

# --- Función principal que controla rutas ---
def app_main(page: ft.Page):
    crear_base_datos()
    route = page.route

    if route == "/":
        # Login
        login_view(page)
    elif route == "/main":
        vista_principal(page)
    elif route == "/clientes":
        gestion_clientes(page)
    elif route == "/tecnicos":
        gestion_tecnicos(page)
    elif route == "/registro_servicio":
        registro_servicio(page)
    elif route == "/ver_servicios":
        ver_servicios(page)
    elif route == "/tickets":
        soporte_tickets(page)
    elif route == "/reportes":
        generar_reportes(page)
    elif route == "/registro":
        registro_view(page)
    elif route == "/tutorial":
        ver_tutorial(page)

    elif route == "/recuperar":
        recuperar_view(page)
    else:
        page.go("/")

# --- Login, Registro y Recuperar vistas ---
def login_view(page: ft.Page):
    page.title = "FAST-NET Login"
    page.bgcolor = BLUE_GREY_100
    page.window_width = 500
    page.window_height = 500

    usuario = ft.TextField(label="Usuario", autofocus=True)
    contraseña = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

    def verificar_login(e):
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contraseña = ?", (usuario.value, contraseña.value))
        if cursor.fetchone():
            page.client_storage.set("usuario", usuario.value)
            page.go("/main")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Credenciales incorrectas"), bgcolor=RED_400)
            page.snack_bar.open = True
            page.update()
        conn.close()

    def abrir_registro(e):
        page.go("/registro")

    def abrir_recuperar(e):
        page.go("/recuperar")

    login_column = ft.Column([
        ft.Text("FAST-NET", size=30, weight="bold"),
        usuario,
        contraseña,
        ft.ElevatedButton("Iniciar Sesión", on_click=verificar_login, bgcolor=GREEN_400),
        ft.TextButton("Registrar nuevo usuario", on_click=abrir_registro),
        ft.TextButton("¿Olvidaste tu contraseña?", on_click=abrir_recuperar)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.views.clear()
    page.views.append(ft.View("/", [ft.Container(content=login_column, alignment=ft.alignment.center)]))
    page.update()

def registro_view(page: ft.Page):
    page.title = "Registrar Usuario"
    page.bgcolor = BLUE_GREY_100
    page.window_width = 500
    page.window_height = 550

    usuario = ft.TextField(label="Usuario", width=300)
    correo = ft.TextField(label="Correo Electrónico", width=300)
    contraseña = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    confirmar = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, width=300)

    def registrar_usuario(e):
        if not usuario.value or not correo.value or not contraseña.value or not confirmar.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa todos los campos"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        if contraseña.value != confirmar.value:
            page.snack_bar = ft.SnackBar(ft.Text("Las contraseñas no coinciden"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return
        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? OR correo = ?", (usuario.value, correo.value))
        if cursor.fetchone():
            page.snack_bar = ft.SnackBar(ft.Text("Usuario o correo ya existe"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            conn.close()
            return
        cursor.execute("INSERT INTO usuarios (usuario, contraseña, correo) VALUES (?, ?, ?)", (usuario.value, contraseña.value, correo.value))
        conn.commit()
        conn.close()
        page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado con éxito"), bgcolor=GREEN)
        page.snack_bar.open = True
        page.go("/")

    btn_registrar = ft.ElevatedButton("Registrar", on_click=registrar_usuario, bgcolor=BLUE)
    btn_volver = ft.TextButton("Volver al login", on_click=lambda e: page.go("/"))

    column = ft.Column([usuario, correo, contraseña, confirmar, btn_registrar, btn_volver], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

    page.views.clear()
    page.views.append(ft.View("/registro", [ft.Container(content=column, alignment=ft.alignment.center)]))
    page.update()

def recuperar_view(page: ft.Page):
    page.title = "Recuperar Contraseña"
    page.bgcolor = BLUE_GREY_100
    page.window_width = 500
    page.window_height = 400

    correo = ft.TextField(label="Correo Electrónico", width=300)

    def cerrar_dialogo(e):
        page.dialog.open = False
        page.update()

    def recuperar_contraseña(e):
        if not correo.value:
            page.snack_bar = ft.SnackBar(ft.Text("Ingresa el correo electrónico"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect("faznet.db")
        cursor = conn.cursor()
        cursor.execute("SELECT contraseña FROM usuarios WHERE correo = ?", (correo.value,))
        fila = cursor.fetchone()
        conn.close()

        if fila:
            dialog = ft.AlertDialog(
                title=ft.Text("Contraseña Recuperada"),
                content=ft.Text(f"Tu contraseña es: {fila[0]}"),
                actions=[ft.TextButton("OK", on_click=cerrar_dialogo)],
                modal=True
            )
            page.dialog = dialog
            page.dialog.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Correo no encontrado"), bgcolor=RED)
            page.snack_bar.open = True
            page.update()

    btn_recuperar = ft.ElevatedButton("Recuperar", on_click=recuperar_contraseña, bgcolor=ORANGE)
    btn_volver = ft.TextButton("Volver al login", on_click=lambda e: page.go("/"))

    column = ft.Column(
        [correo, btn_recuperar, btn_volver],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    page.views.clear()
    page.views.append(ft.View("/recuperar", [ft.Container(content=column, alignment=ft.alignment.center)]))
    page.update()




# --- Cambiar rutas al cambiar page.route ---
def app_main(page: ft.Page):
    route = page.route
    if route == "/":
        login_view(page)
    elif route == "/main":
        vista_principal(page)
    elif route == "/clientes":
        gestion_clientes(page)
    elif route == "/tecnicos":
        gestion_tecnicos(page)
    elif route == "/registro_servicio":
        registro_servicio(page)
    elif route == "/ver_servicios":
        ver_servicios(page)
    elif route == "/tickets":
        soporte_tickets(page)
    elif route == "/reportes":
        generar_reportes(page)
    elif route == "/registro":
        registro_view(page)
    elif route == "/tutorial":
        ver_tutorial(page)
    elif route == "/recuperar":
        recuperar_view(page)
    else:
        page.go("/")

def main(page: ft.Page):
    page.title = "FAST-NET"
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = True
    page.bgcolor = BLUE_GREY_100

    def route_change(e):
        app_main(page)
    page.on_route_change = route_change

    app_main(page)

ft.app(target=main)
