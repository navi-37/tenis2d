import os
import math
import pygame
from engine.game_object import GameObject


class Ball(GameObject):
    def __init__(self, x, y, speed=10):
        json_path = os.path.join("assets", "sprites", "pelota.json")
        super().__init__(x, y, json_path, player_number=0, variant="ball")

        self.speed = speed
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.z = 0
        self.gravity = -0.26
        self.bounce = 0.8
        self.max_z = 200
        self.active = False
        print(f"🎾 Pelota cargada. Animaciones: {list(self.animations.keys())}")

    def update(self, dt):
        if not self.active:
            return
        super().update(dt)

        # Movimiento plano
        self.x += self.vel_x
        self.y += self.vel_y

        # Movimiento vertical
        self.vel_z += self.gravity
        self.z += self.vel_z

        if self.z <= 0:
            self.z = 0
            self.vel_z *= -self.bounce
            if abs(self.vel_z) < 1:
                self.vel_z = 0

        self.rect.x = self.x
        self.rect.y = self.y - self.z

    def draw(self, surface):
        if self.current_animation not in self.animations:
            return

        # Frame según altura (0..3)
        frame_index = int((self.z / self.max_z) * 3)
        frame_index = max(0, min(frame_index, 3))

        x, y, w, h = self.animations[self.current_animation][frame_index]
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h))

        # ---- calcular "suelo" exacto del sprite usando mask ----
        mask = pygame.mask.from_surface(frame)
        rects = mask.get_bounding_rects()
        if rects:
            bbox = rects[0]
            bottom_in_frame = bbox.bottom
        else:
            bottom_in_frame = h  # fallback si el frame está vacío

        # top-left donde se blitea el frame en pantalla
        screen_y = self.y - self.z
        draw_top = screen_y - h // 2

        # y del contacto con el suelo en pantalla
        ground_y = draw_top + bottom_in_frame

        # ---- sombra con desplazamiento por altura ----
        shadow_scale = max(0.25, 1 - (self.z / self.max_z) * 0.8)

        shadow_w = int(w * 0.25 * shadow_scale)
        shadow_h = int(h * 0.15 * shadow_scale)

        # desplazamiento proporcional a la altura z
        # cuanto más alta la pelota, más abajo se proyecta la sombra
        offset_y = int(self.z * 0.7)

        shadow_rect = pygame.Rect(
            int(self.x - shadow_w / 2),
            int(ground_y + offset_y - shadow_h / 2),
            shadow_w,
            shadow_h
        )

        pygame.draw.ellipse(surface, (25, 25, 25, 180), shadow_rect)

        # ---- dibujar pelota ----
        surface.blit(frame, (self.x - w // 2, draw_top))

    def launch(self, direction="down_right"):
        self.active = True
        self.set_animation("bounce", loop=True)

        if direction == "down_right":
            angle = 30
        elif direction == "down_left":
            angle = -30
        elif direction == "up_right":
            angle = -150
        elif direction == "up_left":
            angle = 150
        else:
            angle = 0

        rad = math.radians(angle)
        self.vel_x = self.speed * math.sin(rad)
        self.vel_y = abs(self.speed * math.cos(rad))
        self.vel_z = 10

    def stop(self):
        self.active = False
        self.vel_x = self.vel_y = self.vel_z = 0
        self.z = 0

    # === COLISIONES ===
    def collides_with(self, player):
        player_rect = pygame.Rect(player.x, player.y, 150, 150)
        return self.rect.colliderect(player_rect)

    def handle_collisions(self, jugador1, jugador2, screen_height):
        if not self.active:
            return

        # Colisión con jugador 1
        if jugador1.hitting and self.collides_with(jugador1):
            offset = (self.x - (jugador1.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = abs(self.speed * math.cos(angle))
            self.vel_z = 8

        # Colisión con jugador 2
        elif jugador2.hitting and self.collides_with(jugador2):
            offset = (self.x - (jugador2.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = -abs(self.speed * math.cos(angle))
            self.vel_z = 8

        # Fin del punto
        if self.y <= 0 or self.y >= screen_height:
            self.active = False
