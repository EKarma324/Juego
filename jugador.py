#interfaz jugador

from abc import ABC, abstractmethod
import random
import unicodedata


def normalizar_texto(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas para comparaciones sin ambigüedad."""
    texto = texto.strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


class Rol(ABC):
    def __init__(self, nombre: str):
        self.nombre = nombre

    @abstractmethod
    def mostrar_informacion(self, palabra_secreta: str) -> str:
        """Método abstracto que redefinirá cada subclase (Polimorfismo)."""
        pass


class Civil(Rol):
    def __init__(self):
        super().__init__("Civil")

    def mostrar_informacion(self, palabra_secreta: str) -> str:
        return f"Tu rol es CIVIL. La palabra secreta es: '{palabra_secreta}'"


class Impostor(Rol):
    def __init__(self):
        super().__init__("Impostor")

    def mostrar_informacion(self, palabra_secreta: str) -> str:
        return "¡Eres el IMPOSTOR! No conoces la palabra secreta, debes disimular."


class Configuracion:
    def __init__(
        self,
        num_rondas: int = 3,
        tiempo_debate: int = 60,
        categoria: str = "Animales",
        ultima_oportunidad: bool = True,
        max_longitud_pista: int = 50,
    ):
        self.num_rondas = num_rondas
        self.tiempo_debate = tiempo_debate
        self.categoria_seleccionada = categoria
        self.opcion_ultima_oportunidad = ultima_oportunidad
        self.max_longitud_pista = max_longitud_pista


class Jugador:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.rol: Rol | None = None
        self.activo = True
        self.puntaje = 0

    def asignar_rol(self, rol_obj: Rol):
        self.rol = rol_obj

    def ver_su_rol(self, palabra_secreta: str) -> str:
        if self.rol is None:
            return "Sin rol asignado."
        return self.rol.mostrar_informacion(palabra_secreta)

    def registrar_pista(self, texto: str) -> "Pista":
        return Pista(texto, self)

    def emitir_voto(self, jugador_objetivo: "Jugador") -> "Jugador":
        return jugador_objetivo


class Categoria:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.palabras: list[str] = []

    def agregar_palabra(self, palabra: str):
        palabra_limpia = palabra.strip().lower()
        if palabra_limpia and palabra_limpia not in self.palabras:
            self.palabras.append(palabra_limpia)


class BancoPalabras:
    def __init__(self):
        self.categorias: dict[str, Categoria] = {}

    def agregar_categoria(self, categoria_obj: Categoria):
        self.categorias[categoria_obj.nombre] = categoria_obj

    def obtener_palabra_aleatoria(self, nombre_categoria: str) -> str:
        categoria = self.categorias.get(nombre_categoria)
        if categoria and categoria.palabras:
            return random.choice(categoria.palabras)
        return "elefante"


class PalabraSecreta:
    def __init__(self, nombre: str, categoria: str, pista: str = ""):
        self.nombre = nombre
        self.categoria = categoria
        self.pista = pista

    def mostrar_palabra(self) -> str:
        return self.nombre


class Pista:
    def __init__(self, texto: str, autor: Jugador):
        self.texto = texto.strip()
        self.autor = autor

    def validar_pista(self, palabra_secreta: str, max_longitud: int) -> tuple[bool, str]:
        if not self.texto:
            return False, "La pista no puede estar vacía."
        if len(self.texto) > max_longitud:
            return False, f"La pista excede el máximo de {max_longitud} caracteres."
        if normalizar_texto(palabra_secreta) in normalizar_texto(self.texto):
            return False, "La pista no puede contener la palabra secreta."
        return True, "Pista válida."


class Votacion:
    def __init__(self):
        self.votos: dict[Jugador, Jugador] = {}

    def registrar_voto(self, votante: Jugador, sospechoso: Jugador) -> bool:
        if votante != sospechoso and sospechoso.activo:
            self.votos[votante] = sospechoso
            return True
        return False

    def determinar_mas_votado(self) -> Jugador | None:
        conteo: dict[Jugador, int] = {}
        for sospechoso in self.votos.values():
            conteo[sospechoso] = conteo.get(sospechoso, 0) + 1

        if not conteo:
            return None

        max_votos = max(conteo.values())
        candidatos = [jugador for jugador, votos in conteo.items() if votos == max_votos]

        if len(candidatos) == 1:
            return candidatos[0]
        return random.choice(candidatos)

    def evaluar_ultima_oportunidad(self, impostor: Jugador, palabra_secreta: str, intento: str) -> bool:
        return normalizar_texto(intento) == normalizar_texto(palabra_secreta)


class Ronda:
    def __init__(self, numero_ronda: int):
        self.numero_ronda = numero_ronda
        self.palabra_secreta = ""
        self.pistas: list[Pista] = []
        self.votacion = Votacion()
        self.impostor: Jugador | None = None

    def asignar_roles_y_palabra(self, jugadores_activos: list[Jugador], banco: BancoPalabras, categoria: str):
        self.palabra_secreta = banco.obtener_palabra_aleatoria(categoria)

        for jugador in jugadores_activos:
            jugador.asignar_rol(Civil())

        impostor_elegido = random.choice(jugadores_activos)
        impostor_elegido.asignar_rol(Impostor())
        self.impostor = impostor_elegido


class Partida:
    def __init__(self, config: Configuracion):
        self.config = config
        self.estado = "Pendiente"
        self.ronda_actual = 0
        self.jugadores: list[Jugador] = []
        self.banco = BancoPalabras()
        self._cargar_banco_inicial()

    def _cargar_banco_inicial(self):
        categorias_base = {
            "Animales": [
                "elefante", "jirafa", "delfin", "pinguino", "camaleon",
                "murcielago", "cocodrilo", "flamenco", "pulpo", "koala"
            ],
            "Comida": [
                "hamburguesa", "sushi", "arepa", "empanada", "lasana",
                "tacos", "ceviche", "paella", "chocolate", "aguacate"
            ],
            "Lugares": [
                "hospital", "aeropuerto", "biblioteca", "submarino", "volcan",
                "museo", "estadio", "desierto", "zoologico", "castillo"
            ],
            "Objetos": [
                "microscopio", "brujula", "telescopio", "paraguas", "guitarra",
                "reloj", "espejo", "linterna", "candado", "bicicleta"
            ],
        }
        for nombre_cat, palabras in categorias_base.items():
            categoria = Categoria(nombre_cat)
            for palabra in palabras:
                categoria.agregar_palabra(palabra)
            self.banco.agregar_categoria(categoria)

    def iniciar_partida(self, lista_nombres: list[str]) -> tuple[bool, str]:
        nombres_limpios = [n.strip() for n in lista_nombres if n.strip()]
        if len(set(n.lower() for n in nombres_limpios)) != len(nombres_limpios):
            return False, "Error: No puede haber nombres repetidos."
        if 3 <= len(nombres_limpios) <= 10:
            self.jugadores = [Jugador(nombre) for nombre in nombres_limpios]
            self.estado = "En curso"
            self.ronda_actual = 1
            return True, f"¡Partida iniciada con {len(self.jugadores)} jugadores!"
        return False, "Error: Se requieren entre 3 y 10 jugadores."

    def asignar_puntos(self, ganan_civiles: bool):
        for jugador in self.jugadores:
            es_impostor = isinstance(jugador.rol, Impostor)
            if ganan_civiles and not es_impostor:
                jugador.puntaje += 100
            elif not ganan_civiles and es_impostor:
                jugador.puntaje += 200

    def mostrar_puntajes(self):
        print("\n--- TABLA DE PUNTAJES ---")
        ranking = sorted(self.jugadores, key=lambda j: j.puntaje, reverse=True)
        for pos, jugador in enumerate(ranking, start=1):
            print(f"{pos}. {jugador.nombre}: {jugador.puntaje} pts")


def limpiar_consola():
    print("\n" * 40)


def leer_entero(mensaje: str, minimo: int, maximo: int, por_defecto: int) -> int:
    while True:
        try:
            entrada = input(f"{mensaje} [{minimo}-{maximo}, defecto {por_defecto}]: ").strip()
            if not entrada:
                return por_defecto
            valor = int(entrada)
            if minimo <= valor <= maximo:
                return valor
            print(f"Ingresa un número entre {minimo} y {maximo}.")
        except ValueError:
            print("Entrada inválida. Escribe un número entero.")


def ejecutar_en_terminal():
    print("========================================")
    print("   EL IMPOSTOR - JUEGO EN TERMINAL")
    print("========================================")

    categorias = ["Animales", "Comida", "Lugares", "Objetos"]
    print("\nCategorías disponibles:")
    for idx, cat in enumerate(categorias, start=1):
        print(f"  {idx}. {cat}")

    idx_cat = leer_entero("Elige el número de categoría", 1, len(categorias), 1)
    categoria_elegida = categorias[idx_cat - 1]
    num_rondas = leer_entero("Número de rondas", 1, 10, 2)
    tiempo_debate = leer_entero("Tiempo sugerido de debate (segundos)", 15, 300, 60)
    max_longitud = leer_entero("Longitud máxima de pista", 15, 120, 50)
    ultima_op = input("¿Activar última oportunidad del impostor? (s/n) [s]: ").strip().lower() != "n"

    config = Configuracion(
        num_rondas=num_rondas,
        tiempo_debate=tiempo_debate,
        categoria=categoria_elegida,
        ultima_oportunidad=ultima_op,
        max_longitud_pista=max_longitud,
    )
    partida = Partida(config)

    while True:
        cantidad = leer_entero("¿Cuántos jugadores participarán?", 3, 10, 4)
        nombres = []
        for i in range(1, cantidad + 1):
            nombre = input(f"Nombre del jugador {i}: ").strip()
            nombres.append(nombre)

        ok, msg = partida.iniciar_partida(nombres)
        print(msg)
        if ok:
            break

    for num_ronda in range(1, config.num_rondas + 1):
        partida.ronda_actual = num_ronda
        ronda = Ronda(num_ronda)
        ronda.asignar_roles_y_palabra(partida.jugadores, partida.banco, config.categoria_seleccionada)

        print(f"\n================ RONDA {num_ronda} de {config.num_rondas} ================")
        print(f"Categoría: {config.categoria_seleccionada}")

        for jugador in partida.jugadores:
            input(f"\nPasa el dispositivo a {jugador.nombre} y presiona ENTER para ver tu rol...")
            print(jugador.ver_su_rol(ronda.palabra_secreta))
            input("Presiona ENTER para ocultar y pasar al siguiente...")
            limpiar_consola()

        print(f"\n--- FASE DE PISTAS (Categoría: {config.categoria_seleccionada}) ---")
        for jugador in partida.jugadores:
            while True:
                texto = input(f"{jugador.nombre}, escribe tu pista: ")
                pista = jugador.registrar_pista(texto)
                valida, motivo = pista.validar_pista(ronda.palabra_secreta, config.max_longitud_pista)
                if valida:
                    ronda.pistas.append(pista)
                    print("-> Pista registrada.")
                    break
                print(f"-> Error: {motivo}")

        print(f"\n--- DEBATE ({config.tiempo_debate}s sugeridos) ---")
        for p in ronda.pistas:
            print(f"  * {p.autor.nombre}: \"{p.texto}\"")
        input("\nPresiona ENTER cuando termine el debate para votar...")

        print("\n--- VOTACIÓN ---")
        for votante in partida.jugadores:
            candidatos = [j for j in partida.jugadores if j != votante and j.activo]
            print(f"\nTurno de votar de {votante.nombre}:")
            for idx, c in enumerate(candidatos, start=1):
                print(f"  {idx}. {c.nombre}")

            eleccion = leer_entero("Elige el número del sospechoso", 1, len(candidatos), 1)
            ronda.votacion.registrar_voto(votante, candidatos[eleccion - 1])
            print("-> Voto registrado.")

        mas_votado = ronda.votacion.determinar_mas_votado()
        impostor = ronda.impostor

        print("\n--- RESULTADO DE LA RONDA ---")
        if mas_votado:
            print(f"Más votado: {mas_votado.nombre}")

        if mas_votado == impostor and impostor is not None:
            print(f"¡Descubrieron a {impostor.nombre} como el IMPOSTOR!")
            if config.opcion_ultima_oportunidad:
                intento = input(f"{impostor.nombre}, ÚLTIMA OPORTUNIDAD - ¿cuál es la palabra secreta? ")
                if ronda.votacion.evaluar_ultima_oportunidad(impostor, ronda.palabra_secreta, intento):
                    print(f"¡Adivinaste '{ronda.palabra_secreta}'! Gana el Impostor (+200 pts).")
                    partida.asignar_puntos(ganan_civiles=False)
                else:
                    print(f"Fallaste (era '{ronda.palabra_secreta}'). Ganan los Civiles (+100 pts c/u).")
                    partida.asignar_puntos(ganan_civiles=True)
            else:
                print(f"La palabra secreta era '{ronda.palabra_secreta}'. Ganan los Civiles (+100 pts c/u).")
                partida.asignar_puntos(ganan_civiles=True)
        else:
            nombre_impostor = impostor.nombre if impostor else "desconocido"
            print(f"No atraparon al Impostor ({nombre_impostor}). La palabra era '{ronda.palabra_secreta}'.")
            print("¡Gana el Impostor (+200 pts)!")
            partida.asignar_puntos(ganan_civiles=False)

        partida.mostrar_puntajes()

    partida.estado = "Finalizada"
    print("\n========================================")
    print("           PARTIDA FINALIZADA")
    print("========================================")
    partida.mostrar_puntajes()


if __name__ == "__main__":
    try:
        ejecutar_en_terminal()
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario. ¡Hasta pronto!")