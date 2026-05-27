from customtkinter import *
from codigo.libro import Libro  # Importa la clase unificada Libro para manejar las descargas

class agregarLibro(CTkToplevel):
    """
    Ventana emergente (Toplevel) para agregar un libro a partir de un enlace.
    Implementa el flujo interactivo: Ingreso -> Descarga y Regex -> Confirmación -> Guardado local.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("AGREGAR LIBRO")
        self.configure(fg_color="#d9dbff")  # Fondo azul claro pastel que combina con la paleta principal
        
        # Tamaño de la ventana
        self.geometry("1000x700")
        self.attributes("-topmost", True)  # Mantener la ventana al frente

        # Configuración de columnas (1 central ancha y 2 laterales estrechas para centrado)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=8)
        self.grid_columnconfigure(2, weight=1)
        
        # Configuración de filas
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=30)
        self.grid_rowconfigure(2, weight=1)

        self.nuevo_libro_cache = None  # Almacenará temporalmente el libro descargado en caché

        self.ventna_anterior()
        self.tabla1()
       
    def ventna_anterior(self):
        """
        Dibuja el botón 'Atrás' en la parte superior y la línea divisoria.
        """
        self.linea1 = CTkFrame(self, height=2, fg_color="#696dc2")
        self.linea1.grid(row=0, columnspan=3, column=0, padx=0, pady=(50,0), sticky="we")
        
        self.devolver = CTkButton(self,
                                    text="Atrás",
                                    fg_color="#1a1c43",
                                    height=40,
                                    corner_radius=5,
                                    command=self.button_callbck)
        self.devolver.grid(row=0, column=0, padx=30, pady=0, sticky="w")
       
    def tabla1(self):
        """
        Dibuja el formulario principal para ingresar el enlace URL de Project Gutenberg.
        """
        # Limpiamos si hay elementos anteriores en la ventana
        if hasattr(self, 'cuadro1'):
            self.cuadro1.destroy()

        self.cuadro1 = CTkFrame(self,
                                   fg_color="#bec1f6",
                                   border_color="#696dc2",
                                   border_width=1,
                                   corner_radius=5)
        self.cuadro1.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        # Configuración del grid interno del cuadro1
        self.cuadro1.grid_columnconfigure(0, weight=1)
        self.cuadro1.grid_rowconfigure(0, weight=1)
        self.cuadro1.grid_rowconfigure(1, weight=1)
        self.cuadro1.grid_rowconfigure(2, weight=1)
        self.cuadro1.grid_rowconfigure(3, weight=1)

        # Título del cuadro
        self.titulo = CTkLabel(self.cuadro1,
                                text="AGREGAR LIBRO",
                                text_color="black",
                                font=("Calibri Light", 30, "bold"),
                                fg_color="transparent")
        self.titulo.grid(row=0, column=0, padx=30, pady=(20, 10), sticky="w")

        # Subtítulo explicativo
        self.label_subtitulo = CTkLabel(self.cuadro1,
                                        text="Ingresa el enlace del libro de Project Gutenberg (.txt)",
                                        text_color="#454ccd",
                                        font=("Calibri Light", 15, "bold"),
                                        fg_color="transparent")
        self.label_subtitulo.grid(row=0, column=0, padx=30, pady=(70, 0), sticky="w")

        # Caja de entrada del enlace
        self.entry_enlace = CTkEntry(self.cuadro1,
                                     placeholder_text="https://www.gutenberg.org/cache/epub/.../pg....txt",
                                     width=700,
                                     height=35,
                                     fg_color="#dbddff",
                                     border_color="#1a1c43")
        self.entry_enlace.grid(row=1, column=0, padx=30, pady=(10, 0), sticky="nw")
        
        # Etiqueta para mostrar estados/errores de la descarga
        self.label_estado = CTkLabel(self.cuadro1,
                                     text="",
                                     text_color="red",
                                     font=("Calibri Light", 14, "bold"),
                                     fg_color="transparent")
        self.label_estado.grid(row=2, column=0, padx=30, pady=5, sticky="w")

        # Botón para descargar e iniciar el análisis
        self.boton_agregar = CTkButton(self.cuadro1,
                                     text="Descargar y Analizar",
                                     fg_color="#1a1c43",
                                     height=40,
                                     corner_radius=5,
                                     command=self.descargar_y_procesar_libro)
        self.boton_agregar.grid(row=3, column=0, padx=30, pady=(0, 20), sticky="nw")

    def descargar_y_procesar_libro(self):
        """
        Descarga el libro de la URL indicada y extrae sus metadatos.
        Si tiene éxito, redirige a la pantalla de confirmación.
        """
        enlace = self.entry_enlace.get().strip()
        if enlace == "" or not enlace.startswith("http"):
            self.label_estado.configure(text="Por favor, ingresa un enlace HTTP válido de Project Gutenberg.", text_color="red")
            return

        self.label_estado.configure(text="Descargando y analizando el libro... Por favor espera.", text_color="#1a1c43")
        self.update()  # Forzar actualización de la interfaz gráfica

        try:
            # Creamos una instancia de Libro, la cual descarga y parsea automáticamente el texto
            nuevo_libro = Libro(enlace=enlace)
            self.nuevo_libro_cache = nuevo_libro
            
            # Si se descargó correctamente, mostramos la pantalla de confirmación
            self.guardar_si_no()
        except Exception as e:
            self.label_estado.configure(text=f"Error al descargar o procesar el libro. Verifica el enlace. Detalle: {e}", text_color="red")
            print(f"Error en descargar_y_procesar_libro: {e}")

    def guardar_si_no(self):
        """
        Dibuja la pantalla de confirmación mostrando los metadatos extraídos
        y consultando al usuario si desea guardar el libro en la biblioteca.
        """
        # Limpiamos el cuadro para dibujar la confirmación
        for widget in self.cuadro1.winfo_children():
            widget.destroy()

        self.cuadro1.grid_rowconfigure(0, weight=1)
        self.cuadro1.grid_rowconfigure(1, weight=4)
        self.cuadro1.grid_rowconfigure(2, weight=1)
        self.cuadro1.grid_rowconfigure(3, weight=1)

        # Título de confirmación
        self.titulo_conf = CTkLabel(self.cuadro1,
                                    text="¿Deseas guardar este libro en la biblioteca?",
                                    text_color="black",
                                    font=("Calibri Light", 24, "bold"),
                                    fg_color="transparent")
        self.titulo_conf.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="w")

        # Contenedor para mostrar los metadatos extraídos
        self.meta_frame = CTkFrame(self.cuadro1, fg_color="#dbddff", corner_radius=5)
        self.meta_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        
        self.meta_frame.grid_columnconfigure(0, weight=1)
        self.meta_frame.grid_columnconfigure(1, weight=4)

        # Mostrar metadatos detallados
        labels = [
            ("Título:", self.nuevo_libro_cache.titulo),
            ("Autor:", self.nuevo_libro_cache.autor),
            ("Idioma:", self.nuevo_libro_cache.idioma),
            ("Fecha de Publicación:", self.nuevo_libro_cache.release_date),
            ("Enlace de Origen:", self.nuevo_libro_cache.enlace)
        ]

        for idx, (label_text, value_text) in enumerate(labels):
            lbl_tit = CTkLabel(self.meta_frame, text=label_text, text_color="#1a1c43", font=("Calibri Light", 14, "bold"))
            lbl_tit.grid(row=idx, column=0, padx=15, pady=8, sticky="w")
            
            lbl_val = CTkLabel(self.meta_frame, text=value_text, text_color="black", font=("Calibri Light", 14), justify="left", wraplength=550)
            lbl_val.grid(row=idx, column=1, padx=15, pady=8, sticky="w")

        # Botón de confirmación "Sí, guardar"
        self.boton_guardar = CTkButton(self.cuadro1,
                                     text="Sí, guardar libro",
                                     fg_color="#2c8d2c",  # Color verde para éxito
                                     hover_color="#1e641e",
                                     height=40,
                                     corner_radius=5,
                                     command=self.guardar_libro_confirmado)
        self.boton_guardar.grid(row=2, column=0, padx=30, pady=5, sticky="w")

        # Botón de cancelación "No, volver a intentar"
        self.boton_no_guardar = CTkButton(self.cuadro1,
                                     text="No, intentar con otro enlace",
                                     fg_color="#c82333",  # Color rojo para cancelación
                                     hover_color="#9c1c28",
                                     height=40,
                                     corner_radius=5,
                                     command=self.tabla1)
        self.boton_no_guardar.grid(row=2, column=0, padx=(200, 0), pady=5, sticky="w")

        self.lift()
        self.focus_force()

    def guardar_libro_confirmado(self):
        """
        Flujo de guardado definitivo: guarda el archivo .txt local,
        lo incorpora a la biblioteca, persiste los datos en JSON y refresca la app.
        """
        try:
            # 1. Guardar el archivo .txt del libro localmente
            self.nuevo_libro_cache.guardar_archivo_local()

            # 2. Agregar a la biblioteca cargada en el Master (App)
            self.master.biblioteca.agregar_libro(self.nuevo_libro_cache)

            # 3. Persistir la biblioteca actualizada en datos/libros.json
            self.master.biblioteca.guardar()

            # 4. Mostrar pantalla de confirmación exitosa
            self.confirmación()
            
            # 5. Refrescar la tabla en la ventana principal del master
            self.master.cargar_libros()

        except Exception as e:
            # Si ocurre algún error inesperado al guardar
            print(f"Error al guardar el libro: {e}")

    def confirmación(self):
        """
        Dibuja la pantalla de confirmación de éxito tras agregar el libro.
        """
        for widget in self.cuadro1.winfo_children():
            widget.destroy()

        self.cuadro1.grid_rowconfigure(0, weight=1)
        self.cuadro1.grid_rowconfigure(1, weight=1)

        self.confirmacion_label = CTkLabel(self.cuadro1,
                                            text="¡Libro Agregado Exitosamente!",
                                            text_color="#2c8d2c",
                                            font=("Calibri Light", 28, "bold"),
                                            fg_color="transparent")
        self.confirmacion_label.grid(row=0, column=0, padx=30, pady=(50, 10), sticky="s")

        self.info_lbl = CTkLabel(self.cuadro1,
                                 text=f"El libro '{self.nuevo_libro_cache.titulo}' ya forma parte del catálogo local.",
                                 text_color="black",
                                 font=("Calibri Light", 16),
                                 fg_color="transparent")
        self.info_lbl.grid(row=1, column=0, padx=30, pady=10, sticky="n")

        self.boton_cerrar = CTkButton(self.cuadro1,
                                     text="Entendido",
                                     fg_color="#1a1c43",
                                     height=40,
                                     corner_radius=5,
                                     command=self.button_callbck)
        self.boton_cerrar.grid(row=1, column=0, padx=30, pady=(80, 20), sticky="n")

    def button_callbck(self):
        """
        Cierra la ventana actual de adición de libros.
        """
        self.destroy()