from customtkinter import *
from agregarLibro import agregarLibro  # Importa la ventana para agregar libros
from info_libro import info_libro        # Importa la ventana de información detallada
from codigo.biblio import Biblioteca     # Importa la clase gestora del catálogo
from codigo.usuario import GestorPrestamos  # Importa el gestor para préstamo de libros

class App(CTk):
    """
    Ventana principal de la aplicación Biblioteca Gutenberg.
    Permite visualizar el catálogo, buscar por título/autor, e iniciar los flujos
    de agregar libros, préstamos y devoluciones.
    """
    def __init__(self):
        super().__init__()

        # Instanciamos los gestores lógicos de biblioteca y préstamos
        self.biblioteca = Biblioteca()
        self.prestamos = GestorPrestamos()
        
        self.toplevel_window = None

        self.title("BIBLIOTECA DIGITAL")
        self.configure(fg_color="#d9dbff")  # Fondo azul claro pastel

        # Obtener dimensiones de pantalla y maximizar ventana
        self.screenwidth = self.winfo_screenwidth()
        self.screenheight = self.winfo_screenheight()
        self.geometry(f"{self.screenwidth}x{self.screenheight}+0+0")

        # Configuración del grid principal (3 columnas con peso para centrado)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=9)
        self.grid_columnconfigure(2, weight=2)
        
        # Configuración del grid principal (5 filas)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=6)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(3, weight=10)
        self.grid_rowconfigure(4, weight=4)

        # Título principal de la aplicación
        Titulo = "BIBLIOTECA DIGITAL"
        subtitulo = "Explora el inventario de la biblioteca"
        self.label = CTkLabel(self, 
                              text=Titulo,
                              text_color="black",
                              font=("Calibri Light", 30, "bold"),
                              fg_color="transparent")
        self.label.grid(row=0, column=0, padx=100, pady=0, sticky="w")

        # Subtítulo secundario
        self.subtitulo = CTkLabel(self, 
                              text=subtitulo,
                              text_color="#454ccd",
                              font=("Calibri Light", 15, "bold"),
                              fg_color="transparent")
        self.subtitulo.grid(row=0, column=0, padx=100, pady=(50,0), sticky="w")

        # Botón para abrir la ventana de agregar libro
        self.button2 = CTkButton(self,
                                text="Agregar libro",
                                fg_color="#1a1c43",
                                hover_color="#2c2f6d",
                                font=("Calibri Light", 14, "bold"),
                                height=40,
                                corner_radius=5,
                                command=self.button2_callbck)
        self.button2.grid(row=0, column=2, padx=(10,50), pady=(10,5), sticky="w")

        # Campo de entrada para el buscador de libros
        self.entry = CTkEntry(self,
                            placeholder_text="Buscar libro por título o autor...",
                            width=700,
                            fg_color="#ffffff",
                            border_color="#1a1c43",
                            height=35,
                            font=("Calibri Light", 13))
        self.entry.grid(row=0, column=0, padx=100, pady=(120,0), sticky="w")

        # Botón para disparar la búsqueda de libros
        self.button_buscar = CTkButton(self,
                                       text="Buscar",
                                       fg_color="#1a1c43",
                                       hover_color="#2c2f6d",
                                       font=("Calibri Light", 14, "bold"),
                                       height=40,
                                       corner_radius=5,
                                       command=self.buscar_libro)
        self.button_buscar.grid(row=0, column=1, padx=20, pady=(120,0), sticky="w")

        # Línea divisoria decorativa
        self.linea1 = CTkFrame(self,
                               height=2,
                               fg_color="#696dc2")
        self.linea1.grid(row=0, columnspan=2, column=0, padx=(100,0), pady=(210,0), sticky="we")

        # Construir la estructura de la tabla e iniciar carga de datos
        self.tabla()
        self.subir_libros()

    def tabla(self):
        """
        Crea el marco contenedor scrollable para la tabla de libros.
        Configura los nombres de las cabeceras.
        """
        if hasattr(self, 'book_table'):
            self.book_table.destroy()

        self.book_table = CTkScrollableFrame(self,
                                            fg_color="#bec1f6",
                                            border_color="#696dc2",
                                            border_width=1,
                                            corner_radius=5)
        self.book_table.grid(row=1, column=0, columnspan=2, padx=(100,0), pady=(0,0), sticky="nswe")

        self.book_table.grid_columnconfigure(0, weight=4)
        self.book_table.grid_columnconfigure(1, weight=3)
        self.book_table.grid_columnconfigure(2, weight=2)        
        self.book_table.grid_columnconfigure(3, weight=2)  

        # Nombres de las cabeceras de la tabla
        cabecera = ["Título", "Autor", "Estado", "Más"]
        for x in range(4):
            self.descripcion = CTkLabel(self.book_table, 
                                text=cabecera[x],
                                text_color="black",
                                font=("Calibri Light", 20, "bold"),
                                fg_color="transparent")
            self.descripcion.grid(row=0, column=x, padx=10, pady=5, sticky="w")

    def subir_libros(self):
        """
        Carga la biblioteca y préstamos de disco, sincroniza estados
        y puebla la tabla en pantalla.
        """
        # Carga la base de datos de libros
        self.biblioteca.cargar() 
        # Carga la base de datos de préstamos activos
        self.prestamos.cargar_prestamos()
        
        # Sincroniza el estado de cada libro según los préstamos activos
        for libro in self.biblioteca.libros:
            prestamo = self.prestamos.obtener_prestamo_por_libro(libro)
            if prestamo:
                libro.estado = "Prestado"
            else:
                libro.estado = "Disponible"

        # Puebla la tabla con la lista cargada
        self.poblar_tabla(self.biblioteca.libros)

    def poblar_tabla(self, lista_libros=None):
        """
        Llena dinámicamente la tabla con los libros proporcionados en la lista.
        """
        if lista_libros is None:
            lista_libros = self.biblioteca.libros

        # Destruimos los elementos anteriores de filas inferiores a la cabecera
        for L in self.book_table.winfo_children():
            info = L.grid_info()
            if 'row' in info and int(info['row']) > 0:
                L.destroy()

        # Insertamos cada libro en una fila nueva
        for i, libro in enumerate(lista_libros):
            fila = i + 1 

            self.titulo_libro = CTkLabel(self.book_table,
                                text=libro.titulo,
                                text_color="black",
                                font=("Calibri Light", 15),
                                fg_color="transparent")
            self.titulo_libro.grid(row=fila, column=0, padx=10, pady=5, sticky="w")
            
            self.autor_libro = CTkLabel(self.book_table,
                                text=libro.autor,
                                text_color="black",
                                font=("Calibri Light", 15),
                                fg_color="transparent")
            self.autor_libro.grid(row=fila, column=1, padx=10, pady=5, sticky="w")
            
            # Color verde para Disponible y rojo para Prestado
            color_estado = "#2c8d2c" if libro.estado == "Disponible" else "#a01b1b"
            self.estado_libro = CTkLabel(self.book_table,
                                text=libro.estado,
                                text_color=color_estado,
                                font=("Calibri Light", 15, "bold"),
                                fg_color="transparent")
            self.estado_libro.grid(row=fila, column=2, padx=10, pady=5, sticky="w")

            texto_boton = "Más información"
            self.mas_info = CTkButton(self.book_table,
                                text=texto_boton,
                                text_color="white",
                                font=("Calibri Light", 13, "bold"),
                                fg_color="#1a1c43",
                                hover_color="#2c2f6d",
                                height=28,
                                command=lambda lib=libro: self.mas_info_callback(lib))  # Usamos lambda para pasar el objeto libro correcto
            self.mas_info.grid(row=fila, column=3, padx=10, pady=5, sticky="w")

    def cargar_libros(self):
        """
        Busca libros según el criterio de búsqueda (Título o Autor) ingresado,
        y actualiza la visualización de la tabla.
        """
        criterio = self.entry.get().strip().lower()
        if criterio != "":
            # Filtramos coincidencia en título o en autor
            libros_filtrados = []
            for libro in self.biblioteca.libros:
                if criterio in libro.titulo.lower() or criterio in libro.autor.lower():
                    libros_filtrados.append(libro)
            self.poblar_tabla(libros_filtrados)
        else:
            # Si la barra está vacía, muestra todo el catálogo
            self.poblar_tabla(self.biblioteca.libros)

    def buscar_libro(self):
        """
        Callback que se dispara al presionar el botón 'Buscar'.
        """
        self.cargar_libros()
        
    def mas_info_callback(self, libro):
        """
        Abre la ventana emergente de detalles pasando el libro seleccionado.
        """
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = info_libro(self, libro)
            self.toplevel_window.grab_set() 
        else:
            # Cerramos ventana anterior para evitar duplicaciones molestas
            self.toplevel_window.destroy()
            self.toplevel_window = info_libro(self, libro)
            self.toplevel_window.grab_set()

    def button2_callbck(self):
        """
        Abre la ventana emergente para agregar un libro nuevo a partir de un enlace.
        """
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = agregarLibro(self)   
            self.toplevel_window.grab_set() 
        else:
            self.toplevel_window.destroy()
            self.toplevel_window = agregarLibro(self)
            self.toplevel_window.grab_set()

# Inicialización directa del bucle principal
if __name__ == "__main__":
    app = App()
    app.mainloop()