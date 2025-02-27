import pygame
import random
import math

# Configuración de la pantalla
ANCHO, ALTO = 500, 500
COLOR_FONDO = (30, 30, 30)

# Configuración de los agentes
TAMANIO_AGENTE = 20
COLOR_AGENTE_REACTIVO = (0, 255, 0)  # Verde para agentes reactivos
COLOR_AGENTE_MANUAL = (0, 100, 255)  # Azul para el agente manual
VELOCIDAD_AGENTE = 2
NUMERO_AGENTES = 10  # Número de agentes reactivos

# Configuración de los obstáculos
COLOR_OBSTACULO = (255, 0, 0)
NUMERO_OBSTACULOS = 5
TAMANIO_OBSTACULO = 40

# Configuración del campo de visión
CAMPO_VISION = 60  # Distancia de visión del agente (valor inicial)
CAMPO_VISION_MIN = 20  # Valor mínimo para el campo de visión
CAMPO_VISION_MAX = 150  # Valor máximo para el campo de visión
CAMPO_VISION_PASO = 5  # Incremento/decremento por paso
COLOR_CAMPO_VISION = (100, 100, 100, 30)  # Color semi-transparente para el campo de visión
MOSTRAR_CAMPO_VISION = True  # Controla si se muestra el campo de visión

# Inicialización de Pygame
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Agentes Reactivos y Manual")

# Generar obstáculos en posiciones aleatorias
obstaculos = []
for _ in range(NUMERO_OBSTACULOS):
    obs_x = random.randint(0, ANCHO - TAMANIO_OBSTACULO)
    obs_y = random.randint(0, ALTO - TAMANIO_OBSTACULO)
    obstaculos.append(pygame.Rect(obs_x, obs_y, TAMANIO_OBSTACULO, TAMANIO_OBSTACULO))


