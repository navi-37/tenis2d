import pygame
import os
from engine.ui import Scene


class MenuScene(Scene):
    """Menú principal del juego"""

    def __init__(self, game):
        super().__init__(game)
        self.state = "inicio"
        self.selected_players = 1  # Por defecto 1 jugador

        # Cargar fuente
        base_path = os.path.dirname(os.path.dirname(__file__))
        font_path = os.path.join(base_path, "assets", "fonts", "Minecraft.ttf")
        self.font = pygame.font.Font(font_path, 50)
        self.title_surf = self.font.render(
            "Presiona 'ENTER' para continuar",
            True,
            (255, 255, 255)
        )

        # Cargar imágenes
        self._load_images()

        # Máscaras para detección de hover
        self.mask_boton1 = pygame.mask.from_surface(self.boton1)
        self.mask_boton2 = pygame.mask.from_surface(self.boton2)

        # Animación de scroll
        self.x_offset = 0
        self.scroll_speed = 20

    def _load_images(self):
        """Carga y escala todas las imágenes del menú"""
        img_path = "assets/img"
        size = (self.game.width, self.game.height)

        # Función helper para cargar y escalar
        def load_scale(filename, convert_alpha=False):
            img = pygame.image.load(os.path.join(img_path, filename))
            img = img.convert_alpha() if convert_alpha else img.convert()
            return pygame.transform.scale(img, size)

        self.background = load_scale("utuTenisPantalla.png")
        self.titulo = load_scale("utuTenisTexto.png", True)
        self.titulojugadores = load_scale("tituloJugadores.png", True)

        self.boton1 = load_scale("boton1jugador.png", True)
        self.boton1apretado = load_scale("boton1jugadorAPRETADO.png", True)
        self.boton2 = load_scale("boton2jugadores.png", True)
        self.boton2apretado = load_scale("boton2jugadoresAPRETADO.png", True)

    def _check_button_hover(self, mask, offset_x):
        """Verifica si el mouse está sobre un botón usando su máscara"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        local_x = mouse_x - offset_x
        local_y = mouse_y

        if (0 <= local_x < mask.get_size()[0] and
                0 <= local_y < mask.get_size()[1]):
            try:
                return mask.get_at((local_x, local_y))
            except IndexError:
                return False
        return False

    def start_game(self, num_players):
        """Inicia el juego con el número de jugadores seleccionado"""
        self.selected_players = num_players
        self.game.change_scene('game', num_players=num_players)

    def handle_events(self, events):
        """Maneja eventos del menú"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.state == "inicio":
                    self.state = "desplazando"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "seleccion_jugadores":
                    offset_x = self.x_offset + self.game.width

                    # Verificar clic en botón 1 jugador
                    if self._check_button_hover(self.mask_boton1, offset_x):
                        self.start_game(1)

                    # Verificar clic en botón 2 jugadores
                    elif self._check_button_hover(self.mask_boton2, offset_x):
                        self.start_game(2)

    def update(self, dt):
        """Actualiza la animación del menú"""
        if self.state == "desplazando":
            self.x_offset -= self.scroll_speed
            if self.x_offset <= -self.game.width:
                self.x_offset = -self.game.width
                self.state = "seleccion_jugadores"

    def draw(self, surface):
        """Dibuja el menú"""
        # Fondo base
        surface.blit(self.background, (0, 0))
        surface.blit(self.titulo, (self.x_offset, 0))

        # Pantalla de inicio
        if self.state in ["inicio", "desplazando"]:
            title_rect = self.title_surf.get_rect(
                center=(surface.get_width() / 2 + self.x_offset,
                        self.game.height / 1.16)
            )
            surface.blit(self.title_surf, title_rect)

        # Pantalla de selección de jugadores
        if self.state in ["desplazando", "seleccion_jugadores"]:
            offset_x = self.x_offset + self.game.width

            surface.blit(self.titulojugadores, (offset_x, 0))

            # Determinar qué versión de los botones mostrar (normal o hover)
            boton1_actual = (self.boton1apretado
                             if self._check_button_hover(self.mask_boton1, offset_x)
                             else self.boton1)

            boton2_actual = (self.boton2apretado
                             if self._check_button_hover(self.mask_boton2, offset_x)
                             else self.boton2)

            surface.blit(boton1_actual, (offset_x, 0))
            surface.blit(boton2_actual, (offset_x, 0))