import os
import sys
from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk

import Back_shutdown as back


APP_DIR = os.path.dirname(os.path.abspath(__file__))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def parse_args_notify():
    if len(sys.argv) >= 3 and sys.argv[1] == "--notify":
        return " ".join(sys.argv[2:]).strip().strip('"')
    return None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Programador de Apagado")
        self._set_responsive_geometry()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Listo.")
        self.selected_task_var = tk.StringVar(value="Ninguna tarea seleccionada")

        self._build_ui()
        self.refresh_list()

        self.bind("<Configure>", self._on_window_resize)

    def _set_responsive_geometry(self):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        win_w = int(screen_w * 0.88)
        win_h = int(screen_h * 0.84)

        min_w = 1120
        min_h = 700

        win_w = max(min_w, min(win_w, screen_w - 40))
        win_h = max(min_h, min(win_h, screen_h - 70))

        x = max((screen_w - win_w) // 2, 0)
        y = max((screen_h - win_h) // 2, 0)

        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.minsize(min_w, min_h)

    def _build_ui(self):
        self._configure_treeview_style()

        self.root_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.root_frame.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.root_frame.grid_columnconfigure(0, weight=1)
        self.root_frame.grid_rowconfigure(1, weight=1)
        self.root_frame.grid_rowconfigure(2, weight=0)

        self._build_header(self.root_frame)
        self._build_body(self.root_frame)
        self._build_footer(self.root_frame)

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, corner_radius=18, fg_color=("#dbeafe", "#172554"))
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="⚡ Programador de Apagado",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 2))

        subtitle = ctk.CTkLabel(
            header,
            text="Crea, edita y administra tareas de apagado de Windows con una interfaz moderna.",
            font=ctk.CTkFont(size=13),
            text_color=("#334155", "#cbd5e1")
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))

    def _build_body(self, parent):
        self.body = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=0)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(self.body)
        self._build_right_panel(self.body)

    def _build_left_panel(self, parent):
        self.left_outer = ctk.CTkFrame(parent, corner_radius=18, fg_color=("#f8fafc", "#111827"))
        self.left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.left_outer.grid_rowconfigure(0, weight=1)
        self.left_outer.grid_columnconfigure(0, weight=1)

        self.left_scroll = ctk.CTkScrollableFrame(
            self.left_outer,
            corner_radius=18,
            fg_color="transparent"
        )
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.left_scroll.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            self.left_scroll,
            text="Configuración",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0f172a", "#f8fafc")
        )
        form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 4))

        selected_lbl = ctk.CTkLabel(
            self.left_scroll,
            textvariable=self.selected_task_var,
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#94a3b8"),
            wraplength=320,
            justify="left"
        )
        selected_lbl.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))

        # ===== Datos base =====
        base_card = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#ede9fe", "#312e81"))
        base_card.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        base_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            base_card,
            text="Datos base",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#312e81", "#ede9fe")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        ctk.CTkLabel(base_card, text="Nombre", text_color=("#1e1b4b", "#e0e7ff")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 6)
        )
        self.name_var = tk.StringVar(value="MiApagado")
        self.name_entry = ctk.CTkEntry(base_card, textvariable=self.name_var, height=38)
        self.name_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        ctk.CTkLabel(base_card, text="Modo", text_color=("#1e1b4b", "#e0e7ff")).grid(
            row=3, column=0, sticky="w", padx=14, pady=(0, 6)
        )
        self.mode_var = tk.StringVar(value="Fecha y hora")
        modes = ["Fecha y hora", "En X horas", "Diario (perpetuo)", "Cada N horas (perpetuo)"]
        self.mode_menu = ctk.CTkOptionMenu(
            base_card,
            variable=self.mode_var,
            values=modes,
            height=38,
            command=lambda _=None: self._toggle_fields()
        )
        self.mode_menu.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 14))

        # ===== Fecha y hora =====
        self.dt_frame = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#dcfce7", "#14532d"))
        self.dt_frame.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.dt_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.dt_frame,
            text="Programación exacta",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#14532d", "#dcfce7")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))

        ctk.CTkLabel(self.dt_frame, text="Fecha", text_color=("#166534", "#bbf7d0")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        ctk.CTkLabel(self.dt_frame, text="Hora", text_color=("#166534", "#bbf7d0")).grid(
            row=1, column=1, sticky="w", padx=14, pady=(0, 4)
        )

        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ctk.CTkEntry(self.dt_frame, textvariable=self.date_var, height=36)
        self.date_entry.grid(row=2, column=0, sticky="ew", padx=(14, 7), pady=(0, 12))

        self.time_var = tk.StringVar(value=datetime.now().replace(second=0, microsecond=0).strftime("%H:%M"))
        self.time_entry = ctk.CTkEntry(self.dt_frame, textvariable=self.time_var, height=36)
        self.time_entry.grid(row=2, column=1, sticky="ew", padx=(7, 14), pady=(0, 12))

        # ===== En horas =====
        self.hours_frame = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#fef3c7", "#78350f"))
        self.hours_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.hours_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.hours_frame,
            text="Apagar en X horas",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#78350f", "#fde68a")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        ctk.CTkLabel(self.hours_frame, text="Horas desde ahora", text_color=("#92400e", "#fde68a")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        self.hours_var = tk.StringVar(value="2")
        self.hours_entry = ctk.CTkEntry(self.hours_frame, textvariable=self.hours_var, height=36)
        self.hours_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        # ===== Diario =====
        self.daily_frame = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#fee2e2", "#7f1d1d"))
        self.daily_frame.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.daily_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.daily_frame,
            text="Programación diaria",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#7f1d1d", "#fecaca")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        ctk.CTkLabel(self.daily_frame, text="Hora diaria", text_color=("#991b1b", "#fecaca")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        self.daily_time_var = tk.StringVar(value="23:30")
        self.daily_entry = ctk.CTkEntry(self.daily_frame, textvariable=self.daily_time_var, height=36)
        self.daily_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        # ===== Cada N horas =====
        self.hourly_frame = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#e0f2fe", "#0c4a6e"))
        self.hourly_frame.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.hourly_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.hourly_frame,
            text="Repetición periódica",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0c4a6e", "#bae6fd")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        ctk.CTkLabel(self.hourly_frame, text="Cada N horas", text_color=("#075985", "#bae6fd")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        self.every_n_var = tk.StringVar(value="6")
        self.every_n_entry = ctk.CTkEntry(self.hourly_frame, textvariable=self.every_n_var, height=36)
        self.every_n_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        # ===== Acciones =====
        actions = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#f1f5f9", "#1e293b"))
        actions.grid(row=7, column=0, sticky="ew", padx=18, pady=(6, 12))
        actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            actions,
            text="Acciones",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0f172a", "#e2e8f0")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 8))

        self.create_btn = ctk.CTkButton(
            actions, text="Crear", height=40, fg_color="#16a34a", hover_color="#15803d", command=self.create_task
        )
        self.create_btn.grid(row=1, column=0, sticky="ew", padx=(14, 7), pady=(0, 14))

        self.edit_btn = ctk.CTkButton(
            actions, text="Editar", height=40, fg_color="#2563eb", hover_color="#1d4ed8", command=self.edit_selected
        )
        self.edit_btn.grid(row=1, column=1, sticky="ew", padx=(7, 14), pady=(0, 14))

        # ===== Aviso =====
        notify_box = ctk.CTkFrame(self.left_scroll, corner_radius=16, fg_color=("#fae8ff", "#581c87"))
        notify_box.grid(row=8, column=0, sticky="ew", padx=18, pady=(0, 18))
        notify_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            notify_box,
            text="Aviso al iniciar sesión",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#581c87", "#f5d0fe")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        self.notify_msg_var = tk.StringVar(value="Este PC tiene apagado programado. Revisa tus tareas.")
        self.notify_entry = ctk.CTkEntry(notify_box, textvariable=self.notify_msg_var, height=36)
        self.notify_entry.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        notify_btns = ctk.CTkFrame(notify_box, fg_color="transparent")
        notify_btns.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        notify_btns.grid_columnconfigure((0, 1), weight=1)

        self.enable_notify_btn = ctk.CTkButton(
            notify_btns, text="Activar aviso", height=38, fg_color="#7c3aed", hover_color="#6d28d9", command=self.enable_notify
        )
        self.enable_notify_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.disable_notify_btn = ctk.CTkButton(
            notify_btns, text="Desactivar aviso", height=38, fg_color="#dc2626", hover_color="#b91c1c", command=self.disable_notify
        )
        self.disable_notify_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._toggle_fields()

    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(right, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            top,
            text="Tareas registradas",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            top,
            text="Selecciona una tarea para cargarla en el formulario y editarla.",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        table_card = ctk.CTkFrame(right, corner_radius=14)
        table_card.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 10))
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_card,
            columns=("task_name", "kind", "created_at", "schedule_at", "detail"),
            show="headings"
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)

        scroll_y = ctk.CTkScrollbar(table_card, orientation="vertical", command=self.tree.yview)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(8, 10), pady=10)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.heading("task_name", text="Nombre de tarea")
        self.tree.heading("kind", text="Tipo")
        self.tree.heading("created_at", text="Creada")
        self.tree.heading("schedule_at", text="Programada para")
        self.tree.heading("detail", text="Detalle")

        self.tree.column("task_name", width=290, anchor="w")
        self.tree.column("kind", width=120, anchor="w")
        self.tree.column("created_at", width=150, anchor="w")
        self.tree.column("schedule_at", width=160, anchor="w")
        self.tree.column("detail", width=420, anchor="w")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_task)

        buttons = ctk.CTkFrame(right, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        buttons.grid_columnconfigure((0, 1, 2), weight=1)

        self.refresh_btn = ctk.CTkButton(buttons, text="Actualizar lista", height=40, command=self.refresh_list)
        self.refresh_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.query_btn = ctk.CTkButton(buttons, text="Ver detalle", height=40, command=self.query_selected)
        self.query_btn.grid(row=0, column=1, sticky="ew", padx=6)

        self.delete_btn = ctk.CTkButton(
            buttons, text="Eliminar", height=40, fg_color="#dc2626", hover_color="#b91c1c", command=self.delete_selected
        )
        self.delete_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, corner_radius=14, height=48, fg_color=("#e2e8f0", "#0f172a"))
        footer.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=("#0f172a", "#e2e8f0")
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=16, pady=12)

    def _configure_treeview_style(self):
        style = ttk.Style()
        try:
            style.theme_use("default")
        except Exception:
            pass

        style.configure(
            "Treeview",
            background="#1b1f24",
            foreground="#f3f4f6",
            fieldbackground="#1b1f24",
            rowheight=34,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10)
        )
        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "white")]
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#1f2937")]
        )

    def _on_window_resize(self, event=None):
        try:
            total_w = self.winfo_width()
            left_w = max(330, min(430, int(total_w * 0.31)))
            self.left_outer.configure(width=left_w)
        except Exception:
            pass

    def _toggle_fields(self):
        mode = self.mode_var.get()

        def show(widget, visible: bool):
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

        show(self.dt_frame, mode == "Fecha y hora")
        show(self.hours_frame, mode == "En X horas")
        show(self.daily_frame, mode == "Diario (perpetuo)")
        show(self.hourly_frame, mode == "Cada N horas (perpetuo)")

    def set_status(self, text: str):
        self.status_var.set(text)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            recs = back.list_records()
            for r in recs:
                self.tree.insert(
                    "",
                    "end",
                    values=(r.task_name, r.kind, r.created_at, r.schedule_at or "", str(r.detail))
                )
            self.set_status(f"Lista actualizada. Total de tareas: {len(recs)}")
        except Exception as e:
            self.set_status(f"Error al actualizar la lista: {e}")
            messagebox.showerror("Error", str(e))

    def create_task(self):
        name = self.name_var.get().strip() or "MiApagado"
        mode = self.mode_var.get()

        try:
            if mode == "Fecha y hora":
                d = self.date_var.get().strip()
                t = self.time_var.get().strip()
                dt = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
                res = back.create_shutdown_at_datetime(name, dt)

            elif mode == "En X horas":
                hours = float(self.hours_var.get().strip())
                res = back.create_shutdown_in_hours(name, hours)

            elif mode == "Diario (perpetuo)":
                hhmm = self.daily_time_var.get().strip()
                datetime.strptime(hhmm, "%H:%M")
                res = back.create_shutdown_daily(name, hhmm)

            else:
                n = int(self.every_n_var.get().strip())
                res = back.create_shutdown_hourly(name, n)

        except ValueError as e:
            messagebox.showerror("Dato inválido", f"Revisa el formato.\n\nDetalle: {e}")
            self.set_status("Error de validación en los datos.")
            return

        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo crear la tarea."))
            self.set_status("No se pudo crear la tarea.")
            return

        messagebox.showinfo("OK", f"Tarea creada:\n{res.get('task_name')}")
        self.set_status(f"Tarea creada: {res.get('task_name')}")
        self.refresh_list()

    def _get_selected_task_name(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        if not values:
            return None
        return values[0]

    def on_select_task(self, event=None):
        task_name = self._get_selected_task_name()
        if not task_name:
            self.selected_task_var.set("Ninguna tarea seleccionada")
            return

        rec = back.get_record(task_name)
        if not rec:
            self.selected_task_var.set("No se pudo cargar la tarea seleccionada")
            return

        self.selected_task_var.set(f"Seleccionada: {task_name}")
        self.name_var.set(task_name)

        if rec.kind == "once_datetime":
            self.mode_var.set("Fecha y hora")
            dt_str = rec.detail.get("datetime") or rec.schedule_at
            if dt_str:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                self.date_var.set(dt.strftime("%Y-%m-%d"))
                self.time_var.set(dt.strftime("%H:%M"))

        elif rec.kind == "in_hours":
            self.mode_var.set("En X horas")
            self.hours_var.set(str(rec.detail.get("hours", 2)))

        elif rec.kind == "daily":
            self.mode_var.set("Diario (perpetuo)")
            self.daily_time_var.set(rec.detail.get("time", "23:30"))

        elif rec.kind == "hourly":
            self.mode_var.set("Cada N horas (perpetuo)")
            self.every_n_var.set(str(rec.detail.get("every_n_hours", 6)))

        self._toggle_fields()
        self.set_status(f"Tarea cargada para edición: {task_name}")

    def edit_selected(self):
        task_name = self._get_selected_task_name()
        if not task_name:
            messagebox.showwarning("Selecciona", "Selecciona una tarea primero.")
            self.set_status("No hay tarea seleccionada para editar.")
            return

        mode = self.mode_var.get()

        try:
            if mode == "Fecha y hora":
                d = self.date_var.get().strip()
                t = self.time_var.get().strip()
                dt = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
                res = back.edit_shutdown_task(task_name, "once_datetime", dt=dt)

            elif mode == "En X horas":
                hours = float(self.hours_var.get().strip())
                res = back.edit_shutdown_task(task_name, "in_hours", hours=hours)

            elif mode == "Diario (perpetuo)":
                hhmm = self.daily_time_var.get().strip()
                datetime.strptime(hhmm, "%H:%M")
                res = back.edit_shutdown_task(task_name, "daily", hhmm=hhmm)

            else:
                n = int(self.every_n_var.get().strip())
                res = back.edit_shutdown_task(task_name, "hourly", every_n_hours=n)

        except ValueError as e:
            messagebox.showerror("Dato inválido", f"Revisa el formato.\n\nDetalle: {e}")
            self.set_status("Error de validación al editar.")
            return

        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo editar la tarea."))
            self.set_status("No se pudo editar la tarea.")
            return

        warning = res.get("warning")
        if warning:
            messagebox.showwarning("Editada con aviso", f"Tarea actualizada:\n{task_name}\n\n{warning}")
        else:
            messagebox.showinfo("OK", f"Tarea editada:\n{task_name}")

        self.set_status(f"Tarea editada: {task_name}")
        self.refresh_list()

    def delete_selected(self):
        task_name = self._get_selected_task_name()
        if not task_name:
            messagebox.showwarning("Selecciona", "Selecciona una tarea primero.")
            self.set_status("No hay tarea seleccionada para eliminar.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar esta tarea?\n\n{task_name}"):
            self.set_status("Eliminación cancelada.")
            return

        res = back.delete_record(task_name)
        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo eliminar."))
            self.set_status("No se pudo eliminar la tarea.")
        else:
            messagebox.showinfo("OK", f"Eliminada: {task_name}")
            self.selected_task_var.set("Ninguna tarea seleccionada")
            self.set_status(f"Tarea eliminada: {task_name}")

        self.refresh_list()

    def query_selected(self):
        task_name = self._get_selected_task_name()
        if not task_name:
            messagebox.showwarning("Selecciona", "Selecciona una tarea primero.")
            self.set_status("No hay tarea seleccionada para consultar.")
            return

        res = back.query_task_verbose(task_name)
        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo consultar."))
            self.set_status("No se pudo consultar la tarea.")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Detalle: {task_name}")
        win.geometry("950x620")
        win.minsize(700, 420)

        wrap = ctk.CTkFrame(win, corner_radius=14)
        wrap.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(
            wrap,
            text=f"Detalle de la tarea",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", padx=14, pady=(14, 6))

        subtitle = ctk.CTkLabel(
            wrap,
            text=task_name,
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        subtitle.pack(anchor="w", padx=14, pady=(0, 10))

        txt = ctk.CTkTextbox(wrap)
        txt.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        txt.insert("1.0", res["output"])
        txt.configure(state="disabled")

        self.set_status(f"Mostrando detalle de: {task_name}")

    def enable_notify(self):
        msg = self.notify_msg_var.get().strip() or "Este PC tiene apagado programado."
        python_exe = sys.executable
        ui_path = os.path.join(APP_DIR, "UI_LAUNCHER.py")

        res = back.enable_startup_notify(python_exe, ui_path, msg)
        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo activar el aviso."))
            self.set_status("No se pudo activar el aviso.")
            return

        messagebox.showinfo("OK", f"Aviso activado (tarea):\n{res.get('task_name')}")
        self.set_status(f"Aviso activado: {res.get('task_name')}")

    def disable_notify(self):
        res = back.disable_startup_notify()
        if not res.get("ok"):
            messagebox.showerror("Error", res.get("error", "No se pudo desactivar el aviso."))
            self.set_status("No se pudo desactivar el aviso.")
            return

        messagebox.showinfo("OK", "Aviso desactivado.")
        self.set_status("Aviso desactivado.")


if __name__ == "__main__":
    notify_msg = parse_args_notify()
    if notify_msg:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Aviso", notify_msg)
        root.destroy()
        sys.exit(0)

    app = App()
    app.mainloop()