# Clase para representar a un agente
class Agente:
    def __init__(self, es_manual=False):
        self.x = random.randint(0, ANCHO - TAMANIO_AGENTE)
        self.y = random.randint(0, ALTO - TAMANIO_AGENTE)
        self.direccion = random.choice(["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"])
        self.es_manual = es_manual
        self.color = COLOR_AGENTE_MANUAL if es_manual else COLOR_AGENTE_REACTIVO
        self.ultima_colision = None  # Para recordar la última dirección de colisión

    def obtener_rectangulo(self):
        return pygame.Rect(self.x, self.y, TAMANIO_AGENTE, TAMANIO_AGENTE)

    def obtener_campo_vision(self):
        """Obtiene el rectángulo que representa el campo de visión del agente en su dirección."""
        vision_x, vision_y = self.x, self.y
        vision_ancho, vision_alto = TAMANIO_AGENTE, TAMANIO_AGENTE

        if self.direccion == "ARRIBA":
            vision_y -= CAMPO_VISION
            vision_alto += CAMPO_VISION
        elif self.direccion == "ABAJO":
            vision_alto += CAMPO_VISION
        elif self.direccion == "IZQUIERDA":
            vision_x -= CAMPO_VISION
            vision_ancho += CAMPO_VISION
        elif self.direccion == "DERECHA":
            vision_ancho += CAMPO_VISION

        return pygame.Rect(vision_x, vision_y, vision_ancho, vision_alto)

    def detectar_colision_inminente(self, otros_agentes):
        """Detecta si hay una colisión inminente con obstáculos o con otros agentes."""
        campo_vision = self.obtener_campo_vision()

        # Detectar colisión con bordes
        if (self.direccion == "ARRIBA" and self.y - VELOCIDAD_AGENTE < 0 or
            self.direccion == "ABAJO" and self.y + TAMANIO_AGENTE + VELOCIDAD_AGENTE > ALTO or
            self.direccion == "IZQUIERDA" and self.x - VELOCIDAD_AGENTE < 0 or
            self.direccion == "DERECHA" and self.x + TAMANIO_AGENTE + VELOCIDAD_AGENTE > ANCHO):
            return True

        # Detectar colisión con obstáculos
        for obstaculo in obstaculos:
            if campo_vision.colliderect(obstaculo):
                return True

        # Detectar colisión con otros agentes
        for otro_agente in otros_agentes:
            if otro_agente != self and campo_vision.colliderect(otro_agente.obtener_rectangulo()):
                return True

        return False

    def mover(self, teclas=None, otros_agentes=None):
        if otros_agentes is None:
            otros_agentes = []

        # Calcular nueva posición potencial
        nuevo_x, nuevo_y = self.x, self.y

        if self.es_manual and teclas:
            # Control manual con teclas
            movimiento_realizado = False

            if teclas[pygame.K_UP]:
                self.direccion = "ARRIBA"
                nuevo_y -= VELOCIDAD_AGENTE
                movimiento_realizado = True
            elif teclas[pygame.K_DOWN]:
                self.direccion = "ABAJO"
                nuevo_y += VELOCIDAD_AGENTE
                movimiento_realizado = True
            elif teclas[pygame.K_LEFT]:
                self.direccion = "IZQUIERDA"
                nuevo_x -= VELOCIDAD_AGENTE
                movimiento_realizado = True
            elif teclas[pygame.K_RIGHT]:
                self.direccion = "DERECHA"
                nuevo_x += VELOCIDAD_AGENTE
                movimiento_realizado = True

            # Si no se presionó ninguna tecla, no hay movimiento
            if not movimiento_realizado:
                return
        else:
            # Movimiento autónomo para agentes reactivos
            # Verificar colisión inminente y cambiar dirección si es necesario
            if self.detectar_colision_inminente(otros_agentes):
                self.cambiar_direccion_heuristica()

            # Aplicar movimiento según dirección actual
            if self.direccion == "ARRIBA":
                nuevo_y -= VELOCIDAD_AGENTE
            elif self.direccion == "ABAJO":
                nuevo_y += VELOCIDAD_AGENTE
            elif self.direccion == "IZQUIERDA":
                nuevo_x -= VELOCIDAD_AGENTE
            elif self.direccion == "DERECHA":
                nuevo_x += VELOCIDAD_AGENTE

        # Verificar si la nueva posición causa colisión
        rectangulo_nuevo = pygame.Rect(nuevo_x, nuevo_y, TAMANIO_AGENTE, TAMANIO_AGENTE)
        colision_detectada = False

        # Verificar colisión con bordes
        if (nuevo_x < 0 or nuevo_x > ANCHO - TAMANIO_AGENTE or 
            nuevo_y < 0 or nuevo_y > ALTO - TAMANIO_AGENTE):
            colision_detectada = True

        # Verificar colisión con obstáculos
        for obs in obstaculos:
            if rectangulo_nuevo.colliderect(obs):
                colision_detectada = True
                break

        # Verificar colisión con otros agentes
        for otro_agente in otros_agentes:
            if otro_agente != self:
                otro_rect = otro_agente.obtener_rectangulo()
                if rectangulo_nuevo.colliderect(otro_rect):
                    colision_detectada = True
                    break

        # Actualizar posición si no hay colisión
        if not colision_detectada:
            self.x, self.y = nuevo_x, nuevo_y
            self.ultima_colision = None
        elif not self.es_manual:
            # Agentes reactivos cambian dirección cuando hay colisión
            self.cambiar_direccion_heuristica()

    def cambiar_direccion_heuristica(self):
        # Recordar dirección que causó la colisión
        direccion_colision = self.direccion
        self.ultima_colision = direccion_colision

        # Evitar elegir la dirección opuesta a la colisión (para no quedar atrapado)
        direcciones_posibles = ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"]

        # Eliminar la dirección que causó la colisión
        if direccion_colision in direcciones_posibles:
            direcciones_posibles.remove(direccion_colision)

        # Identificar dirección más prometedora (hacia el centro o lejos de obstáculos)
        direccion_al_centro = self.direccion_hacia_centro()
        if direccion_al_centro in direcciones_posibles:
            # 60% de probabilidad de elegir la dirección hacia el centro
            if random.random() < 0.6:
                self.direccion = direccion_al_centro
                return

        # Si no se eligió la dirección al centro, elegir aleatoriamente entre las restantes
        if direcciones_posibles:
            self.direccion = random.choice(direcciones_posibles)

    def direccion_hacia_centro(self):
        # Determina qué dirección lleva hacia el centro de la pantalla
        centro_x = ANCHO // 2
        centro_y = ALTO // 2

        dx = centro_x - self.x
        dy = centro_y - self.y

        if abs(dx) > abs(dy):
            return "DERECHA" if dx > 0 else "IZQUIERDA"
        else:
            return "ABAJO" if dy > 0 else "ARRIBA"

    def dibujar(self):
        # Dibujar el agente
        pygame.draw.rect(pantalla, self.color, (self.x, self.y, TAMANIO_AGENTE, TAMANIO_AGENTE))

        # Dibujar campo de visión (opcional)
        if MOSTRAR_CAMPO_VISION and not self.es_manual:
            campo_vision = self.obtener_campo_vision()
            superficie_vision = pygame.Surface((campo_vision.width, campo_vision.height), pygame.SRCALPHA)
            superficie_vision.fill(COLOR_CAMPO_VISION)
            pantalla.blit(superficie_vision, (campo_vision.x, campo_vision.y))


