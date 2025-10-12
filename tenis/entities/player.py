import pygame
import os
from engine.game_object import GameObject


class Player(GameObject):
    """Jugador con controles y animaciones"""

    def __init__(self, x, y, player_number=1, control_scheme='wasd'):
        json_path = os.path.join('assets', 'sprites', f'player_{player_number}.json')
        super().__init__(x, y, json_path)

        self.velocidad = 8
        self.player_number = player_number
        self.control_scheme = control_scheme
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
            if len(idle_frames) >= 2:
                self.animations['idle_right'] = [idle_frames[0]]
                self.animations['idle_left'] = [idle_frames[1]]
            else:
                self.animations['idle_right'] = idle_frames
                self.animations['idle_left'] = idle_frames

    def handle_input(self, keys):
        """Maneja el input del jugador según su esquema de control"""
        moving = False

        #elegir esquema de controles
        if self.control_scheme == 'wasd':
            left = keys[pygame.K_a]
            right = keys[pygame.K_d]
            up = keys[pygame.K_w]
            down = keys[pygame.K_s]
            hit = keys[pygame.K_SPACE]
        else:  # esquema de flechas
            left = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            up = keys[pygame.K_UP]
            down = keys[pygame.K_DOWN]
            hit = keys[pygame.K_SLASH] or keys[pygame.K_RCTRL]  # / o Ctrl derecho

        # Movimiento horizontal
        if left:
            self.x -= self.velocidad
            self.last_direction = 'left'
            if self.current_animation != self.anims.get('walk_left', ''):
                self.set_animation(self.anims.get('walk_left', 'idle'))
            moving = True

        elif right:
            self.x += self.velocidad
            self.last_direction = 'right'
            if self.current_animation != self.anims.get('walk_right', ''):
                self.set_animation(self.anims.get('walk_right', 'idle'))
            moving = True

        # Movimiento vertical
        if up:
            self.y -= self.velocidad
            if self.last_direction == 'right':
                if self.current_animation != self.anims.get('walk_right', ''):
                    self.set_animation(self.anims.get('walk_right', 'idle'))
            elif self.last_direction == 'left':
                if self.current_animation != self.anims.get('walk_left', ''):
                    self.set_animation(self.anims.get('walk_left', 'idle'))
            moving = True

        elif down:
            self.y += self.velocidad
            if self.last_direction == 'left':
                if self.current_animation != self.anims.get('walk_left', ''):
                    self.set_animation(self.anims.get('walk_left', 'idle'))
            elif self.last_direction == 'right':
                if self.current_animation != self.anims.get('walk_right', ''):
                    self.set_animation(self.anims.get('walk_right', 'idle'))
            moving = True

        # Acción de golpe
        if hit:
            if self.last_direction == 'idle':
                self.set_animation(self.anims['hit_right'])
            elif self.last_direction == 'left':
                self.set_animation(self.anims['hit_left'])
            elif self.last_direction == 'right':
                self.set_animation(self.anims['hit_right'])
            moving = True

        # Si no hay movimiento, idle según dirección
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