import pygame
import json
import os


class GameObject:
    """Clase base para objetos animados del juego"""

    def __init__(self, x, y, json_path, player_number=1, variant=1):
        self.x = x
        self.y = y
        self.sprite_sheet = None
        self.animations = {}
        self.current_animation = 'idle'
        self.frame_index = 0
        self.rect = None
        self.frame_time = 0
        self.frame_duration = 150  # ms por frame
        self.mask = None  # mask para colisiones pixel-perfect

        # Control de loop de animaciones
        self.animation_loop = True  # Por defecto las animaciones hacen loop
        self.animation_finished = False  # Flag para saber si una animación no-loop terminó

        # Cargar desde JSON
        self.load_from_json(json_path, player_number, variant)

    def load_from_json(self, json_path, player_number, variant):
        """Carga las animaciones desde el JSON y el spritesheet"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Cargar spritesheet
        spritesheet_path = os.path.join('assets', 'sprites', data.get("spritesheet_path", "spritesheet.png"))
        if not os.path.exists(spritesheet_path):
            raise FileNotFoundError(f"No se encontró el spritesheet en: {spritesheet_path}")

        self.sprite_sheet = pygame.image.load(spritesheet_path).convert_alpha()

        # Buscar el jugador correcto
        player_name = f"player {player_number}_{variant}"
        player_data = next(
            (p for p in data["players"] if p["character_name"] == player_name),
            None
        )

        if not player_data:
            raise ValueError(f"No se encontró {player_name} en {json_path}")

        # Convertir las animaciones del formato JSON a tuplas (x, y, w, h)
        for anim_name, frames in player_data["animations"].items():
            self.animations[anim_name] = []
            for frame_data in frames:
                # Convertir de diccionario a tupla
                self.animations[anim_name].append((
                    frame_data["x"],
                    frame_data["y"],
                    frame_data["width"],
                    frame_data["height"]
                ))

        # Establecer animación inicial
        if self.animations:
            first_anim = list(self.animations.keys())[0]
            self.set_animation(first_anim)

    def set_animation(self, anim_name, loop=True):
        """
        Cambia la animación actual
        Args:
            anim_name: nombre de la animación
            loop: si True, la animación se repite; si False, se detiene en el último frame
        """
        if not self.animations:
            return

        if anim_name not in self.animations:
            anim_name = list(self.animations.keys())[0]

        self.current_animation = anim_name
        self.frame_index = 0
        self.frame_time = 0
        self.animation_loop = loop
        self.animation_finished = False

        # Configurar rect
        x, y, w, h = self.animations[self.current_animation][0]
        if not self.rect:
            self.rect = pygame.Rect(self.x, self.y, w, h)
        else:
            self.rect.update(self.x, self.y, w, h)

        # Crear mask inicial
        self.update_mask()

    def update(self, dt):
        """Actualiza animación y mask"""
        if not self.animations or self.current_animation not in self.animations:
            return

        # Solo avanzar frames si la animación no ha terminado
        if not self.animation_finished:
            # Convertir dt a milisegundos si está en segundos
            dt_ms = dt * 1000 if dt < 1 else dt

            self.frame_time += dt_ms
            if self.frame_time >= self.frame_duration:
                self.frame_time -= self.frame_duration
                frames = self.animations[self.current_animation]

                if self.animation_loop:
                    # Animación con loop
                    self.frame_index = (self.frame_index + 1) % len(frames)
                else:
                    # Animación sin loop
                    self.frame_index += 1
                    if self.frame_index >= len(frames):
                        self.frame_index = len(frames) - 1
                        self.animation_finished = True

        # Actualizar rect
        self.rect.x = self.x
        self.rect.y = self.y

        # Actualizar mask del frame actual
        self.update_mask()

    def update_mask(self):
        """Genera la mask del frame actual para colisiones pixel-perfect"""
        if not self.sprite_sheet or not self.animations:
            self.mask = None
            return

        x, y, w, h = self.animations[self.current_animation][self.frame_index]
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h))
        frame = pygame.transform.scale(frame, (300, 300))  # mismo reescalado que en draw
        self.mask = pygame.mask.from_surface(frame)

    def draw(self, surface):
        """Dibuja el frame actual"""
        if not self.sprite_sheet or not self.animations or self.current_animation not in self.animations:
            return

        x, y, w, h = self.animations[self.current_animation][self.frame_index]
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h))
        frame = pygame.transform.scale(frame, (300, 300))
        surface.blit(frame, self.rect)