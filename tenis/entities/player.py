import pygame
import os
from engine.game_object import GameObject


class Player(GameObject):
    """Jugador con controles y animaciones"""

    def __init__(self, x, y, player_number=1):
        json_path = os.path.join('assets', 'sprites', f'player_{player_number}.json')
        super().__init__(x, y, json_path)

        self.velocidad = 8
        self.player_number = player_number

        # Mapear nombres de animaciones genéricas a las que están en el JSON
        self._detect_animations()
        self.last_direction = 'idle'

    def _detect_animations(self):
        self.anims = {}

        animation_map = {
            'idle': ['idle'],
            'walk_left': ['walk_left'],
            'walk_right': ['walk_right'],
            'walk_up': ['walk_up'],
            'walk_down': ['walk_down'],
            'hit_left': ['hit_left'],
            'hit_right': ['hit_right']
        }

        for key, possible_names in animation_map.items():
            for name in possible_names:
                if name in self.animations:
                    self.anims[key] = name
                    break

        # Después de detectar anims normales
        if 'idle' in self.animations:
            idle_frames = self.animations['idle']
            # Suponiendo tu JSON: primer frame para right, segundo para left
            if len(idle_frames) >= 2:
                self.animations['idle_right'] = [idle_frames[0]]
                self.animations['idle_left'] = [idle_frames[1]]
            else:
                # Si solo hay un idle, duplicamos para ambos
                self.animations['idle_right'] = idle_frames
                self.animations['idle_left'] = idle_frames

    def handle_input(self, keys):
        """Maneja el input del jugador y actualiza animación"""
        moving = False

        # Movimiento horizontal
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.velocidad
            self.last_direction = 'left'
            if self.current_animation != self.anims.get('walk_left', ''):
                self.set_animation(self.anims.get('walk_left', 'idle'))
            moving = True

        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.velocidad
            self.last_direction = 'right'
            if self.current_animation != self.anims.get('walk_right', ''):
                self.set_animation(self.anims.get('walk_right', 'idle'))
            moving = True

        # Movimiento vertical
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.velocidad
            if self.last_direction == 'right':
                if self.current_animation != self.anims.get('walk_right', ''):
                    self.set_animation(self.anims.get('walk_right', 'idle'))
            elif self.last_direction == 'left':
                if self.current_animation != self.anims.get('walk_left', ''):
                    self.set_animation(self.anims.get('walk_left', 'idle'))
            moving = True

        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.velocidad
            if self.last_direction == 'left':
                if self.current_animation != self.anims.get('walk_left', ''):
                    self.set_animation(self.anims.get('walk_left', 'idle'))
            elif self.last_direction == 'right':
                if self.current_animation != self.anims.get('walk_right', ''):
                    self.set_animation(self.anims.get('walk_right', 'idle'))
            moving = True

        # Acción de golpe
        if keys[pygame.K_SPACE]:
            if self.last_direction == 'idle':
                self.set_animation(self.anims['hit_right'])
            elif self.last_direction == 'left':
                self.set_animation(self.anims['hit_left'])
            elif self.last_direction == 'right':
                self.set_animation(self.anims['hit_right'])
            moving = True

        # Si no hay movimiento, poner idle según última dirección
        if not moving:
            if self.last_direction == 'left':
                self.set_animation('idle_left')
            elif self.last_direction == 'right':
                self.set_animation('idle_right')
            else:
                self.set_animation(self.anims.get('idle', 'idle'))

    def update(self, dt, keys=None):
        """Actualiza el jugador"""
        if keys:
            self.handle_input(keys)

        # Llamar al update de la clase padre para manejar animaciones
        super().update(dt)


    def print_available_animations(self):
        """Método de debug para ver qué animaciones están disponibles"""
        print(f"\n=== Player {self.player_number} - Animaciones disponibles ===")
        print(f"Animaciones en JSON: {list(self.animations.keys())}")
        print(f"Mapeo de controles: {self.anims}")
        print(f"Animación actual: {self.current_animation}")
        print("=" * 50)