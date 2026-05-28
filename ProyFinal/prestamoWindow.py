from customtkinter import *
from codigo.usuario import Usuario  # Importamos la clase Usuario para instanciar los lectores

class prestamoWindow(CTkToplevel):
    """
    Ventana emergente (Toplevel) para capturar los datos del lector (Nombre, Correo, Teléfono)
    y registrar el préstamo de un libro seleccionado.
    """
    def __init__(self, parent, libro, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent  # Instancia de la ventana de detalles (info_libro)
        self.libro = libro    # Objeto Libro que se va a prestar

        self.title("REGISTRAR PRÉSTAMO")
        self.configure(fg_color="#d9dbff")  # Fondo azul claro pastel

        # Tamaño centrado y adecuado
        self.geometry("650x500")
        self.attributes("-topmost", True)  # Mantener al frente

        # Centrar los elementos de la cuadrícula
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=6)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_rowconfigure(2, weight=1)

        self.inicializar_ventana()

    def inicializar_ventana(self):
        """
        Dibuja los componentes visuales en la ventana de préstamo.
        """
        # Contenedor principal con bordes pulidos
        self.cuadro_prestamo = CTkFrame(self,
                                        fg_color="#bec1f6",
                                        border_color="#696dc2",
                                        border_width=1,
                                        corner_radius=5)
        self.cuadro_prestamo.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        self.cuadro_prestamo.grid_columnconfigure(0, weight=1)
        self.cuadro_prestamo.grid_columnconfigure(1, weight=2)

        # Título interno
        self.lbl_titulo = CTkLabel(self.cuadro_prestamo,
                                   text="FORMULARIO DE PRÉSTAMO",
                                   text_color="black",
                                   font=("Calibri Light", 22, "bold"))
        self.lbl_titulo.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Mensaje del libro
        self.lbl_sub = CTkLabel(self.cuadro_prestamo,
                                text=f"Registrando préstamo de: '{self.libro.titulo}'",
                                text_color="#1a1c43",
                                font=("Calibri Light", 13, "bold"),
                                wraplength=480,
                                justify="left")
        self.lbl_sub.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")

        # Campo: Nombre Completo
        self.lbl_nom = CTkLabel(self.cuadro_prestamo,
                                text="Nombre Completo:",
                                text_color="black",
                                font=("Calibri Light", 14, "bold"))
        self.lbl_nom.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.entry_nombre = CTkEntry(self.cuadro_prestamo,
                                    placeholder_text=" ",
                                    fg_color="white",
                                    border_color="#1a1c43",
                                    width=280)
        self.entry_nombre.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # Campo: Correo Electrónico
        self.lbl_cor = CTkLabel(self.cuadro_prestamo,
                                text="Correo Electrónico:", 
                                text_color="black", 
                                font=("Calibri Light", 14, "bold"))
        self.lbl_cor.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.entry_correo = CTkEntry(self.cuadro_prestamo, 
                                     placeholder_text=" ...@correo.com", 
                                     fg_color="white", 
                                     border_color="#1a1c43", 
                                     width=280)
        self.entry_correo.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        # Campo: Número de Teléfono
        self.lbl_tel = CTkLabel(self.cuadro_prestamo, 
                                text="Número Telefónico:", 
                                text_color="black", 
                                font=("Calibri Light", 14, "bold"))
        self.lbl_tel.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        self.entry_telefono = CTkEntry(self.cuadro_prestamo, 
                                       placeholder_text=" ", 
                                       fg_color="white", 
                                       border_color="#1a1c43", 
                                       width=280)
        self.entry_telefono.grid(row=4, column=1, padx=20, pady=10, sticky="w")

        # Etiqueta de aviso de error
        self.lbl_error = CTkLabel(self.cuadro_prestamo, 
                                  text="", 
                                  text_color="red", 
                                  font=("Calibri Light", 12, "bold"))
        self.lbl_error.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="w")

        # Botones de Acción
        self.btn_confirmar = CTkButton(self.cuadro_prestamo,
                                       text="Confirmar Préstamo",
                                       fg_color="#2c8d2c",
                                       hover_color="#1e641e",
                                       font=("Calibri Light", 14, "bold"),
                                       height=35,
                                       command=self.confirmar_prestamo)
        self.btn_confirmar.grid(row=6, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")

        self.btn_cancelar = CTkButton(self.cuadro_prestamo,
                                      text="Cancelar",
                                      fg_color="#1a1c43",
                                      hover_color="#272a63",
                                      font=("Calibri Light", 14),
                                      height=35,
                                      command=self.destroy)
        self.btn_cancelar.grid(row=6, column=1, padx=(170, 20), pady=(10, 5), sticky="w")

    def confirmar_prestamo(self):
        """
        Lee y valida los campos ingresados.
        Si son correctos, registra el préstamo en el Gestor de Préstamos,
        guarda la biblioteca, refresca las ventanas y se cierra.
        """
        nombre = self.entry_nombre.get().strip()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()

        # Validación básica de datos obligatorios
        if nombre == "" or correo == "" or telefono == "":
            self.lbl_error.configure(text="Datos incompletos, completa todos los campos del lector.")
            return

        try:
            # 1. Creamos el objeto Usuario correspondiente al lector
            lector = Usuario(nombre=nombre, correo=correo, telefono=telefono)

            # 2. Registramos el préstamo a través del Gestor de Préstamos de la app principal (master/App)
            # parent (info_libro) -> parent (App) -> prestamos
            self.parent.parent.prestamos.registrar_nuevo_prestamo(usuario=lector, libro=self.libro)

            # 3. Guardamos los cambios de estado en la biblioteca local en JSON
            self.parent.parent.biblioteca.guardar()

            # 4. Refrescamos la tabla principal de la aplicación principal
            self.parent.parent.cargar_libros()

            # 5. Refrescamos la ventana de detalles para mostrar el nuevo estado y los datos del préstamo
            self.parent.inicializar_interfaz()

            print(f"Préstamo del libro '{self.libro.titulo}' registrado exitosamente a nombre de {nombre}.")
            
            # Cerrar la ventana actual
            self.destroy()

        except Exception as e:
            self.lbl_error.configure(text=f"Error al registrar préstamo: {e}")
            print(f"Error en confirmar_prestamo: {e}")
