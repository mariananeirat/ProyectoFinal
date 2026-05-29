import json
import os
from datetime import datetime, timedelta
from .libro import Libro  # Importa la clase Libro desde el módulo hermano

class Usuario:
    """
    Clase que representa a un usuario solicitante de un préstamo.
    Almacena los datos requeridos por el PDF: nombre, correo y número de teléfono.
    """
    def __init__(self, nombre, correo, telefono):
        self.nombre = nombre        
        self.correo = correo        
        self.telefono = telefono  

    def to_dict(self):
        """
        Convierte los datos del usuario a diccionario para la serialización JSON.
        """
        return {
            "Nombre": self.nombre,
            "Correo": self.correo,
            "Teléfono": self.telefono
        }

    @classmethod
    def from_dict(cls, d):
        """
        Crea un objeto Usuario a partir de un diccionario cargado de JSON.
        """
        if not d:
            return None
        return cls(
            nombre=d.get("Nombre", ""),
            correo=d.get("Correo", ""),
            telefono=d.get("Teléfono", "")
        )


class Prestamo:
    """
    Clase que representa una transacción de préstamo de un libro.
    Calcula fechas automáticas de préstamo y de devolución (a 15 días).
    """
    def __init__(self, usuario, libro_titulo, fecha_prestamo=None, fecha_devolucion=None):
        self.usuario = usuario  # Instancia de Usuario
        self.libro_titulo = libro_titulo  # Guardamos el título del libro para relacionarlos

        # Fecha de préstamo (automática si no se proporciona)
        if isinstance(fecha_prestamo, str):
            self.fecha_prestamo = datetime.strptime(fecha_prestamo, "%Y-%m-%d %H:%M:%S")
        elif fecha_prestamo:
            self.fecha_prestamo = fecha_prestamo
        else:
            self.fecha_prestamo = datetime.now()

        # Fecha de devolución automática a 15 días
        if isinstance(fecha_devolucion, str):
            self.fecha_devolucion = datetime.strptime(fecha_devolucion, "%Y-%m-%d %H:%M:%S")
        elif fecha_devolucion:
            self.fecha_devolucion = fecha_devolucion
        else:
            self.fecha_devolucion = self.fecha_prestamo + timedelta(days=15)

    def to_dict(self):
        """
        Convierte el préstamo a diccionario para poder guardarlo en JSON.
        """
        return {
            "usuario": self.usuario.to_dict() if hasattr(self.usuario, "to_dict") else self.usuario,
            "libro_titulo": self.libro_titulo,
            "fecha_prestamo": self.fecha_prestamo.strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_devolucion": self.fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_dict(cls, d):
        """
        Crea un préstamo a partir de los datos en formato diccionario del JSON.
        """
        user_d = d.get("usuario")
        usuario = Usuario.from_dict(user_d) if isinstance(user_d, dict) else user_d
        return cls(
            usuario=usuario,
            libro_titulo=d.get("libro_titulo"),
            fecha_prestamo=d.get("fecha_prestamo"),
            fecha_devolucion=d.get("fecha_devolucion")
        )


class GestorPrestamos:
    """
    Clase encargada de controlar el ciclo de vida de los préstamos,
    incluyendo guardar y cargar en datos/prestamos.json.
    """
    def __init__(self):
        self.prestamos = []

    def cargar_prestamos(self, ruta="datos/prestamos.json"):
        """
        Carga el registro de préstamos desde el archivo JSON local.
        """
        if not os.path.exists(ruta):
            self.prestamos = []
            return
        
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.prestamos = [Prestamo.from_dict(d) for d in datos]
            print(f"Préstamos cargados exitosamente desde {ruta} ({len(self.prestamos)} registros)")
        except Exception as e:
            print(f"Error al cargar los préstamos: {e}")
            self.prestamos = []

    def guardar_prestamos(self, ruta="datos/prestamos.json"):
        """
        Persiste todos los préstamos actuales en el archivo JSON local.
        """
        try:
            directorio = os.path.dirname(ruta)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prestamos], f, ensure_ascii=False, indent=4)
            print(f"Préstamos persistidos exitosamente en {ruta}")
        except Exception as e:
            print(f"Error al guardar los préstamos: {e}")

    def registrar_nuevo_prestamo(self, usuario, libro):
        """
        Crea y registra un nuevo préstamo para un libro, cambiando su estado.
        """
        libro.cambiar_est("Prestado")
        nuevo_p = Prestamo(usuario, libro.titulo)
        self.prestamos.append(nuevo_p)
        self.guardar_prestamos()
        return nuevo_p

    def obtener_prestamo_por_libro(self, libro):
        """
        Busca si hay un préstamo activo relacionado con el libro indicado.
        """
        for p in self.prestamos:
            if p.libro_titulo.lower() == libro.titulo.lower():
                return p
        return None

    def procesar_devolucion(self, libro, clave_admin):
        """
        Devuelve un libro a estado Disponible si se ingresa la clave de administrador correcta.
        Elimina el préstamo activo del registro.
        """
        if clave_admin == "home26":
            # Cambiamos el estado del libro
            libro.cambiar_est("Disponible")
            
            # Buscamos y retiramos el préstamo activo del registro
            prestamo_activo = self.obtener_prestamo_por_libro(libro)
            if prestamo_activo in self.prestamos:
                self.prestamos.remove(prestamo_activo)
            
            # Guardamos los cambios en el archivo JSON
            self.guardar_prestamos()
            print(f"Devolución procesada correctamente para el libro '{libro.titulo}'")
            return True
        else:
            print("Clave de administrador incorrecta.")
            return False
