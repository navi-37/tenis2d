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
        self.scaled_size = 300

        self._is_hitting = False

        # Mapear nombres de animaciones genéricas a las que están en el JSON
        self._detect_animations()
        self.vertical_idle_side = 'right'
        self.last_direction = 'idle'
        self.foot_offset = 290

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
            #print(f"Player {self.player_number}: Iniciando animación {anim_name}")  # Debug
            # IMPORTANTE: loop=False para que la animación no se repita
            self.set_animation(anim_name, loop=False)
            self._is_hitting = True
        #else:
            #print(f"Player {self.player_number}: Animación {anim_name} no encontrada")  # Debug

    def update(self, dt, keys=None):
        """Actualiza el jugador"""
        if keys:
            self.handle_input(keys)

        # DEBUG: Imprimir estado durante hit
        #if self._is_hitting:
        #    print(
        #        f"Player {self.player_number} HIT - Anim: {self.current_animation}, Frame: {self.frame_index}, Finished: {self.animation_finished}")

        # Actualizamos animación y mask
        super().update(dt)

        # Detectar cuando termina la animación de hit
        if self._is_hitting and self.animation_finished:
            print(f"Player {self.player_number}: Finalizando hit")  # Debug
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
        print(f"\n=== Player {self.player_number} - Animaciones disponibles ===")
        print(f"Animaciones en JSON: {list(self.animations.keys())}")
        print(f"Mapeo de controles: {self.anims}")
        print(f"Animación actual: {self.current_animation}")
        print("=" * 50)