import pygame
import os

from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene


class TenisGame:
    """Clase principal del juego"""

    def __init__(self):
        pygame.init()

        # Configuración de ventana
        self.width = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("utuTenis")

        # Control de tiempo
        self.clock = pygame.time.Clock()
        self.running = True

        # Sistema de escenas
        self.scenes = {}
        self.current_scene = None

        # Inicializar escenas
        self.setup_scenes()

    def setup_scenes(self):
        """Inicializa todas las escenas del juego"""
        self.scenes = {
            'menu': MenuScene(self)
        }
        self.current_scene = self.scenes['menu']

    def change_scene(self, scene_name, **kwargs):
        """Cambia a una escena diferente"""
        if scene_name == 'game':
            # Crear nueva instancia de GameScene con parámetros
            num_players = kwargs.get('num_players', 1)
            self.scenes['game'] = GameScene(self, num_players)
            self.current_scene = self.scenes['game']

        elif scene_name == 'menu':
            # Reiniciar el menú
            self.scenes['menu'] = MenuScene(self)
            self.current_scene = self.scenes['menu']

        elif scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]

        else:
            print(f"Advertencia: Escena '{scene_name}' no encontrada")

    def run(self):
        """Loop principal del juego"""
        while self.running:
            # Limitar a 60 FPS y obtener delta time
            dt = self.clock.tick(60)

            # Eventos
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Actualizar escena actual
            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update(dt)
                self.current_scene.draw(self.screen)

            # Actualizar pantalla
            pygame.display.flip()

        pygame.quit()