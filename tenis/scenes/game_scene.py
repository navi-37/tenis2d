import pygame
from engine.ui import Scene
from tenis.entities.player import Player


class GameScene(Scene):
    """Escena principal del juego"""

    def __init__(self, game, num_players=1):
        super().__init__(game)

        # Fondo
        self.background_img = pygame.image.load("assets/img/cancha.png").convert()
        self.background = pygame.transform.scale(
            self.background_img,
            (self.game.width, self.game.height)
        )

        # Crear jugadores
        self.players = []
        self.num_players = num_players

        # Jugador 1
        self.player1 = Player(450, 50, player_number=1)
        self.players.append(self.player1)

        # Debug: mostrar animaciones disponibles
        self.player1.print_available_animations()

        # Jugador 2 (si es modo 2 jugadores)
        if num_players == 2:
            self.player2 = Player(self.game.width - 150, self.game.height // 2, player_number=2)
            self.players.append(self.player2)
            self.player2.print_available_animations()

    def handle_events(self, events):
        """Maneja eventos de la escena"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene('menu')

    def update(self, dt):
        """Actualiza la lógica del juego"""
        keys = pygame.key.get_pressed()

        # Actualizar cada jugador
        for player in self.players:
            player.update(dt, keys)

        # Aquí puedes agregar lógica de colisiones, pelota, etc.

    def draw(self, surface):
        """Dibuja la escena"""
        # Dibujar fondo
        surface.blit(self.background, (0, 0))

        # Dibujar jugadores
        for player in self.players:
            player.draw(surface)

        # Debug: mostrar FPS
        if hasattr(self.game, 'clock'):
            fps = int(self.game.clock.get_fps())
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f'FPS: {fps}', True, (255, 255, 255))
            surface.blit(fps_text, (10, 10))