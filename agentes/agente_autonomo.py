import pygame
import random
import math
import datetime

# Configuración de la pantalla
ANCHO, ALTO = 600, 600
TAMANIO_CELDA = 40
FILAS = ANCHO // TAMANIO_CELDA
COLUMNAS = ALTO // TAMANIO_CELDA

# Colores
COLOR_FONDO = (30, 30, 30)
COLOR_SUCIO = (139, 69, 19)  # Marrón
COLOR_LIMPIO = (255, 255, 255)  # Blanco
COLOR_ASPIRADOR = (0, 255, 0)  # Verde
COLOR_BOTON = (0, 120, 200)  # Azul para botón
COLOR_BOTON_HOVER = (30, 150, 230)  # Azul claro para hover

# Colores adicionales para la aspiradora
COLOR_ASPIRADOR_CUERPO = (50, 50, 200)  # Azul oscuro
COLOR_ASPIRADOR_RUEDAS = (40, 40, 40)  # Negro
COLOR_ASPIRADOR_DETALLES = (220, 20, 60)  # Rojo

# Colores para múltiples aspiradores
COLOR_ASPIRADORES = [(50, 50, 200), (200, 50, 50), (50, 200, 50), (200, 200, 50)]

# Inicializar Pygame
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Aspirador Autónomo Mejorado")

# Add this near the top of your file with other constants
VELOCIDAD_INICIAL = 300  # Delay in milliseconds (lower = faster)
VELOCIDAD_RAPIDA = 100
VELOCIDAD_LENTA = 500

# Add this after initializing the simulation
velocidad_actual = VELOCIDAD_INICIAL

# Fuentes
fuente = pygame.font.SysFont('Arial', 14)
fuente_grande = pygame.font.SysFont('Arial', 24)
fuente_boton = pygame.font.SysFont('Arial', 18)

def inicializar_simulacion():
    # Generar el entorno con suciedad aleatoria (1 = sucio, 0 = limpio)
    entorno = [[random.choice([0, 1]) for _ in range(COLUMNAS)] for _ in range(FILAS)]
    
    # Configuración de múltiples aspiradores
    NUM_ASPIRADORES = 3
    aspiradores = []
    for i in range(NUM_ASPIRADORES):
        aspiradores.append({
            "x": random.randint(0, FILAS - 1),
            "y": random.randint(0, COLUMNAS - 1),
            "color": COLOR_ASPIRADORES[i % len(COLOR_ASPIRADORES)],
            "movimientos": 0
        })
    
    # Variables para estadísticas
    tiempo_inicio = pygame.time.get_ticks()
    celdas_iniciales_sucias = sum(sum(fila) for fila in entorno)
    estadisticas = {
        "tiempo_transcurrido": 0,
        "movimientos_totales": 0,
        "celdas_limpiadas": 0,
        "celdas_iniciales": celdas_iniciales_sucias,
        "tiempo_inicio": tiempo_inicio
    }
    
    return entorno, aspiradores, estadisticas, False  # False = limpieza_completa

# Función para guardar estadísticas
def guardar_estadisticas(estadisticas):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    segundos = estadisticas["tiempo_transcurrido"] // 1000
    milisegundos = estadisticas["tiempo_transcurrido"] % 1000
    
    with open("estadisticas_aspiradora.txt", "a") as archivo:
        archivo.write(f"=== Simulación completada: {fecha} ===\n")
        archivo.write(f"Tiempo total: {segundos}.{milisegundos:03d} segundos\n")
        archivo.write(f"Movimientos totales: {estadisticas['movimientos_totales']}\n")
        archivo.write(f"Celdas limpiadas: {estadisticas['celdas_limpiadas']}\n")
        archivo.write(f"Eficiencia: {estadisticas['celdas_limpiadas'] / max(1, estadisticas['movimientos_totales'])} celdas/movimiento\n")
        archivo.write("===================================\n\n")

