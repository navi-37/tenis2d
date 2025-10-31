import pygame
import os
from engine.game_object import GameObject


class Player(GameObject):
    """Jugador con controles y animaciones"""
    def __init__(self, x, y, player_number=1, variant=1, control_scheme='wasd'):
        self.player_number = player_number
        self.variant = variant
        self.character_name = f"player {player_number}_{variant}"

        # Ruta al JSON unificado
        json_path = os.path.join('assets', 'sprites', 'players.json')

        # Llamar al GameObject con los parámetros correctos
        super().__init__(x, y, json_path, player_number, variant)

        # Configuración del jugador
        self.velocidad = 8
        self.control_scheme = control_scheme
        self.scaled_size = 300
        self._is_hitting = False
        self.vertical_idle_side = 'right'
        self.last_direction = 'idle'
        self.foot_offset = 290

        # Guardar posición previa para colisiones
        self.prev_x = x
        self.prev_y = y

        # Detectar animaciones disponibles
        self._detect_animations()

    def _detect_animations(self):
        """Detecta qué animaciones están disponibles en el JSON"""
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

        # Crear variantes de idle para cada dirección
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
        # Si estamos golpeando, no procesar movimiento ni cambiar animaciones
        if self._is_hitting:
            return

        moving = False

        # Elegir esquema de controles
        if self.control_scheme == 'wasd':
            left = keys[pygame.K_a]
            right = keys[pygame.K_d]
            up = keys[pygame.K_w]
            down = keys[pygame.K_s]
        else:  # esquema de flechas
            left = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            up = keys[pygame.K_UP]
            down = keys[pygame.K_DOWN]

        # Actualizar posición
        if left:
            self.x -= self.velocidad
            self.last_direction = 'left'
            moving = True
        elif right:
            self.x += self.velocidad
            self.last_direction = 'right'
            moving = True

        if up:
            self.y -= self.velocidad
            moving = True
        elif down:
            self.y += self.velocidad
            moving = True

        # Cambiar animación según movimiento
        if left:
            anim = self.anims.get('walk_left', 'idle')
            if self.current_animation != anim:
                self.set_animation(anim)
        elif right:
            anim = self.anims.get('walk_right', 'idle')
            if self.current_animation != anim:
                self.set_animation(anim)
        elif up or down:
            desired_anim = f'walk_{self.last_direction}' if self.last_direction in ['left', 'right'] else 'walk_right'
            if self.current_animation != self.anims.get(desired_anim):
                self.set_animation(self.anims.get(desired_anim, 'idle'))
        elif not moving:
            if self.last_direction == 'left':
                self.set_animation('idle_left')
            elif self.last_direction == 'right':
                self.set_animation('idle_right')
            else:
                self.set_animation('idle')

    def handle_keydown(self, key):
        """Marca que se debe iniciar la animación de golpe al presionar la tecla"""
        if self.control_scheme == 'wasd' and key == pygame.K_SPACE:
            self._start_hit()
        elif self.control_scheme == 'arrows' and (key == pygame.K_SLASH or key == pygame.K_RCTRL):
            self._start_hit()

    def _start_hit(self):
        """Inicia la animación de golpe"""
        # Determinar dirección del golpe
        if self.last_direction == 'left':
            anim_name = 'hit_left'
        else:
            anim_name = 'hit_right'

        # Verificar que la animación existe
        if anim_name in self.animations:
            # IMPORTANTE: loop=False para que la animación no se repita
            self.set_animation(anim_name, loop=False)
            self._is_hitting = True

    def update(self, dt, keys=None):
        """Actualiza el jugador"""
        if keys:
            self.handle_input(keys)

        # Actualizamos animación y mask
        super().update(dt)

        # Detectar cuando termina la animación de hit
        if self._is_hitting and self.animation_finished:
            self._is_hitting = False
            # Volver a idle según la última dirección
            if self.last_direction == 'left':
                self.set_animation('idle_left')
            elif self.last_direction == 'right':
                self.set_animation('idle_right')
            else:
                self.set_animation('idle')

    def print_available_animations(self):
        """Método de debug para ver qué animaciones están disponibles"""
        print(f"\n=== Player {self.player_number}_{self.variant} - Animaciones disponibles ===")
        print(f"Animaciones en JSON: {list(self.animations.keys())}")
        print(f"Mapeo de controles: {self.anims}")
        print(f"Animación actual: {self.current_animation}")
        print("=" * 50)