from customtkinter import *
from codigo.usuario import GestorPrestamos  # Importa para poder consultar préstamos
import os

class info_libro(CTkToplevel):
    """
    Ventana emergente (Toplevel) para mostrar la información detallada de un libro.
    Incluye metadatos, vista previa, estadísticas (total palabras/páginas),
    un buscador de palabras internas, una gráfica de las palabras más repetidas,
    y botones para gestionar el préstamo o devolución.
    """
    def __init__(self, parent, libro, *args, **kwargs):
        # Aseguramos pasar los argumentos al constructor padre
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.libro = libro

        self.title("INFORMACIÓN DEL LIBRO")
        self.configure(fg_color="#d9dbff")  # Fondo azul claro pastel
        
        # Tamaño amplio para organizar todo
        self.geometry("1100x750")
        self.attributes("-topmost", True)  # Mantener por encima de la ventana principal

        # Columnas: Izquierda (Metadatos y Préstamos), Derecha (Preview y Gráfica)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        
        self.grid_rowconfigure(0, weight=1)

        # Inicializamos los marcos principales
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        """
        Dibuja los componentes en la pantalla de detalles.
        """
        # Limpiar si ya existe para redibujado tras actualización de estado
        for widget in self.winfo_children():
            widget.destroy()

        # COLUMNA IZQUIERDA: Metadatos Básicos y Préstamo
        self.frame_izq = CTkFrame(self, 
                                  fg_color="#bec1f6", 
                                  border_color="#696dc2", 
                                  border_width=1, 
                                  corner_radius=5)
        self.frame_izq.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        self.frame_izq.grid_columnconfigure(0, weight=1)
        self.frame_izq.grid_rowconfigure(0, weight=1)  # Título
        self.frame_izq.grid_rowconfigure(1, weight=5)  # Metadatos
        self.frame_izq.grid_rowconfigure(2, weight=3)  # Info préstamo
        self.frame_izq.grid_rowconfigure(3, weight=2)  # Acciones

        # Botón Atrás
        self.btn_atras = CTkButton(self.frame_izq, 
                                   text="← Volver al catálogo", 
                                   fg_color="#1a1c43", 
                                   text_color="white", 
                                   command=self.destroy)
        self.btn_atras.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        # Contenedor de Metadatos
        self.frame_meta = CTkFrame(self.frame_izq,
                                   fg_color="transparent")
        self.frame_meta.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_meta.grid_columnconfigure(0, weight=1)
        self.frame_meta.grid_columnconfigure(1, weight=2)

        # Título del libro (Grande y visible)
        self.lbl_titulo = CTkLabel(self.frame_meta, 
                                   text=self.libro.titulo, 
                                   text_color="black", 
                                   font=("Calibri Light", 22, "bold"), 
                                   wraplength=350, justify="left")
        self.lbl_titulo.grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="w")

        # Campos de Metadatos
        metadatos = [
            ("Autor:", self.libro.autor),
            ("Idioma:", self.libro.idioma),
            ("Lanzamiento:", self.libro.release_date),
            ("Estado:", self.libro.estado),
        ]

        for idx, (label, valor) in enumerate(metadatos):
            row_idx = idx + 1
            lbl_tag = CTkLabel(self.frame_meta, 
                               text=label, 
                               text_color="#1a1c43", 
                               font=("Calibri Light", 14, "bold"))
            lbl_tag.grid(row=row_idx, column=0, padx=10, pady=8, sticky="w")

            color_val = "black"
            if label == "Estado:":
                color_val = "#2c8d2c" if valor == "Disponible" else "#a01b1b"
                
            lbl_val = CTkLabel(self.frame_meta, 
                               text=valor, 
                               text_color=color_val, 
                               font=("Calibri Light", 14, "bold" if label == "Estado:" else "normal"), 
                               wraplength=220, 
                               justify="left")
            lbl_val.grid(row=row_idx, column=1, padx=10, pady=8, sticky="w")

        # SECCIÓN DE DATOS DE PRÉSTAMO ACTIVO
        self.frame_prestamo_info = CTkFrame(self.frame_izq, 
                                            fg_color="#dbddff", 
                                            corner_radius=5)
        self.frame_prestamo_info.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_prestamo_info.grid_columnconfigure(0, weight=1)

        prestamo_activo = self.parent.prestamos.obtener_prestamo_por_libro(self.libro)
        if prestamo_activo:
            self.lbl_pres_titulo = CTkLabel(self.frame_prestamo_info, 
                                            text="Información del Préstamo", 
                                            text_color="#1a1c43", 
                                            font=("Calibri Light", 15, "bold"))
            self.lbl_pres_titulo.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

            user_info = prestamo_activo.usuario
            detalles_p = [
                (f"Lector: {user_info.nombre if hasattr(user_info, 'nombre') else user_info.get('Nombre')}"),
                (f"Correo: {user_info.correo if hasattr(user_info, 'correo') else user_info.get('Correo')}"),
                (f"Teléfono: {user_info.telefono if hasattr(user_info, 'telefono') else user_info.get('Teléfono')}"),
                (f"Préstamo: {prestamo_activo.fecha_prestamo.strftime('%d/%m/%Y') if hasattr(prestamo_activo.fecha_prestamo, 'strftime') else prestamo_activo.fecha_prestamo}"),
                (f"Devolución: {prestamo_activo.fecha_devolucion.strftime('%d/%m/%Y') if hasattr(prestamo_activo.fecha_devolucion, 'strftime') else prestamo_activo.fecha_devolucion}")
            ]

            for i, det in enumerate(detalles_p):
                lbl_det = CTkLabel(self.frame_prestamo_info, text=det, text_color="black", font=("Calibri Light", 13), justify="left")
                lbl_det.grid(row=i+1, column=0, padx=15, pady=3, sticky="w")
        else:
            self.lbl_pres_vacio = CTkLabel(self.frame_prestamo_info, text="El libro está en la biblioteca,\nlisto para ser prestado.", text_color="#454ccd", font=("Calibri Light", 14, "italic"), justify="center")
            self.lbl_pres_vacio.grid(row=0, column=0, padx=15, pady=30, sticky="nsew")

        # BOTONES DE ACCIÓN (PRÉSTAMO / DEVOLUCIÓN)
    
        self.frame_botones = CTkFrame(self.frame_izq, 
                                      fg_color="transparent")
        self.frame_botones.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_botones.grid_columnconfigure(0, weight=1)

        if self.libro.estado == "Disponible":
            self.btn_accion = CTkButton(self.frame_botones,
                                        text="Solicitar préstamo",
                                        fg_color="#2c8d2c",  # Verde éxito
                                        hover_color="#1e641e",
                                        font=("Calibri Light", 16, "bold"),
                                        height=45,
                                        command=self.abrir_ventana_prestamo)
            self.btn_accion.grid(row=0, column=0, padx=10, pady=10, sticky="we")
        else:
            self.btn_accion = CTkButton(self.frame_botones,
                                        text="Devolver libro",
                                        fg_color="#c82333",  # Rojo peligro/devolución
                                        hover_color="#9c1c28",
                                        font=("Calibri Light", 16, "bold"),
                                        height=45,
                                        command=self.devolver_libro)
            self.btn_accion.grid(row=0, column=0, padx=10, pady=10, sticky="we")


        # =====================================================================
        # COLUMNA DERECHA: Preview, Buscador y Estadísticas
        # =====================================================================
        self.frame_der = CTkFrame(self, 
                                  fg_color="#bec1f6", 
                                  border_color="#696dc2", 
                                  border_width=1, 
                                  corner_radius=5)
        self.frame_der.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        self.frame_der.grid_columnconfigure(0, weight=1)
        self.frame_der.grid_rowconfigure(0, weight=2)  # Estadísticas rápidas
        self.frame_der.grid_rowconfigure(1, weight=5)  # Preview y Buscador
        self.frame_der.grid_rowconfigure(2, weight=6)  # Gráfica de palabras

        # --- SECCIÓN 1: Estadísticas rápidas ---
        self.frame_stats = CTkFrame(self.frame_der, 
                                    fg_color="#dbddff", 
                                    corner_radius=5)
        self.frame_stats.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.frame_stats.grid_columnconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(1, weight=1)

        palabras_totales = self.libro.contar_plbs()
        paginas_estimadas = self.libro.estimar_pags()

        self.box_palabras = CTkFrame(self.frame_stats, fg_color="transparent")
        self.box_palabras.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.lbl_cant_pal = CTkLabel(self.box_palabras, 
                                     text=f"{palabras_totales:,}", 
                                     text_color="#1a1c43", 
                                     font=("Calibri Light", 22, "bold"))
        self.lbl_cant_pal.pack(pady=(5, 0))
        self.lbl_lbl_pal = CTkLabel(self.box_palabras, 
                                    text="Palabras Totales", 
                                    text_color="black", 
                                    font=("Calibri Light", 13))
        self.lbl_lbl_pal.pack(pady=(0, 5))

        self.box_paginas = CTkFrame(self.frame_stats, 
                                    fg_color="transparent")
        self.box_paginas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.lbl_cant_pag = CTkLabel(self.box_paginas, 
                                     text=str(paginas_estimadas), 
                                     text_color="#1a1c43", 
                                     font=("Calibri Light", 22, "bold"))
        
        self.lbl_cant_pag.pack(pady=(5, 0))
        self.lbl_lbl_pag = CTkLabel(self.box_paginas, 
                                    text="Páginas Estimadas", 
                                    text_color="black", 
                                    font=("Calibri Light", 13))
        self.lbl_lbl_pag.pack(pady=(0, 5))

        # --- SECCIÓN 2: Vista previa (600 palabras) y Buscador interno ---
        self.frame_preview = CTkFrame(self.frame_der, 
                                      fg_color="transparent")
        self.frame_preview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.frame_preview.grid_columnconfigure(0, weight=6)
        self.frame_preview.grid_columnconfigure(1, weight=4)
        self.frame_preview.grid_rowconfigure(0, weight=1)

        # Caja de Texto Scrollable para la Vista Previa (primeras 600 palabras)
        self.box_txt_preview = CTkFrame(self.frame_preview, 
                                        fg_color="#dbddff", 
                                        corner_radius=5)
        self.box_txt_preview.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        
        self.lbl_prev_title = CTkLabel(self.box_txt_preview, 
                                       text="Vista Previa del Libro (600 Palabras)", 
                                       text_color="black", 
                                       font=("Calibri Light", 14, "bold"))
        self.lbl_prev_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.txt_preview = CTkTextbox(self.box_txt_preview, 
                                      fg_color="white", 
                                      text_color="black", 
                                      font=("Calibri Light", 12), 
                                      wrap="word", 
                                      height=140)
        self.txt_preview.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Insertamos el texto de vista previa en la caja
        preview_content = self.libro.obtener_preview()
        if preview_content.strip() == "":
            preview_content = "(El archivo de texto local no se encuentra o está vacío.)"
        self.txt_preview.insert("0.0", preview_content)
        self.txt_preview.configure(state="disabled")  # Solo lectura

        # Caja del Buscador de palabras internas
        self.box_buscador = CTkFrame(self.frame_preview, 
                                     fg_color="#dbddff", 
                                     corner_radius=5)
        self.box_buscador.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        self.box_buscador.grid_columnconfigure(0, weight=1)

        self.lbl_bus_title = CTkLabel(self.box_buscador, 
                                      text="Buscador de Palabra", 
                                      text_color="black", 
                                      font=("Calibri Light", 14, "bold"))
        self.lbl_bus_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.entry_palabra = CTkEntry(self.box_buscador, 
                                      placeholder_text="Escribe una palabra...", 
                                      fg_color="white", 
                                      border_color="#1a1c43")
        self.entry_palabra.grid(row=1, column=0, padx=15, pady=5, sticky="we")

        self.btn_buscar_interna = CTkButton(self.box_buscador, 
                                            text="Contar apariciones", 
                                            fg_color="#1a1c43", 
                                            hover_color="#272a63", 
                                            command=self.contar_palabra_interna)
        self.btn_buscar_interna.grid(row=2, column=0, padx=15, pady=5, sticky="we")

        self.lbl_resultado_busqueda = CTkLabel(self.box_buscador, 
                                               text="Conteo: -", 
                                               text_color="#1a1c43", 
                                               font=("Calibri Light", 15, "bold"))
        self.lbl_resultado_busqueda.grid(row=3, column=0, padx=15, pady=10, sticky="w")

        # --- SECCIÓN 3: Gráfica de palabras más repetidas ---
        self.frame_grafica = CTkFrame(self.frame_der, 
                                      fg_color="#dbddff", 
                                      corner_radius=5)
        self.frame_grafica.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        
        self.frame_grafica.grid_columnconfigure(0, weight=1)
        self.frame_grafica.grid_rowconfigure(0, weight=1)  # Título
        self.frame_grafica.grid_rowconfigure(1, weight=10) # Gráfico de barras

        self.lbl_graf_title = CTkLabel(self.frame_grafica, 
                                       text="Palabras Más Frecuentes (Excluyendo Conectores)", 
                                       text_color="black", 
                                       font=("Calibri Light", 14, "bold"))
        self.lbl_graf_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        # Contenedor de las barras
        self.box_bars = CTkScrollableFrame(self.frame_grafica, 
                                           fg_color="transparent")
        self.box_bars.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.box_bars.grid_columnconfigure(0, weight=3) # Palabra
        self.box_bars.grid_columnconfigure(1, weight=6) # Barra gráfica
        self.box_bars.grid_columnconfigure(2, weight=1) # Conteo numérico

        # Obtenemos las 10 palabras más frecuentes
        frecuentes = self.libro.plbs_mas_repetidas(10)
        
        if frecuentes:
            max_conteo = frecuentes[0][1]  # El conteo más alto sirve como base del 100% de la barra
            #[0]= la palabra repetida; [1]= lleva el conteo de esa palabra
            
            for i, (palabra, conteo) in enumerate(frecuentes):
                # 1. Etiqueta de la palabra
                lbl_plb = CTkLabel(self.box_bars, 
                                   text=f"{i+1}. {palabra}", 
                                   text_color="black", 
                                   font=("Calibri Light", 12, "bold"))
                lbl_plb.grid(row=i, column=0, padx=5, pady=4, sticky="w")

                # 2. Barra gráfica horizontal
                # Calculamos el ancho de la barra proporcional al conteo máximo (ancho max de 250px)
                ancho_barra = int(220 * (conteo / max_conteo))
                if ancho_barra < 5:
                    ancho_barra = 5

                bar_container = CTkFrame(self.box_bars, fg_color="transparent", height=16)
                bar_container.grid(row=i, column=1, padx=5, pady=4, sticky="w")

                bar_color = "#696dc2" if i % 2 == 0 else "#1a1c43"  # Alternamos colores premium
                bar = CTkFrame(bar_container, fg_color=bar_color, width=ancho_barra, height=14, corner_radius=2)
                bar.pack(side="left")

                # 3. Conteo numérico
                lbl_num = CTkLabel(self.box_bars, text=f"{conteo:,}", text_color="black", font=("Calibri Light", 12))
                lbl_num.grid(row=i, column=2, padx=5, pady=4, sticky="e")
        else:
            lbl_sin_datos = CTkLabel(self.box_bars, text="No hay suficientes datos de texto para generar el análisis gráfico.", text_color="#1a1c43", font=("Calibri Light", 13, "italic"))
            lbl_sin_datos.grid(row=0, column=0, columnspan=3, padx=20, pady=40, sticky="nsew")

    def contar_palabra_interna(self):
        """
        Lee la palabra ingresada por el usuario y muestra el conteo exacto de
        apariciones en el libro.
        """
        palabra = self.entry_palabra.get().strip()
        if palabra == "":
            self.lbl_resultado_busqueda.configure(text="Escribe una palabra.")
            return

        conteo = self.libro.buscar_plb(palabra)
        self.lbl_resultado_busqueda.configure(text=f"Conteo: {conteo:,} veces", text_color="#2c8d2c")

    def abrir_ventana_prestamo(self):
        """
        Abre la ventana para ingresar los datos del lector y realizar el préstamo.
        """
        from prestamoWindow import prestamoWindow  # Importa dinámicamente para evitar dependencias circulares
        
        self.ventana_p = prestamoWindow(self, self.libro)
        self.ventana_p.grab_set()

    def devolver_libro(self):
        """
        Solicita la clave de administrador para procesar la devolución del libro.
        Si es correcta, cambia el estado a Disponible y actualiza la UI.
        """
        # Solicitamos la clave al usuario mediante un diálogo nativo
        dialog = CTkInputDialog(
            text="Ingresa la clave de administrador para registrar la devolución:",
            title="Devolución de Libro"
        )
        
        # Recuperamos la clave
        clave = dialog.get_input()
        
        if clave is not None:
            # Procesamos la devolución usando el Gestor de Préstamos del padre (master/App)
            exito = self.parent.prestamos.procesar_devolucion(self.libro, clave)
            
            if exito:
                # 1. Guardamos la biblioteca con el nuevo estado del libro
                self.parent.biblioteca.guardar()
                
                # 2. Refrescamos la ventana principal para actualizar la tabla
                self.parent.cargar_libros()
                
                # 3. Redibujamos esta ventana para actualizar metadatos y botones
                self.inicializar_interfaz()
                
                # Mostrar mensaje de éxito
                self.parent.label.configure(text_color="black")  # Refresco estético
                print(f"Libro '{self.libro.titulo}' devuelto exitosamente.")
            else:
                # Si la clave fue errónea, alertamos al usuario en consola o interfaz
                CTkMessagebox = None # Manejo de fallo elegante en consola
                print("Error: Clave de administrador incorrecta.")
