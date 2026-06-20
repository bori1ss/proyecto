"""
estudiante_screen.py
Pantalla y lógica EXCLUSIVA del rol Estudiante:
- Crear, editar y eliminar sus propias actividades académicas,
  indicando la materia a la que pertenecen (texto libre).
- Marcar cada actividad propia como Entregada/Pendiente.
- Ordenar y buscar dentro de su propio cronograma (por fecha, tipo,
  materia o palabra clave).

El estudiante organiza sus actividades de forma completamente
individual: la "materia" aquí es solo un dato descriptivo que el
propio estudiante escribe, sin relación con las materias del módulo
de Docente (no hay inscripciones ni materias compartidas).

Implementado como Mixin (EstudianteMixin), separado por completo del
flujo del Docente (ver docente_screen.py).
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from database import COLORES_TIPO, COLOR_ENTREGADO, COLOR_PENDIENTE
from widgets import crear_tarjeta_actividad, armar_panel_filtros, campo_orden_sql


class EstudianteMixin:
    # =====================================================================
    # PANTALLA PRINCIPAL DEL ESTUDIANTE
    # =====================================================================
    def mostrar_dashboard_estudiante(self):
        self.limpiar_pantalla()
        self.encabezado(self.contenedor)

        frame_izq_contenedor = ctk.CTkFrame(self.contenedor, width=320)
        frame_izq_contenedor.pack(side="left", fill="y", padx=5, pady=5)
        # Panel izquierdo con scroll propio: evita que el botón "Añadir
        # Actividad" quede fuera del área visible en ventanas pequeñas.
        frame_izq = ctk.CTkScrollableFrame(frame_izq_contenedor, width=300, fg_color="transparent")
        frame_izq.pack(fill="both", expand=True)

        frame_der = ctk.CTkFrame(self.contenedor)
        frame_der.pack(side="right", fill="both", padx=5, pady=5, expand=True)

        # --- Formulario de actividad propia ---
        ctk.CTkLabel(frame_izq, text="Mis Actividades", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(frame_izq, text="Añadir Actividad", font=("Arial", 16, "bold")).pack(pady=(5, 5))

        ctk.CTkLabel(frame_izq, text="Materia:").pack(anchor="w", padx=25)
        self.ent_materia_est = ctk.CTkEntry(frame_izq, placeholder_text="Ej. Cálculo II", width=280)
        self.ent_materia_est.pack(pady=5)

        ctk.CTkLabel(frame_izq, text="Tipo de Tarea:").pack(anchor="w", padx=25)
        self.ent_tipo_est = ctk.CTkComboBox(frame_izq, values=list(COLORES_TIPO.keys()), state="readonly", width=280)
        self.ent_tipo_est.set("Tarea")
        self.ent_tipo_est.pack(pady=5)

        ctk.CTkLabel(frame_izq, text="Fecha de Entrega:").pack(anchor="w", padx=25)
        frame_fecha = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_fecha.pack(pady=5)

        anio_actual = datetime.now().year
        dias = [str(i).zfill(2) for i in range(1, 32)]
        meses = [str(i).zfill(2) for i in range(1, 13)]
        anios = [str(i) for i in range(anio_actual, anio_actual + 6)]

        self.combo_dia_est = ctk.CTkComboBox(frame_fecha, values=dias, width=75, state="readonly")
        self.combo_dia_est.set(datetime.now().strftime("%d"))
        self.combo_dia_est.pack(side="left", padx=2)
        self.combo_mes_est = ctk.CTkComboBox(frame_fecha, values=meses, width=75, state="readonly")
        self.combo_mes_est.set(datetime.now().strftime("%m"))
        self.combo_mes_est.pack(side="left", padx=2)
        self.combo_anio_est = ctk.CTkComboBox(frame_fecha, values=anios, width=90, state="readonly")
        self.combo_anio_est.set(str(anio_actual))
        self.combo_anio_est.pack(side="left", padx=2)

        ctk.CTkLabel(frame_izq, text="Descripción de la actividad:").pack(anchor="w", padx=25)
        self.txt_desc_est = ctk.CTkTextbox(frame_izq, width=280, height=110)
        self.txt_desc_est.pack(pady=5)

        frame_botones_form = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_botones_form.pack(pady=10)
        self.btn_guardar_est = ctk.CTkButton(frame_botones_form, text="Añadir Actividad", fg_color="#2980B9",
                                              hover_color="#2471A3", command=self.guardar_actividad_estudiante,
                                              width=180)
        self.btn_guardar_est.pack(side="left", padx=3)
        self.btn_cancelar_edicion_est = ctk.CTkButton(frame_botones_form, text="Cancelar", fg_color="#95A5A6",
                                                       hover_color="#7F8C8D", width=90,
                                                       command=self.cancelar_edicion_estudiante)
        # se muestra solo durante edición (ver editar_actividad_estudiante / cancelar_edicion_estudiante)

        # --- Panel derecho: filtros + lista ---
        armar_panel_filtros(frame_der, self, self.actualizar_lista_estudiante)
        self.scroll_actividades = ctk.CTkScrollableFrame(frame_der, label_text="Mi Cronograma de Actividades")
        self.scroll_actividades.pack(fill="both", expand=True, padx=10, pady=10)

        self.actualizar_lista_estudiante()

    # =====================================================================
    # GESTIÓN DE ACTIVIDADES PROPIAS (crear / editar / eliminar)
    # =====================================================================
    def cancelar_edicion_estudiante(self):
        self.actividad_en_edicion = None
        self.ent_materia_est.delete(0, "end")
        self.txt_desc_est.delete("1.0", "end")
        self.ent_tipo_est.set("Tarea")
        self.btn_guardar_est.configure(text="Añadir Actividad")
        self.btn_cancelar_edicion_est.pack_forget()

    def guardar_actividad_estudiante(self):
        materia = self.ent_materia_est.get().strip().title()
        tipo = self.ent_tipo_est.get()
        desc = self.txt_desc_est.get("1.0", "end-1c").strip()
        fecha_str = f"{self.combo_anio_est.get()}-{self.combo_mes_est.get()}-{self.combo_dia_est.get()}"

        if not materia:
            messagebox.showwarning("Campo vacío", "Escribe el nombre de la materia.")
            return
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
                "UPDATE actividades_estudiante SET materia = ?, tipo = ?, fecha = ?, descripcion = ? "
                "WHERE id = ? AND usuario_id = ?",
                (materia, tipo, fecha_str, desc, self.actividad_en_edicion, self.usuario_id_actual)
            )
        else:
            self.cursor.execute(
                "INSERT INTO actividades_estudiante (usuario_id, materia, tipo, fecha, descripcion) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.usuario_id_actual, materia, tipo, fecha_str, desc)
            )
        self.conn.commit()
        self.cancelar_edicion_estudiante()
        self.actualizar_lista_estudiante()

    def editar_actividad_estudiante(self, id_act, materia, tipo, fecha, descripcion):
        self.actividad_en_edicion = id_act
        self.ent_materia_est.delete(0, "end")
        self.ent_materia_est.insert(0, materia or "")
        self.ent_tipo_est.set(tipo)
        try:
            anio, mes, dia = fecha.split("-")
            self.combo_anio_est.set(anio)
            self.combo_mes_est.set(mes)
            self.combo_dia_est.set(dia)
        except ValueError:
            pass
        self.txt_desc_est.delete("1.0", "end")
        self.txt_desc_est.insert("1.0", descripcion)
        self.btn_guardar_est.configure(text="Guardar Cambios")
        self.btn_cancelar_edicion_est.pack(side="left", padx=3)

    def eliminar_actividad_estudiante(self, id_act):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta actividad?"):
            self.cursor.execute(
                "DELETE FROM actividades_estudiante WHERE id = ? AND usuario_id = ?",
                (id_act, self.usuario_id_actual)
            )
            self.conn.commit()
            self.actualizar_lista_estudiante()

    def marcar_entrega_estudiante(self, actividad_id, estado_actual):
        nuevo_estado = "Entregado" if estado_actual != "Entregado" else "Pendiente"
        self.cursor.execute(
            "UPDATE actividades_estudiante SET estado = ? WHERE id = ? AND usuario_id = ?",
            (nuevo_estado, actividad_id, self.usuario_id_actual)
        )
        self.conn.commit()
        self.actualizar_lista_estudiante()

    # =====================================================================
    # RENDERIZADO DE LA LISTA (vista estudiante)
    # =====================================================================
    def actualizar_lista_estudiante(self):
        for w in self.scroll_actividades.winfo_children():
            w.destroy()

        # El orden por "materia" en el panel de filtros compartido usa el
        # alias nombre_materia (pensado originalmente para la vista del
        # Docente); aquí la columna real se llama "materia".
        campo_orden = campo_orden_sql(self).replace("LOWER(nombre_materia)", "LOWER(materia)")

        query = f"""
            SELECT id, materia, tipo, fecha, descripcion, estado
            FROM actividades_estudiante
            WHERE usuario_id = ?
            AND (LOWER(descripcion) LIKE ? OR LOWER(materia) LIKE ?)
            ORDER BY {campo_orden}
        """
        patron = f"%{self.texto_busqueda}%"
        self.cursor.execute(query, (self.usuario_id_actual, patron, patron))
        filas = self.cursor.fetchall()

        if not filas:
            ctk.CTkLabel(self.scroll_actividades,
                         text="No tienes actividades. Usa el formulario de la izquierda para crear una.",
                         font=("Arial", 13, "italic")).pack(pady=20)
            return

        for id_act, materia, tipo, fecha, descripcion, estado in filas:
            crear_tarjeta_actividad(
                self.scroll_actividades, materia=materia or "Sin materia", tipo=tipo, fecha=fecha,
                descripcion=descripcion, estado=estado,
                construir_botones=lambda parent, i=id_act, m=materia, t=tipo, f=fecha, d=descripcion, e=estado: [
                    ctk.CTkButton(
                        parent,
                        text="↩️ Pendiente" if e == "Entregado" else "✅ Completar",
                        width=100, height=28,
                        fg_color=COLOR_PENDIENTE if e == "Entregado" else COLOR_ENTREGADO,
                        hover_color="#95A5A6" if e == "Entregado" else "#27AE60",
                        command=lambda: self.marcar_entrega_estudiante(i, e)
                    ).pack(pady=3),
                    ctk.CTkButton(parent, text="✏️ Editar", width=100, height=28,
                                  fg_color="#F39C12", hover_color="#D68910",
                                  command=lambda: self.editar_actividad_estudiante(i, m, t, f, d)).pack(pady=3),
                    ctk.CTkButton(parent, text="❌ Eliminar", width=100, height=28,
                                  fg_color="#D9534F", hover_color="#C9302C",
                                  command=lambda: self.eliminar_actividad_estudiante(i)).pack(pady=3),
                ]
            )
