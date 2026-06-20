"""
docente_screen.py
Pantalla y lógica EXCLUSIVA del rol Docente:
- Crear y seleccionar sus propias materias.
- Publicar, editar y eliminar actividades dentro de la materia activa.

Implementado como Mixin (DocenteMixin), separado por completo del
flujo del Estudiante (ver estudiante_screen.py).
"""
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from database import COLORES_TIPO
from widgets import crear_tarjeta_actividad, armar_panel_filtros, campo_orden_sql


class DocenteMixin:
    # =====================================================================
    # PANTALLA PRINCIPAL DEL DOCENTE
    # =====================================================================
    def mostrar_dashboard_docente(self):
        self.limpiar_pantalla()
        self.encabezado(self.contenedor)

        frame_izq_contenedor = ctk.CTkFrame(self.contenedor, width=340)
        frame_izq_contenedor.pack(side="left", fill="y", padx=5, pady=5)
        # Todo el panel izquierdo va dentro de un frame con scroll propio:
        # así, si la ventana es pequeña o el formulario crece, el botón
        # "Publicar Actividad" siempre queda accesible deslizando, en vez
        # de quedar empujado fuera del área visible.
        frame_izq = ctk.CTkScrollableFrame(frame_izq_contenedor, width=320, fg_color="transparent")
        frame_izq.pack(fill="both", expand=True)

        frame_der = ctk.CTkFrame(self.contenedor)
        frame_der.pack(side="right", fill="both", padx=5, pady=5, expand=True)

        # --- Gestión de materias propias ---
        ctk.CTkLabel(frame_izq, text="Mis Materias", font=("Arial", 18, "bold")).pack(pady=10)

        frame_nueva_materia = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_nueva_materia.pack(pady=5)
        self.ent_nueva_materia = ctk.CTkEntry(frame_nueva_materia, placeholder_text="Nombre de nueva materia", width=200)
        self.ent_nueva_materia.pack(side="left", padx=3)
        ctk.CTkButton(frame_nueva_materia, text="+", width=35, command=self.crear_materia).pack(side="left")

        self.lista_materias_frame = ctk.CTkScrollableFrame(frame_izq, height=150, label_text="Selecciona una materia")
        self.lista_materias_frame.pack(fill="x", pady=8, padx=10)
        self.cargar_materias_docente()

        # --- Formulario de actividad ---
        ctk.CTkLabel(frame_izq, text="Añadir Actividad", font=("Arial", 16, "bold")).pack(pady=(15, 5))

        self.lbl_materia_activa = ctk.CTkLabel(frame_izq, text="⚠️ Selecciona una materia arriba", text_color="#E67E22")
        self.lbl_materia_activa.pack(pady=2)

        ctk.CTkLabel(frame_izq, text="Tipo de Tarea:").pack(anchor="w", padx=25)
        self.ent_tipo = ctk.CTkComboBox(frame_izq, values=list(COLORES_TIPO.keys()), state="readonly", width=280)
        self.ent_tipo.set("Tarea")
        self.ent_tipo.pack(pady=5)

        ctk.CTkLabel(frame_izq, text="Fecha de Entrega:").pack(anchor="w", padx=25)
        frame_fecha = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_fecha.pack(pady=5)

        anio_actual = datetime.now().year
        dias = [str(i).zfill(2) for i in range(1, 32)]
        meses = [str(i).zfill(2) for i in range(1, 13)]
        anios = [str(i) for i in range(anio_actual, anio_actual + 6)]

        self.combo_dia = ctk.CTkComboBox(frame_fecha, values=dias, width=75, state="readonly")
        self.combo_dia.set(datetime.now().strftime("%d"))
        self.combo_dia.pack(side="left", padx=2)
        self.combo_mes = ctk.CTkComboBox(frame_fecha, values=meses, width=75, state="readonly")
        self.combo_mes.set(datetime.now().strftime("%m"))
        self.combo_mes.pack(side="left", padx=2)
        self.combo_anio = ctk.CTkComboBox(frame_fecha, values=anios, width=90, state="readonly")
        self.combo_anio.set(str(anio_actual))
        self.combo_anio.pack(side="left", padx=2)

        ctk.CTkLabel(frame_izq, text="Descripción de la actividad:").pack(anchor="w", padx=25)
        self.txt_desc = ctk.CTkTextbox(frame_izq, width=280, height=110)
        self.txt_desc.pack(pady=5)

        frame_botones_form = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_botones_form.pack(pady=10)
        self.btn_guardar = ctk.CTkButton(frame_botones_form, text="Publicar Actividad", fg_color="#2980B9",
                                          hover_color="#2471A3", command=self.guardar_actividad, width=180)
        self.btn_guardar.pack(side="left", padx=3)
        self.btn_cancelar_edicion = ctk.CTkButton(frame_botones_form, text="Cancelar", fg_color="#95A5A6",
                                                   hover_color="#7F8C8D", width=90,
                                                   command=self.cancelar_edicion)
        # se muestra solo durante edición (ver editar_actividad / cancelar_edicion)

        # --- Panel derecho: filtros + lista ---
        armar_panel_filtros(frame_der, self, self.actualizar_lista_docente)
        self.scroll_actividades = ctk.CTkScrollableFrame(frame_der, label_text="Cronograma de Actividades")
        self.scroll_actividades.pack(fill="both", expand=True, padx=10, pady=10)

        self.actualizar_lista_docente()

    # =====================================================================
    # GESTIÓN DE MATERIAS (solo docente)
    # =====================================================================
    def cargar_materias_docente(self):
        for w in self.lista_materias_frame.winfo_children():
            w.destroy()

        self.cursor.execute(
            "SELECT id, nombre FROM materias WHERE docente_id = ? ORDER BY nombre ASC",
            (self.usuario_id_actual,)
        )
        materias = self.cursor.fetchall()

        if not materias:
            ctk.CTkLabel(self.lista_materias_frame, text="Aún no tienes materias creadas.",
                         font=("Arial", 11, "italic")).pack(pady=10)
            return

        for materia_id, nombre in materias:
            seleccionada = (materia_id == self.materia_seleccionada_id)
            color = "#2980B9" if seleccionada else "#34495E"
            ctk.CTkButton(
                self.lista_materias_frame, text=nombre, fg_color=color, hover_color="#21618C",
                anchor="w", command=lambda m=materia_id, n=nombre: self.seleccionar_materia(m, n)
            ).pack(fill="x", pady=2, padx=4)

    def crear_materia(self):
        nombre = self.ent_nueva_materia.get().strip().title()
        if not nombre:
            messagebox.showwarning("Campo vacío", "Escribe el nombre de la materia.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO materias (nombre, docente_id) VALUES (?, ?)",
                (nombre, self.usuario_id_actual)
            )
            self.conn.commit()
            self.ent_nueva_materia.delete(0, "end")
            self.cargar_materias_docente()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya tienes una materia con ese nombre.")

    def seleccionar_materia(self, materia_id, nombre):
        self.materia_seleccionada_id = materia_id
        self.cancelar_edicion()
        self.lbl_materia_activa.configure(text=f"📚 Materia activa: {nombre}", text_color="#2ECC71")
        self.cargar_materias_docente()
        self.actualizar_lista_docente()

    # =====================================================================
    # GESTIÓN DE ACTIVIDADES (solo docente: crear / editar / eliminar)
    # =====================================================================
    def cancelar_edicion(self):
        self.actividad_en_edicion = None
        self.txt_desc.delete("1.0", "end")
        self.ent_tipo.set("Tarea")
        self.btn_guardar.configure(text="Publicar Actividad")
        self.btn_cancelar_edicion.pack_forget()

    def guardar_actividad(self):
        if not self.materia_seleccionada_id:
            messagebox.showwarning("Materia requerida", "Selecciona o crea una materia primero.")
            return

        tipo = self.ent_tipo.get()
        desc = self.txt_desc.get("1.0", "end-1c").strip()
        fecha_str = f"{self.combo_anio.get()}-{self.combo_mes.get()}-{self.combo_dia.get()}"

        if not desc:
            messagebox.showwarning("Campo vacío", "Escribe la descripción de la actividad.")
            return
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida", "La combinación de fecha seleccionada no existe.")
            return

        if self.actividad_en_edicion:
            self.cursor.execute(
                "UPDATE actividades SET tipo = ?, fecha = ?, descripcion = ? WHERE id = ?",
                (tipo, fecha_str, desc, self.actividad_en_edicion)
            )
        else:
            self.cursor.execute(
                "INSERT INTO actividades (materia_id, tipo, fecha, descripcion) VALUES (?, ?, ?, ?)",
                (self.materia_seleccionada_id, tipo, fecha_str, desc)
            )
        self.conn.commit()
        self.cancelar_edicion()
        self.actualizar_lista_docente()

    def editar_actividad(self, id_act, tipo, fecha, descripcion):
        self.actividad_en_edicion = id_act
        self.ent_tipo.set(tipo)
        try:
            anio, mes, dia = fecha.split("-")
            self.combo_anio.set(anio)
            self.combo_mes.set(mes)
            self.combo_dia.set(dia)
        except ValueError:
            pass
        self.txt_desc.delete("1.0", "end")
        self.txt_desc.insert("1.0", descripcion)
        self.btn_guardar.configure(text="Guardar Cambios")
        self.btn_cancelar_edicion.pack(side="left", padx=3)

    def eliminar_actividad(self, id_act):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta actividad por completo? "
                                             "Esto también borra las entregas asociadas."):
            self.cursor.execute("DELETE FROM entregas WHERE actividad_id = ?", (id_act,))
            self.cursor.execute("DELETE FROM actividades WHERE id = ?", (id_act,))
            self.conn.commit()
            self.actualizar_lista_docente()

    # =====================================================================
    # RENDERIZADO DE LA LISTA (vista docente)
    # =====================================================================
    def actualizar_lista_docente(self):
        for w in self.scroll_actividades.winfo_children():
            w.destroy()

        query = f"""
            SELECT a.id, m.nombre AS nombre_materia, a.tipo, a.fecha, a.descripcion
            FROM actividades a JOIN materias m ON a.materia_id = m.id
            WHERE m.docente_id = ?
            AND (LOWER(a.descripcion) LIKE ? OR LOWER(m.nombre) LIKE ?)
            ORDER BY {campo_orden_sql(self)}
        """
        patron = f"%{self.texto_busqueda}%"
        self.cursor.execute(query, (self.usuario_id_actual, patron, patron))
        filas = self.cursor.fetchall()

        if not filas:
            ctk.CTkLabel(self.scroll_actividades, text="No hay actividades que coincidan.",
                         font=("Arial", 13, "italic")).pack(pady=20)
            return

        for id_act, materia, tipo, fecha, descripcion in filas:
            crear_tarjeta_actividad(
                self.scroll_actividades, materia=materia, tipo=tipo, fecha=fecha,
                descripcion=descripcion, estado=None,
                construir_botones=lambda parent, i=id_act, t=tipo, f=fecha, d=descripcion: [
                    ctk.CTkButton(parent, text="✏️ Editar", width=100, height=28,
                                  fg_color="#F39C12", hover_color="#D68910",
                                  command=lambda: self.editar_actividad(i, t, f, d)).pack(pady=3),
                    ctk.CTkButton(parent, text="❌ Eliminar", width=100, height=28,
                                  fg_color="#D9534F", hover_color="#C9302C",
                                  command=lambda: self.eliminar_actividad(i)).pack(pady=3),
                ]
            )