# Función para buscar celdas sucias cercanas
def buscar_celdas_sucias(entorno, x, y, radio_busqueda=2):
    celdas_sucias = []
    for i in range(max(0, x-radio_busqueda), min(FILAS, x+radio_busqueda+1)):
        for j in range(max(0, y-radio_busqueda), min(COLUMNAS, y+radio_busqueda+1)):
            if entorno[i][j] == 1:  # Celda sucia
                # Calcular distancia Manhattan
                distancia = abs(i - x) + abs(j - y)
                celdas_sucias.append((i, j, distancia))

    # Ordenar por distancia
    if celdas_sucias:
        celdas_sucias.sort(key=lambda c: c[2])
        return celdas_sucias[0][0], celdas_sucias[0][1]  # Retornar la más cercana
    return None


# Función mejorada para mover el aspirador con prevención de colisiones
def mover_aspirador(x, y, entorno, aspiradores):
    # Primero verificar si hay otros aspiradores en las celdas adyacentes
    posiciones_ocupadas = []
    for aspirador in aspiradores:
        # No consideramos el aspirador actual
        if aspirador["x"] == x and aspirador["y"] == y:
            continue
        # Agregamos la posición y las posiciones adyacentes como "zonas de exclusión"
        posiciones_ocupadas.append((aspirador["x"], aspirador["y"]))

    # Buscar celdas sucias cercanas
    celda_sucia = buscar_celdas_sucias(entorno, x, y)

    if celda_sucia:
        # Encontró una celda sucia cercana
        destino_x, destino_y = celda_sucia

        # Posibles movimientos hacia la celda sucia
        posibles_movimientos = []
        if destino_x > x:
            posibles_movimientos.append((x + 1, y, "abajo"))
        elif destino_x < x:
            posibles_movimientos.append((x - 1, y, "arriba"))
        elif destino_y > y:
            posibles_movimientos.append((x, y + 1, "derecha"))
        elif destino_y < y:
            posibles_movimientos.append((x, y - 1, "izquierda"))

        # Verificar colisiones en esos movimientos
        for nuevo_x, nuevo_y, _ in posibles_movimientos:
            if (nuevo_x, nuevo_y) not in posiciones_ocupadas:
                if 0 <= nuevo_x < FILAS and 0 <= nuevo_y < COLUMNAS:
                    return nuevo_x, nuevo_y

    # Si no encontró celdas sucias o hay colisión, moverse aleatoriamente evitando colisiones
    movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    random.shuffle(movimientos)
    for dx, dy in movimientos:
        nuevo_x, nuevo_y = x + dx, y + dy
        if (
            (nuevo_x, nuevo_y) not in posiciones_ocupadas
            and 0 <= nuevo_x < FILAS
            and 0 <= nuevo_y < COLUMNAS
        ):
            return nuevo_x, nuevo_y

    # Si no puede moverse en ninguna dirección, se queda quieto
    return x, y


