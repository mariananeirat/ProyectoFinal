import json   # Librería para guardar y cargar datos en formato JSON (formato de texto tipo diccionario)
import os     # Librería para trabajar con carpetas y archivos del sistema de archivos
from .libro import Libro  # Importa la clase Libro desde el módulo hermano libro.py

class Biblioteca:
    """
    Clase encargada de gestionar el catálogo completo de libros.
    Permite agregar, buscar, listar disponibles/prestados y persistir en JSON.
    """

    def __init__(self):
        """
        Inicializa una biblioteca con una lista vacía de libros.
        """
        self.libros = []

    def agregar_libro(self, libro):
        """
        Agrega un nuevo objeto Libro a la lista del catálogo de la biblioteca.
        """
        self.libros.append(libro)

    def buscar_por_titulo(self, titulo):
        """
        Busca libros cuyo título contenga la palabra clave provista.
        Ignora diferencias entre mayúsculas y minúsculas.
        """
        resultados = []
        for libro in self.libros:
            if titulo.lower() in libro.titulo.lower():
                resultados.append(libro)
        return resultados
    
    def buscar_por_autor(self, autor):
        """
        Busca libros cuyo autor contenga el nombre provisto.
        Ignora diferencias entre mayúsculas y minúsculas.
        """
        resultados = []
        for libro in self.libros:
            if autor.lower() in libro.autor.lower():
                resultados.append(libro)
        return resultados
    
    def libros_disponibles(self):
        """
        Retorna una lista con todos los libros que tienen estado 'Disponible'.
        """
        resultados = []
        for libro in self.libros:
            if libro.estado == "Disponible":
                resultados.append(libro)
        return resultados
    
    def libros_prestados(self):
        """
        Retorna una lista con todos los libros que tienen estado 'Prestado'.
        """
        resultados = []
        for libro in self.libros:
            if libro.estado == "Prestado":
                 resultados.append(libro)
        return resultados

    def guardar(self, ruta="datos/libros.json"):
        """
        Guarda el estado actual del catálogo en un archivo local en formato JSON.
        Crea la carpeta 'datos' automáticamente si no existe.
        """
        try:
            # Obtiene la ruta absoluta o relativa correcta
            directorio = os.path.dirname(ruta)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            
            # Abre el archivo para escritura con codificación UTF-8
            with open(ruta, "w", encoding="utf-8") as f:
                # Convierte cada objeto Libro en diccionario mediante to_dict()
                json.dump([libro.to_dict() for libro in self.libros], f, ensure_ascii=False, indent=4)
            print(f"Biblioteca guardada exitosamente en {ruta}")
        except Exception as e:
            print(f"Error al guardar la biblioteca en '{ruta}': {e}")

    def cargar(self, ruta="datos/libros.json"):
        """
        Carga el catálogo de libros desde el archivo JSON especificado.
        Si el archivo no existe, simplemente finaliza sin hacer nada.
        """
        if not os.path.exists(ruta):
            print(f"El archivo de datos '{ruta}' no existe. Se inicia catálogo vacío.")
            self.libros = []
            return
        
        try:
            # Abre el archivo en modo lectura
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            
            # Convierte cada diccionario cargado de nuevo a un objeto Libro
            self.libros = [Libro.from_dict(d) for d in datos]
            print(f"Biblioteca cargada exitosamente desde {ruta} ({len(self.libros)} libros)")
        except Exception as e:
            print(f"Error al cargar la biblioteca desde '{ruta}': {e}")
            self.libros = []
