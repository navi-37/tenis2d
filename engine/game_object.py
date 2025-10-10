import pygame
import json
import os


class GameObject:
    """Clase base para objetos animados del juego"""

    def __init__(self, x, y, json_path):
        self.x = x
        self.y = y
        self.sprite_sheet = None
        self.animations = {}
        self.current_animation = 'idle'
        self.frame_index = 0
        self.rect = None
        self.frame_time = 0
        self.frame_duration = 150  # ms por frame

        self.load_from_json(json_path)

    def load_from_json(self, json_path):
        """Carga spritesheet y animaciones desde JSON"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Cargar imagen del spritesheet
            json_dir = os.path.dirname(os.path.abspath(json_path))
            spritesheet_filename = os.path.basename(data.get('spritesheet_path'))
            spritesheet_path = os.path.join(json_dir, spritesheet_filename)
            self.sprite_sheet = pygame.image.load(spritesheet_path).convert_alpha()

            # Cargar animaciones
            for anim_name, frames_data in data.get('animations', {}).items():
                # Convertir dict a lista si es necesario
                if isinstance(frames_data, dict):
                    frames_data = [frames_data]

                self.animations[anim_name] = [
                    (f['x'], f['y'], f['width'], f['height'])
                    for f in frames_data
                ]

            if not self.animations:
                raise ValueError("No hay animaciones en el JSON")

            # Configurar animación inicial
            self.set_animation('idle')

        except Exception as e:
            print(f"Error cargando {json_path}: {e}")
            raise

    def set_animation(self, anim_name):
        if not self.animations:
            print("No hay animaciones cargadas.")
            return

        if anim_name not in self.animations:
            # fallback seguro
            anim_name = list(self.animations.keys())[0]
            print(f" Animación '{anim_name}' no encontrada, usando '{anim_name}'")

        self.current_animation = anim_name
        self.frame_index = 0
        self.frame_time = 0

        # Garantizar que rect exista
        x, y, w, h = self.animations[self.current_animation][0]
        if not self.rect:
            self.rect = pygame.Rect(self.x, self.y, w, h)
        else:
            self.rect.update(self.x, self.y, w, h)

    def update(self, dt):
        """Actualiza la animación según el tiempo transcurrido"""
        if not self.animations or self.current_animation not in self.animations:
            return

        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time -= self.frame_duration
            frames = self.animations[self.current_animation]
            self.frame_index = (self.frame_index + 1) % len(frames)

        # Actualizar posición del rect
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        """Dibuja el frame actual"""
        if not self.sprite_sheet or not self.animations:
            return

        if self.current_animation not in self.animations:
            return

        x, y, w, h = self.animations[self.current_animation][self.frame_index]
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h))
        frame = pygame.transform.scale(frame, (300, 300)) # reescalado del sprite
        surface.blit(frame, self.rect)
