import re                           # Importa expresiones regulares para buscar patrones en el texto (regex)
import requests                     # Importa la librería para hacer solicitudes HTTP y descargar el libro
import os                           # Para interactuar con archivos y carpetas del sistema
import math                         # Importa matemáticas para el redondeo hacia arriba

class Libro:
    """
    Clase que representa un libro digital de la biblioteca.
    Maneja sus metadatos, su texto y los análisis sobre su contenido.
    """

    def __init__(self, enlace=None, titulo=None, autor=None, idioma=None, release_date=None, ruta_local=None, estado="Disponible"):
        """
        Inicializa un objeto Libro. Puede inicializarse de dos formas:
        1. Proporcionando un enlace de descarga (para un libro nuevo).
        2. Proporcionando metadatos explícitos (al cargar desde JSON).
        """
        self.enlace = enlace
        self.estado = estado     # Puede ser "Disponible" o "Prestado"
        self._texto_cache = None # Guardará el contenido del libro en memoria
        
        if titulo is not None:
            # Caso 1: Inicialización con metadatos explícitos (desde la persistencia de datos)
            self.titulo = titulo
            self.autor = autor if autor is not None else "Autor Desconocido"
            self.idioma = idioma if idioma is not None else "Idioma Desconocido"
            self.release_date = release_date if release_date is not None else "Fecha Desconocida"
            self.ruta_local = ruta_local
        else:
            # Caso 2: Inicialización por primera vez desde un enlace URL de Project Gutenberg
            self.titulo = "Descargando..."
            self.autor = "Descargando..."
            self.idioma = "Descargando..."
            self.release_date = "Descargando..."
            self.ruta_local = None
            
            # Descargamos el libro y extraemos sus metadatos
            if self.enlace:
                self.crear_libro()

    def crear_libro(self):
        """
        Accede al enlace URL del libro, descarga su contenido y extrae los
        metadatos principales mediante expresiones regulares.
        """
        try:
            # Realizamos la petición HTTP GET para obtener el libro
            req = requests.get(self.enlace, timeout=10)
            if req.status_code == 200:
                texto = req.text
                self._texto_cache = texto  # Guardamos el texto en memoria
                
                # Expresión regular para el título (Title:)
                match_titulo = re.search(r'Title:\s*(.+)', texto)
                if match_titulo:
                    # Capturamos la primera línea del título y limpiamos espacios y retornos
                    self.titulo = match_titulo.group(1).split('\r')[0].split('\n')[0].strip()
                else:
                    self.titulo = "Título Desconocido"

                # Expresión regular para el autor (Author:)
                match_autor = re.search(r'Author:\s*(.+)', texto)
                if match_autor:
                    self.autor = match_autor.group(1).split('\r')[0].split('\n')[0].strip()
                else:
                    self.autor = "Autor Desconocido"

                # Expresión regular para el idioma (Language:)
                match_idioma = re.search(r'Language:\s*(.+)', texto)
                if match_idioma:
                    self.idioma = match_idioma.group(1).split('\r')[0].split('\n')[0].strip()
                else:
                    self.idioma = "Idioma Desconocido"

                # Expresión regular para la fecha de lanzamiento (Release date:)
                match_fecha = re.search(r'Release date:\s*(.+)', texto)
                if match_fecha:
                    fecha_s = match_fecha.group(1).split('\r')[0].split('\n')[0].strip()
                    # Si tiene un corchete explicativo como [eBook #XXXX], lo retiramos
                    if '[' in fecha_s:
                        fecha_s = fecha_s.split('[')[0].strip()
                    self.release_date = fecha_s
                else:
                    self.release_date = "Fecha Desconocida"

                print(f"Libro descargado en caché exitosamente: '{self.titulo}'")
            else:
                raise Exception(f"Código de estado HTTP: {req.status_code}")
        except Exception as e:
            print(f"Error al descargar/procesar el enlace '{self.enlace}': {e}")
            raise e

    def guardar_archivo_local(self, carpeta_destino="libros"):
        """
        Guarda el texto descargado en un archivo local .txt en la carpeta destino.
        Retorna la ruta relativa final del archivo guardado.
        """
        # Si no hay texto en caché, intentamos descargarlo primero
        if not self._texto_cache and self.enlace:
            self.crear_libro()

        if not self._texto_cache:
            raise Exception("No hay texto cargado para guardar localmente.")

        # Creamos la carpeta de destino si no existe
        os.makedirs(carpeta_destino, exist_ok=True)

        # Limpiamos el título para generar un nombre de archivo válido
        titulo_limpio = "".join(c for c in self.titulo if c.isalnum() or c in (' ', '_', '-')).rstrip()
        titulo_limpio = titulo_limpio.replace(' ', '_')
        if not titulo_limpio:
            titulo_limpio = "libro_descargado"

        # Nombre y ruta final del archivo
        nombre_archivo = f"{titulo_limpio}.txt"
        self.ruta_local = os.path.join(carpeta_destino, nombre_archivo)

        # Escribimos el contenido del archivo con codificación UTF-8
        with open(self.ruta_local, "w", encoding="utf-8") as f:
            f.write(self._texto_cache)

        print(f"Archivo guardado localmente en: {self.ruta_local}")
        return self.ruta_local

    def obtener_texto(self):
        """
        Lee el contenido del libro desde el archivo de texto local (.txt).
        Usa caché en memoria para acelerar lecturas posteriores.
        """
        if self._texto_cache is not None:
            # Retorna el texto almacenado en memoria si ya fue leído antes
            return self._texto_cache
        
        if not self.ruta_local or not os.path.exists(self.ruta_local):
            return ""
        
        try:
            # Intentamos leer con codificación UTF-8
            with open(self.ruta_local, "r", encoding="utf-8") as f:
                self._texto_cache = f.read()
        except FileNotFoundError:
            self._texto_cache = ""
        except UnicodeDecodeError:
            try:
                # Intento de respaldo con la codificación de windows por si acaso
                with open(self.ruta_local, "r", encoding="latin-1") as f:
                    self._texto_cache = f.read()
            except Exception:
                self._texto_cache = ""
        return self._texto_cache

    def obtener_plbs(self):
        """
        Extrae todas las palabras del texto en una lista en minúsculas,
        omitiendo puntuaciones y números.
        """
        texto = self.obtener_texto()
        if not texto:
            return []
        
        # Filtramos caracteres alfabéticos válidos usando expresiones regulares
        plbs = re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚüÜÑñ]+', texto)
        return [p.lower() for p in plbs]

    def contar_plbs(self):
        """
        Retorna la cantidad total de palabras en el libro.
        """
        return len(self.obtener_plbs())

    def estimar_pags(self):
        """
        Estima las páginas del libro basándose en la fórmula obligatoria del PDF:
        Páginas estimadas = techo(total de palabras / 300)
        """
        total = self.contar_plbs()
        if total == 0:
            return 0
        return math.ceil(total / 300)

    def obtener_preview(self):
        """
        Retorna una vista previa compuesta por las primeras 2 páginas estimadas,
        equivalente a las primeras 600 palabras del texto.
        """
        plbs = self.obtener_plbs()
        # Tomamos las primeras 600 palabras del libro
        primeras_600 = plbs[:600]
        return " ".join(primeras_600) + ("..." if len(plbs) > 600 else "")

    def plbs_mas_repetidas(self, cantidad=10):
        """
        Encuentra las palabras más repetidas en el libro, excluyendo las palabras
        más comunes de la lista stopwords (español e inglés).
        """
        # Definición de stopwords (artículos, preposiciones y conectores)
        stopwords = {
            'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra', 'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 
            'el', 'ella', 'ellos', 'en', 'entre', 'es', 'esa', 'ese', 'eso', 'esta', 'estaba', 'estado', 'estoy', 'fue', 'ha', 'había', 'han', 
            'has', 'hasta', 'hay', 'la', 'las', 'le', 'les', 'lo', 'los', 'me', 'mi', 'mis', 'mucho', 'muy', 'más', 'nada', 'ni', 'no', 'nos', 
            'nuestro', 'o', 'para', 'pero', 'por', 'que', 'se', 'ser', 'si', 'sin', 'sobre', 'su', 'sus', 'también', 'te', 'tener', 'tengo', 
            'tu', 'un', 'una', 'y', 'ya', 'yo', 'él', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 
            'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did', 'do', 
            'does', 'doing', 'down', 'each', 'few', 'for', 'from', 'further', 'had', 'have', 'having', 'he', 'her', 'here', 
            'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'into', 'is', 'it', 'its', 'itself', 'just', 'more', 'most', 
            'my', 'myself', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 
            'own', 's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 
            'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 
            'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'you', 'your', 'yours', 'yourself', 'yourselves'
        }
        
        plbs = self.obtener_plbs()
        if not plbs:
            return []
        
        frecuencia = {}
        # Contamos la frecuencia de cada palabra que no sea una stopword
        for plb in plbs:
            if plb in stopwords:
                continue
            if plb in frecuencia:
                frecuencia[plb] += 1
            else:
                frecuencia[plb] = 1
                
        # Ordenamos las palabras por su frecuencia de mayor a menor
        orden = sorted(frecuencia.items(), key=lambda par: par[1], reverse=True)
        return orden[:cantidad]

    def buscar_plb(self, plb_buscar):
        """
        Cuenta cuántas veces aparece una palabra específica en el texto.
        """
        if not plb_buscar:
            return 0
        
        plbs = self.obtener_plbs()
        busqueda = plb_buscar.lower().strip()
        contador = 0
        
        # Recorremos la lista de palabras para contar las coincidencias exactas
        for plb in plbs:
            if plb == busqueda:
                contador += 1
        return contador

    def cambiar_est(self, nuevo_estado):
        """
        Cambia el estado del libro (debe ser 'Disponible' o 'Prestado').
        """
        if nuevo_estado not in ("Disponible", "Prestado"):
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        self.estado = nuevo_estado

    def to_dict(self):
        """
        Convierte el objeto Libro a un diccionario de Python.
        Facilita la serialización a formato JSON.
        """
        return {
            "Título": self.titulo,
            "Autor": self.autor,
            "Idioma": self.idioma,
            "release_date": self.release_date,
            "enlace": self.enlace,
            "Ruta_local": self.ruta_local,
            "Estado": self.estado
        }

    @classmethod
    def from_dict(cls, d):
        """
        Crea un objeto Libro a partir de un diccionario.
        Facilita la deserialización desde formato JSON.
        """
        return cls(
            enlace=d.get("enlace"),
            titulo=d.get("Título"),
            autor=d.get("Autor"),
            idioma=d.get("Idioma"),
            release_date=d.get("release_date"),
            ruta_local=d.get("Ruta_local"),
            estado=d.get("Estado", "Disponible")
        )