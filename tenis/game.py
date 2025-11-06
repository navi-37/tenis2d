import os

import pygame

from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene


class TenisGame:
    """Clase principal del juego"""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.set_num_channels(16)

        # Configuración de ventana
        self.width = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("utuTenis")
        icono = pygame.image.load("assets/img/icono.png").convert_alpha()
        pygame.display.set_icon(icono)

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
            character1 = kwargs.get('character1')
            character2 = kwargs.get('character2')

            # Debug: verificar qué se está recibiendo
            print(f"\n🔄 change_scene recibió:")
            print(f"   num_players: {num_players}")
            print(f"   character1: {character1}")
            print(f"   character2: {character2}")

            # Crear GameScene con todos los parámetros
            self.scenes['game'] = GameScene(
                self,
                num_players=num_players,
                character1=character1,
                character2=character2
            )
            self.current_scene = self.scenes['game']

        elif scene_name == 'gameover':
            from scenes.gameover_scene import GameOverScene
            num_players = kwargs.get('num_players', 1)
            winner = kwargs.get('winner', 1)
            self.scenes['gameover'] = GameOverScene(self, num_players, winner)
            self.current_scene = self.scenes['gameover']

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
            # limitar a 60 FPS y obtener delta time
            dt = self.clock.tick(60)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # actualizar escena actual
            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update(dt)
                self.current_scene.draw(self.screen)

            pygame.display.flip()

        pygame.quit()