# Función para verificar colisión
def verificar_colision(x, y):
    rectangulo_agente = pygame.Rect(x, y, TAMANIO_AGENTE, TAMANIO_AGENTE)
    if x < 0 or x > ANCHO - TAMANIO_AGENTE or y < 0 or y > ALTO - TAMANIO_AGENTE:
        return True  # Colisión con los bordes
    for obs in obstaculos:
        if rectangulo_agente.colliderect(obs):
            return True  # Colisión con un obstáculo
    return False  # Sin colisión

# Crear agentes
agentes = []
for _ in range(NUMERO_AGENTES):
    agentes.append(Agente(es_manual=False))

# Crear agente manual
agente_manual = Agente(es_manual=True)
agentes.append(agente_manual)

# Bucle principal
ejecutando = True
reloj = pygame.time.Clock()
while ejecutando:
    reloj.tick(60)  # Limitar a 60 FPS

    # Verificar eventos (cierre de ventana y teclas)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            # Ajustar campo de visión con teclas + y -
            if (
                evento.key == pygame.K_PLUS
                or evento.key == pygame.K_KP_PLUS
                or evento.key == pygame.K_EQUALS
            ):
                CAMPO_VISION = min(CAMPO_VISION + CAMPO_VISION_PASO, CAMPO_VISION_MAX)
                print(f"Campo de visión: {CAMPO_VISION}")
            elif evento.key == pygame.K_MINUS or evento.key == pygame.K_KP_MINUS:
                CAMPO_VISION = max(CAMPO_VISION - CAMPO_VISION_PASO, CAMPO_VISION_MIN)
                print(f"Campo de visión: {CAMPO_VISION}")
            # Activar/desactivar la visualización del campo de visión con la tecla 'V'
            elif evento.key == pygame.K_v:
                MOSTRAR_CAMPO_VISION = not MOSTRAR_CAMPO_VISION
                print(f"Mostrar campo de visión: {MOSTRAR_CAMPO_VISION}")

    # Obtener estado de las teclas para el agente manual
    teclas = pygame.key.get_pressed()

    # Actualizar todos los agentes
    for agente in agentes:
        agente.mover(teclas, agentes)

    # Dibujar el entorno
    pantalla.fill(COLOR_FONDO)

    # Dibujar obstáculos
    for obs in obstaculos:
        pygame.draw.rect(pantalla, COLOR_OBSTACULO, obs)

    # Dibujar agentes
    for agente in agentes:
        agente.dibujar()

    # Mostrar instrucciones en pantalla
    fuente = pygame.font.SysFont("Arial", 14)
    texto1 = fuente.render(
        "Usa las flechas para controlar el agente azul", True, (255, 255, 255)
    )
    texto2 = fuente.render(
        "+ / - : Ajustar campo de visión | V : Mostrar/ocultar campo de visión",
        True,
        (255, 255, 255),
    )
    texto3 = fuente.render(
        f"Campo de visión actual: {CAMPO_VISION}", True, (255, 255, 255)
    )
    pantalla.blit(texto1, (10, 10))
    pantalla.blit(texto2, (10, 30))
    pantalla.blit(texto3, (10, 50))

    pygame.display.update()

# Cerrar Pygame
pygame.quit()
