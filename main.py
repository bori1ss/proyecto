"""
main.py
Punto de entrada del Sistema de Gestión Académica.

La clase AppHorarioAvanzada combina tres módulos completamente
independientes mediante herencia múltiple (mixins):
    - AuthMixin         -> auth_screen.py      (login / registro)
    - DocenteMixin       -> docente_screen.py   (solo lógica del docente)
    - EstudianteMixin    -> estudiante_screen.py (solo lógica del estudiante)

Cada mixin no conoce los detalles internos de los otros: comparten
únicamente el estado de sesión (self.usuario_id_actual, self.cursor, etc.)
definido aquí, en __init__.
"""
import customtkinter as ctk

from database import conectar_db
from auth_screen import AuthMixin
from docente_screen import DocenteMixin
from estudiante_screen import EstudianteMixin

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppHorarioAvanzada(ctk.CTk, AuthMixin, DocenteMixin, EstudianteMixin):
    def __init__(self):
        super().__init__()
        self.title("UNIFRANZ - Sistema de Gestión Académica")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.conn, self.cursor = conectar_db()

        # --- Estado de sesión, compartido entre los tres módulos ---
        self.usuario_id_actual = None
        self.usuario_nombre_actual = None
        self.rol_actual = None

        # --- Estado exclusivo del flujo Docente (selección de materia) ---
        self.materia_seleccionada_id = None

        # --- Estado de edición de actividad: usado tanto por Docente como
        #     por Estudiante para saber si el formulario está editando una
        #     actividad existente o creando una nueva. Cada flujo gestiona
        #     sus propias actividades (tablas separadas), nunca se mezclan. ---
        self.actividad_en_edicion = None

        # --- Estado de orden/búsqueda, compartido por ambas listas ---
        self.orden_actual = "fecha"
        self.orden_ascendente = True
        self.texto_busqueda = ""

        self.contenedor = ctk.CTkFrame(self)
        self.contenedor.pack(fill="both", expand=True, padx=15, pady=15)

        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        self.mostrar_pantalla_autenticacion()

    def al_cerrar(self):
        self.conn.close()
        self.destroy()

    def limpiar_pantalla(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = AppHorarioAvanzada()
    app.mainloop()