# Función para dibujar un aspirador
def dibujar_aspirador(pantalla, x, y, color):
    pos_x = y * TAMANIO_CELDA + TAMANIO_CELDA // 2
    pos_y = x * TAMANIO_CELDA + TAMANIO_CELDA // 2
    radio = TAMANIO_CELDA // 2 - 2

    # Cuerpo circular principal
    pygame.draw.circle(pantalla, color, (pos_x, pos_y), radio)

    # Borde exterior
    pygame.draw.circle(pantalla, COLOR_ASPIRADOR_RUEDAS, (pos_x, pos_y), radio, 2)

    # Panel de control central
    pygame.draw.circle(pantalla, COLOR_ASPIRADOR_DETALLES, (pos_x, pos_y), radio // 3)

    # Botón central
    pygame.draw.circle(pantalla, COLOR_LIMPIO, (pos_x, pos_y), radio // 6)

    # Sensores frontales (pequeños círculos)
    angulo = 0  # Podría usarse para indicar dirección
    sensor_x = pos_x + int((radio - 4) * math.cos(math.radians(angulo)))
    sensor_y = pos_y + int((radio - 4) * math.sin(math.radians(angulo)))
    pygame.draw.circle(pantalla, COLOR_ASPIRADOR_RUEDAS, (sensor_x, sensor_y), 3)

    # Segundo sensor
    sensor_x = pos_x + int((radio - 4) * math.cos(math.radians(angulo + 45)))
    sensor_y = pos_y + int((radio - 4) * math.sin(math.radians(angulo + 45)))
    pygame.draw.circle(pantalla, COLOR_ASPIRADOR_RUEDAS, (sensor_x, sensor_y), 3)

# Función para dibujar botón
def dibujar_boton(pantalla, texto, rect, color, hover=False):
    # Dibujar fondo del botón
    if hover:
        pygame.draw.rect(pantalla, COLOR_BOTON_HOVER, rect, border_radius=5)
    else:
        pygame.draw.rect(pantalla, COLOR_BOTON, rect, border_radius=5)
    
    # Dibujar borde
    pygame.draw.rect(pantalla, (200, 200, 200), rect, 2, border_radius=5)
    
    # Dibujar texto
    texto_superficie = fuente_boton.render(texto, True, (255, 255, 255))
    texto_rect = texto_superficie.get_rect(center=rect.center)
    pantalla.blit(texto_superficie, texto_rect)

# Iniciar simulación
entorno, aspiradores, estadisticas, limpieza_completa = inicializar_simulacion()

# Crear botón de reinicio
# boton_reiniciar = pygame.Rect(ANCHO//2 - 60, ALTO//2 + 30, 120, 40)
boton_reiniciar = pygame.Rect(ANCHO//2 - 60, ALTO//2 + 70, 120, 40)  # Changed from +30 to +70

# Bucle principal
ejecutando = True
while ejecutando:
    mouse_pos = pygame.mouse.get_pos()
    mouse_sobre_boton = boton_reiniciar.collidepoint(mouse_pos)

    # Verificar eventos (cierre de ventana)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            # Speed control with + and - keys
            if evento.key == pygame.K_PLUS or evento.key == pygame.K_KP_PLUS:
                velocidad_actual = max(50, velocidad_actual - 50)  # Increase speed (decrease delay)
            elif evento.key == pygame.K_MINUS or evento.key == pygame.K_KP_MINUS:
                velocidad_actual = min(600, velocidad_actual + 50)  # Decrease speed (increase delay)
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if limpieza_completa and boton_reiniciar.collidepoint(evento.pos):
                # Reiniciar la simulación
                entorno, aspiradores, estadisticas, limpieza_completa = inicializar_simulacion()
                velocidad_actual = VELOCIDAD_INICIAL  # Reset speed when restarting

    # Si limpieza no está completa, seguir con la simulación
    if not limpieza_completa:
        # pygame.time.delay(300)  # Pausa para visualizar mejor el movimiento
        pygame.time.delay(velocidad_actual)  # Variable delay based on speed setting

        # En el bucle principal, actualizar cada aspirador
        for aspirador in aspiradores:
            # Verificar si la casilla actual está sucia y limpiarla
            if entorno[aspirador["x"]][aspirador["y"]] == 1:
                entorno[aspirador["x"]][aspirador["y"]] = 0  # Limpiar la casilla
                estadisticas["celdas_limpiadas"] += 1
            else:
                # Si la casilla ya está limpia, moverse a otra casilla
                nuevo_x, nuevo_y = mover_aspirador(
                    aspirador["x"], aspirador["y"], entorno, aspiradores
                )
                if nuevo_x != aspirador["x"] or nuevo_y != aspirador["y"]:
                    aspirador["movimientos"] += 1
                    estadisticas["movimientos_totales"] += 1
                aspirador["x"], aspirador["y"] = nuevo_x, nuevo_y

        # Actualizar estadísticas
        # estadisticas["tiempo_transcurrido"] = (pygame.time.get_ticks() - estadisticas["tiempo_inicio"]) // 1000  # en segundos
        estadisticas["tiempo_transcurrido"] = pygame.time.get_ticks() - estadisticas["tiempo_inicio"]  # Store raw milliseconds


        # Verificar si todo está limpio
        celdas_sucias_restantes = sum(sum(fila) for fila in entorno)
        if celdas_sucias_restantes == 0:
            limpieza_completa = True
            guardar_estadisticas(estadisticas)

    # Dibujar el entorno
    if limpieza_completa:
        # Pantalla negra para mensaje final
        pantalla.fill((0, 0, 0))  # Negro para el mensaje de finalización
    else:
        # Pantalla normal durante la simulación
        pantalla.fill(COLOR_FONDO)
        for i in range(FILAS):
            for j in range(COLUMNAS):
                color = COLOR_SUCIO if entorno[i][j] == 1 else COLOR_LIMPIO
                pygame.draw.rect(pantalla, color, (j * TAMANIO_CELDA, i * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA))

        # Dibujar rejilla
        for i in range(FILAS + 1):
            pygame.draw.line(pantalla, COLOR_FONDO, (0, i * TAMANIO_CELDA), (ANCHO, i * TAMANIO_CELDA), 1)
        for j in range(COLUMNAS + 1):
            pygame.draw.line(pantalla, COLOR_FONDO, (j * TAMANIO_CELDA, 0), (j * TAMANIO_CELDA, ALTO), 1)

        # Dibujar cada aspirador
        for aspirador in aspiradores:
            dibujar_aspirador(pantalla, aspirador["x"], aspirador["y"], aspirador["color"])

        # Mostrar estadísticas en pantalla durante la simulación
        porcentaje_limpio = 0
        if estadisticas["celdas_iniciales"] > 0:
            porcentaje_limpio = int(estadisticas["celdas_limpiadas"]*100/estadisticas["celdas_iniciales"])

        # textos = [
        #     f"Tiempo: {estadisticas['tiempo_transcurrido']} seg",
        #     f"Movimientos: {estadisticas['movimientos_totales']}",
        #     f"Limpiado: {estadisticas['celdas_limpiadas']}/{estadisticas['celdas_iniciales']} ({porcentaje_limpio}%)"
        # ]

        # textos = [
        #     f"Velocidad: {int(100 * VELOCIDAD_INICIAL / velocidad_actual)}%",  # 100% at initial speed
        #     f"Tiempo: {estadisticas['tiempo_transcurrido']} seg",
        #     f"Movimientos: {estadisticas['movimientos_totales']}",
        #     f"Limpiado: {estadisticas['celdas_limpiadas']}/{estadisticas['celdas_iniciales']} ({porcentaje_limpio}%)",
        # ]
        
        segundos = estadisticas["tiempo_transcurrido"] // 1000
        milisegundos = estadisticas["tiempo_transcurrido"] % 1000
        textos = [
            f"Velocidad: {int(100 * VELOCIDAD_INICIAL / velocidad_actual)}%",  # 100% at initial speed
            f"Tiempo: {segundos}.{milisegundos:03d} seg",  # Format as seconds.milliseconds
            f"Movimientos: {estadisticas['movimientos_totales']}",
            f"Limpiado: {estadisticas['celdas_limpiadas']}/{estadisticas['celdas_iniciales']} ({porcentaje_limpio}%)",
        ]

        for i, texto in enumerate(textos):
            superficie_texto = fuente.render(texto, True, (0, 0, 0))  # Changed from (255, 255, 255) to (0, 0, 0)
            pantalla.blit(superficie_texto, (10, 10 + i * 20))

    # Si limpieza está completa, mostrar mensaje y botón de reinicio
    if limpieza_completa:
        # Mostrar mensaje de finalización
        texto_final = fuente_grande.render("¡Limpieza completa!", True, (255, 255, 0))
        pantalla.blit(texto_final, (ANCHO//2 - texto_final.get_width()//2, ALTO//2 - 60))

        # Mostrar estadísticas finales
        # textos = [
        #     f"Tiempo total: {estadisticas['tiempo_transcurrido']} segundos",
        #     f"Movimientos: {estadisticas['movimientos_totales']}",
        #     f"Celdas limpiadas: {estadisticas['celdas_limpiadas']}"
        # ]
        
        segundos = estadisticas["tiempo_transcurrido"] // 1000
        milisegundos = estadisticas["tiempo_transcurrido"] % 1000
        textos = [
            f"Tiempo total: {segundos}.{milisegundos:03d} segundos",
            f"Movimientos: {estadisticas['movimientos_totales']}",
            f"Celdas limpiadas: {estadisticas['celdas_limpiadas']}"
        ]

        for i, texto in enumerate(textos):
            superficie_texto = fuente.render(texto, True, (255, 255, 255))
            pantalla.blit(superficie_texto, (ANCHO//2 - superficie_texto.get_width()//2, ALTO//2 - 20 + i * 20))

        # Dibujar botón de reiniciar
        dibujar_boton(pantalla, "Reiniciar", boton_reiniciar, COLOR_BOTON, hover=mouse_sobre_boton)

    pygame.display.update()

# Cerrar Pygame
pygame.quit()
