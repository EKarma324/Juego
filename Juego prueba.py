#interfaz rol
from abc import ABC, abstractmethod
import random



class Rol(ABC):
    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def mostrar_informacion(self, palabra_secreta):
        "Método abstracto que redefinirá cada subclase (Polimorfismo)"
        pass

class Civil(Rol):
    def __init__(self):
        super().__init__("Civil")

    def mostrar_informacion(self, palabra_secreta):
        return f"Tu rol es Civil. La palabra secreta es: '{palabra_secreta}'"

class Impostor(Rol):
    def __init__(self):
        super().__init__("Impostor")

    def mostrar_informacion(self, palabra_secreta):
        return "¡Eres el IMPOSTOR! No conoces la palabra secreta, debes disimular."

class Configuracion:
    def __init__(self, num_rondas=3, tiempo_debate=60, categoria="Animales", ultima_oportunidad=True, max_longitud_pista=50):
        self.num_rondas = num_rondas
        self.tiempo_debate = tiempo_debate
        self.categoria_seleccionada = categoria
        self.opcion_ultima_oportunidad = ultima_oportunidad
        self.max_longitud_pista = max_longitud_pista


class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.rol = None  
        self.activo = True
        self.puntaje = 0
        

    def asignar_rol(self, rol_obj: Rol):
        self.rol = rol_obj

    def ver_su_rol(self, palabra_secreta):
        return self.rol.mostrar_informacion(palabra_secreta)
    
    def registrar_pista(self, texto):
        return Pista(texto, self)

    def emitir_voto(self, jugador_objetivo):
        return jugador_objetivo

class Configuracion:
    def __init__(self, num_rondas=3, tiempo_debate=60, categoria="Animales", ultima_oportunidad=True, max_longitud_pista=50):
        self.num_rondas = num_rondas
        self.tiempo_debate = tiempo_debate
        self.categoria_seleccionada = categoria
        self.opcion_ultima_oportunidad = ultima_oportunidad
        self.max_longitud_pista = max_longitud_pista


class Categoria:
    def __init__(self, nombre):
        self.nombre = nombre
        self.palabras = []

    def agregar_palabra(self, palabra):
        self.palabras.append(palabra.lower())


class BancoPalabras:
    def __init__(self):
        self.categorias = {}

    def agregar_categoria(self, categoria_obj):
        self.categorias[categoria_obj.nombre] = categoria_obj

    def obtener_palabra_aleatoria(self, nombre_categoria):
        categoria = self.categorias.get(nombre_categoria)
        if categoria and categoria.palabras:
            return random.choice(categoria.palabras)
        return "default"


class PalabraSecreta:
    def __init__(self, nombre, categoria, pista):
        self .nombre = nombre
        self .categoria = categoria
        self .pista = pista

    def mostrar_palabra(self):
        return self.nombre


class Pista:
    def __init__(self, texto, autor):
        self.texto = texto
        self.autor = autor

    def validar_pista(self, palabra_secreta, max_longitud):
        if len(self.texto) > max_longitud:
            return False, "La pista excede la longitud máxima permitida."
        if palabra_secreta.lower() in self.texto.lower():
            return False, "La pista no puede contener la palabra secreta."
        return True, "Pista válida."

class Votacion:
    def __init__(self):
        self.votos = {} 

    def registrar_voto(self, votante, sospechoso):
        if votante != sospechoso and sospechoso.activo:
            self.votos[votante] = sospechoso
            return True
        return False

    def determinar_mas_votado(self):
        conteo = {}
        for sospechoso in self.votos.values():
            conteo[sospechoso] = conteo.get(sospechoso, 0) + 1
        
        if not conteo:
            return None
        
        max_votos = max(conteo.values())
        candidatos = [jugador for jugador, v in conteo.items() if v == max_votos]
        
        if len(candidatos) == 1:
            return candidatos[0]
        else:
            return random.choice(candidatos)  
    def evaluar_ultima_oportunidad(self, impostor, palabra_secreta, intento):
        return intento.strip().lower() == palabra_secreta.lower()

class Ronda:
    def __init__(self, numero_ronda):
        self.numero_ronda = numero_ronda
        self.palabra_secreta = ""
        self.pistas = []

    def asignar_roles_y_palabra(self, jugadores_activos, banco, categoria):
        self.palabra_secreta = banco.obtener_palabra_aleatoria(categoria)
        
        for j in jugadores_activos:
            j.asignar_rol(Civil())
            
        impostor_elegido = random.choice(jugadores_activos)
        impostor_elegido.asignar_rol(Impostor())


class Partida:
    def __init__(self, config: Configuracion):
        self.config = config
        self.estado = "Pendiente"
        self.ronda_actual = 0
        self.jugadores = []
        self.banco = BancoPalabras()

    def iniciar_partida(self, lista_nombres):
        if 3 <= len(lista_nombres) <= 10:
            self.jugadores = [Jugador(nombre) for nombre in lista_nombres]
            self.estado = "En curso"
            self.ronda_actual = 1
            print(f"¡Partida iniciada exitosamente con {len(self.jugadores)} jugadores!")
        else:
            print("Error: Se requieren entre 3 y 10 jugadores.")

if __name__ == "__main__":
    print("=== SIMULADOR DE JUEGO: EL IMPOSTOR ===")
    
    config = Configuracion(num_rondas=1, tiempo_debate=30, categoria="Animales", max_longitud_pista=40)
    
    partida = Partida(config)
    
    nombres = ["Ana", "Carlos", "Sofía", "Mateo"]
    partida.iniciar_partida(nombres)
    
    if partida.estado == "En curso":
        cat_animales = Categoria("Animales")
        cat_animales.agregar_palabra("Elefante")
        cat_animales.agregar_palabra("Jirafa")
        cat_animales.agregar_palabra("Delfín")
        
        partida.banco.agregar_categoria(cat_animales)
        ronda_actual = Ronda(1)
        ronda_actual.asignar_roles_y_palabra(partida.jugadores, partida.banco, config.categoria_seleccionada)
        
        print(f"\n[Ronda 1] Categoría seleccionada: {config.categoria_seleccionada}")
        print("-" * 50)
        
        for jugador in partida.jugadores:
            info_privada = jugador.ver_su_rol(ronda_actual.palabra_secreta)
            print(f"-> Turno de visualización para **{jugador.nombre}**:")
            print(f"   {info_privada}")
        
        print("-" * 50)
        print("\n--- SIMULACIÓN DE ENVÍO DE PISTAS (RF-06) ---")
        
        jugador_test = partida.jugadores[0]
        texto_pista = "Es un animal grande y gris"
        
        nueva_pista = jugador_test.registrar_pista(texto_pista)
        es_valida, mensaje = nueva_pista.validar_pista(ronda_actual.palabra_secreta, config.max_longitud_pista)
        
        print(f"Jugador: {jugador_test.nombre} envía pista: '{texto_pista}'")
        print(f"Validación: {mensaje}")
        
        if es_valida:
            ronda_actual.pistas.append(nueva_pista)
            print("¡Pista registrada con éxito en la ronda!")
            
        print("\n=== FIN DE LA PRUEBA DE CLASES ===")













