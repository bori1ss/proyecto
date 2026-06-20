"""
widgets.py
Componentes visuales reutilizables entre la pantalla de Docente
y la pantalla de Estudiante (tarjeta de actividad, panel de filtros).
"""
import customtkinter as ctk
from database import COLORES_TIPO, COLOR_ENTREGADO, COLOR_PENDIENTE


def crear_tarjeta_actividad(contenedor, materia, tipo, fecha, descripcion, estado, construir_botones):
    """Crea y empaqueta una tarjeta visual para una actividad.

    `estado` puede ser None (vista docente, sin estado de entrega) o
    "Pendiente"/"Entregado" (vista estudiante).
    `construir_botones(frame_acciones)` recibe el frame donde debe
    empaquetar los botones de acción específicos de cada rol.
    """
    color_borde = COLORES_TIPO.get(tipo, "#3498DB")

    tarjeta = ctk.CTkFrame(contenedor, border_width=2, border_color=color_borde)
    tarjeta.pack(fill="x", pady=6, padx=5)

    frame_info = ctk.CTkFrame(tarjeta, fg_color="transparent")
    frame_info.pack(side="left", padx=15, pady=10, fill="x", expand=True)

    cabecera = ctk.CTkFrame(frame_info, fg_color="transparent")
    cabecera.pack(fill="x")
    ctk.CTkLabel(cabecera, text=f"📌 {materia.upper()}", font=("Arial", 13, "bold")).pack(side="left")
    ctk.CTkLabel(cabecera, text=tipo.upper(), font=("Arial", 11, "bold"),
                 text_color=color_borde).pack(side="left", padx=10)

    if estado is not None:
        color_badge = COLOR_ENTREGADO if estado == "Entregado" else COLOR_PENDIENTE
        ctk.CTkLabel(cabecera, text=estado, fg_color=color_badge, corner_radius=6,
                     width=80, font=("Arial", 10, "bold")).pack(side="right", padx=4)

    ctk.CTkLabel(frame_info, text=f"📅 Entrega: {fecha}", font=("Arial", 11)).pack(anchor="w", pady=(4, 0))
    ctk.CTkLabel(frame_info, text=descripcion, justify="left", anchor="w",
                 font=("Arial", 12), wraplength=420).pack(anchor="w", pady=(4, 0))

    frame_acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
    frame_acciones.pack(side="right", padx=10, pady=5)
    construir_botones(frame_acciones)


def armar_panel_filtros(padre, app, callback_actualizar):
    """Crea la barra de 'Ordenar por' + búsqueda, ligada al estado de orden de `app`.

    `app` debe exponer: orden_actual, orden_ascendente, texto_busqueda.
    `callback_actualizar` es la función que vuelve a pintar la lista
    (propia de cada pantalla: docente o estudiante).
    """
    frame_filtros = ctk.CTkFrame(padre)
    frame_filtros.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(frame_filtros, text="Ordenar por:", font=("Arial", 12, "bold")).pack(side="left", padx=10)

    def set_orden(campo):
        if app.orden_actual == campo:
            app.orden_ascendente = not app.orden_ascendente
        else:
            app.orden_actual = campo
            app.orden_ascendente = True
        callback_actualizar()

    ctk.CTkButton(frame_filtros, text="Fecha", width=90, fg_color="#34495E",
                  hover_color="#2C3E50", command=lambda: set_orden("fecha")).pack(side="left", padx=3)
    ctk.CTkButton(frame_filtros, text="Materia", width=90, fg_color="#34495E",
                  hover_color="#2C3E50", command=lambda: set_orden("materia")).pack(side="left", padx=3)
    ctk.CTkButton(frame_filtros, text="Tipo", width=90, fg_color="#34495E",
                  hover_color="#2C3E50", command=lambda: set_orden("tipo")).pack(side="left", padx=3)

    ent_busqueda = ctk.CTkEntry(frame_filtros, placeholder_text="Buscar por descripción o materia...", width=240)
    ent_busqueda.pack(side="right", padx=10)

    def on_buscar(event=None):
        app.texto_busqueda = ent_busqueda.get().strip().lower()
        callback_actualizar()

    ent_busqueda.bind("<KeyRelease>", on_buscar)


def campo_orden_sql(app):
    """Traduce el estado de orden de `app` a una cláusula SQL ORDER BY."""
    mapa = {"fecha": "fecha", "materia": "LOWER(nombre_materia)", "tipo": "tipo"}
    campo = mapa.get(app.orden_actual, "fecha")
    direccion = "ASC" if app.orden_ascendente else "DESC"
    return f"{campo} {direccion}"
