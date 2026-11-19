# Interfaz jugador

class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.rol = None 
        self.activo = True
        self.puntaje = 0

    def asignar_rol(self, rol_obj: Rol):
        self.rol = rol_obj

    def ver_su_rol(self, palabra_secreta):
        # Polimorfismo en acción
        return self.rol.mostrar_informacion(palabra_secreta)

    def registrar_pista(self, texto):
        return Pista(texto, self)

    def emitir_voto(self, jugador_objetivo):
        return jugador_objetivo