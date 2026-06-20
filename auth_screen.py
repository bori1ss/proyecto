"""
auth_screen.py
Pantalla de autenticación (Iniciar Sesión / Registrarse) y encabezado
de sesión compartido por las pantallas de Docente y Estudiante.

Se implementa como un Mixin: la clase principal de la app (en main.py)
hereda de AuthMixin y obtiene estos métodos como propios, compartiendo
self.contenedor, self.cursor, self.conn, etc.
"""
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from database import hash_password


class AuthMixin:
    def mostrar_pantalla_autenticacion(self):
        self.limpiar_pantalla()

        ctk.CTkLabel(self.contenedor, text="Sistema de Organización Académica",
                     font=("Arial", 24, "bold")).pack(pady=15)

        pestanas = ctk.CTkTabview(self.contenedor, width=400, height=400)
        pestanas.pack(pady=10)

        tab_login = pestanas.add("Iniciar Sesión")
        tab_registro = pestanas.add("Registrarse")

        # --- LOGIN ---
        ctk.CTkLabel(tab_login, text="Ingresa tus credenciales", font=("Arial", 14)).pack(pady=10)
        self.log_user = ctk.CTkEntry(tab_login, placeholder_text="Usuario", width=250)
        self.log_user.pack(pady=10)
        self.log_pass = ctk.CTkEntry(tab_login, placeholder_text="Contraseña", show="*", width=250)
        self.log_pass.pack(pady=10)
        self.log_pass.bind("<Return>", lambda e: self.login_usuario())

        ctk.CTkButton(tab_login, text="Entrar", command=self.login_usuario, width=200).pack(pady=20)

        # --- REGISTRO ---
        ctk.CTkLabel(tab_registro, text="Crea una cuenta nueva", font=("Arial", 14)).pack(pady=10)
        self.reg_user = ctk.CTkEntry(tab_registro, placeholder_text="Nuevo Usuario", width=250)
        self.reg_user.pack(pady=5)
        self.reg_pass = ctk.CTkEntry(tab_registro, placeholder_text="Contraseña", show="*", width=250)
        self.reg_pass.pack(pady=5)
        self.reg_pass2 = ctk.CTkEntry(tab_registro, placeholder_text="Confirmar Contraseña", show="*", width=250)
        self.reg_pass2.pack(pady=5)

        ctk.CTkLabel(tab_registro, text="Selecciona tu Rol Académico:").pack(pady=2)
        self.reg_rol = ctk.CTkComboBox(tab_registro, values=["Estudiante", "Docente"], state="readonly", width=250)
        self.reg_rol.set("Estudiante")
        self.reg_rol.pack(pady=5)

        ctk.CTkButton(tab_registro, text="Registrar Cuenta", fg_color="#E67E22", hover_color="#D35400",
                      command=self.registrar_usuario, width=200).pack(pady=15)

    def registrar_usuario(self):
        u = self.reg_user.get().strip()
        c = self.reg_pass.get().strip()
        c2 = self.reg_pass2.get().strip()
        r = self.reg_rol.get().lower()

        if not u or not c:
            messagebox.showwarning("Campos Vacíos", "Por favor, rellena todos los campos de registro.")
            return
        if c != c2:
            messagebox.showwarning("Contraseña", "Las contraseñas no coinciden.")
            return
        if len(c) < 4:
            messagebox.showwarning("Contraseña débil", "La contraseña debe tener al menos 4 caracteres.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                (u, hash_password(c), r)
            )
            self.conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Ya puedes iniciar sesión.")
            self.reg_user.delete(0, "end")
            self.reg_pass.delete(0, "end")
            self.reg_pass2.delete(0, "end")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")

    def login_usuario(self):
        u = self.log_user.get().strip()
        c = self.log_pass.get().strip()
        self.cursor.execute(
            "SELECT id, usuario, rol FROM usuarios WHERE usuario = ? AND contrasena = ?",
            (u, hash_password(c))
        )
        resultado = self.cursor.fetchone()

        if resultado:
            self.usuario_id_actual, self.usuario_nombre_actual, self.rol_actual = resultado
            self.materia_seleccionada_id = None
            self.actividad_en_edicion = None
            self.orden_actual = "fecha"
            self.orden_ascendente = True
            self.texto_busqueda = ""
            if self.rol_actual == "docente":
                self.mostrar_dashboard_docente()
            else:
                self.mostrar_dashboard_estudiante()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def cerrar_sesion(self):
        self.usuario_id_actual = None
        self.usuario_nombre_actual = None
        self.rol_actual = None
        self.materia_seleccionada_id = None
        self.actividad_en_edicion = None
        self.mostrar_pantalla_autenticacion()

    def encabezado(self, contenedor_padre):
        """Barra superior común con info de sesión y botón de logout."""
        frame_top = ctk.CTkFrame(contenedor_padre, fg_color="transparent")
        frame_top.pack(fill="x", pady=5)
        ctk.CTkLabel(
            frame_top,
            text=f"Sesión: {self.usuario_nombre_actual.upper()} | Rol: {self.rol_actual.capitalize()}",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=5)
        ctk.CTkButton(frame_top, text="Cerrar Sesión", width=110, fg_color="#D9534F",
                      hover_color="#C9302C", command=self.cerrar_sesion).pack(side="right", padx=5)
