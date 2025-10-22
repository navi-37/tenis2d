import math
import pygame
from engine.game_object import GameObject

import pygame


import math
import pygame

class Ball:
    def __init__(self, x, y, color=(255, 255, 0), speed=10):
        self.x = x
        self.y = y
        self.radius = 15
        self.color = color
        self.speed = speed
        self.vel_x = 0
        self.vel_y = 0
        self.active = False  # pelota en juego
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

        # Altura
        self.z = 0           # altura sobre el suelo
        self.vel_z = 0       # velocidad vertical
        self.gravity = -0.26  # gravedad (negativa para caer)
        self.bounce = 0.8    # rebote vertical
        self.max_z = 200     # altura máxima visible

    # DIBUJO
    def draw(self, surface):
        """Dibuja la pelota y su sombra."""
        # --- Sombra ---
        shadow_scale = max(0.4, 1 - self.z / self.max_z)
        shadow_width = int(self.radius * 2 * shadow_scale)
        shadow_height = int(self.radius * shadow_scale * 0.5)
        shadow_rect = pygame.Rect(
            int(self.x - shadow_width / 2),
            int(self.y - shadow_height / 2),
            shadow_width,
            shadow_height
        )
        pygame.draw.ellipse(surface, (40, 40, 40), shadow_rect)

        # --- Pelota (ajustada por altura) ---
        screen_y = self.y - self.z  # más alto = más arriba visualmente
        scale = 1 + (self.z / self.max_z) * 0.5
        scaled_radius = int(self.radius * scale)
        pygame.draw.circle(surface, self.color, (int(self.x), int(screen_y)), scaled_radius)

    #   MOVIMIENTO
    def update(self, dt):
        if not self.active:
            return

        # Movimiento plano (x, y)
        self.x += self.vel_x
        self.y += self.vel_y
        self.update_rect()

        # Movimiento vertical (altura)
        self.vel_z += self.gravity
        self.z += self.vel_z

        # Rebote contra el suelo
        if self.z <= 0:
            self.z = 0
            self.vel_z *= -self.bounce
            if abs(self.vel_z) < 1:
                self.vel_z = 0

    def update_rect(self):
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    #   CONTROL
    def launch(self, direction="down_right"):
        """Activa la pelota con movimiento inicial controlado."""
        self.active = True

        # Ángulo horizontal
        if direction == "down_right":
            angle = math.radians(30)
        elif direction == "down_left":
            angle = math.radians(-30)
        elif direction == "up_right":
            angle = math.radians(-150)
        elif direction == "up_left":
            angle = math.radians(150)
        else:
            angle = 0

        # Velocidades iniciales
        self.vel_x = self.speed * math.sin(angle)
        self.vel_y = abs(self.speed * math.cos(angle))
        self.vel_z = 10  # pequeño salto inicial

    def stop(self):
        self.active = False
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.z = 0

    #   COLISIONES
    def collides_with(self, player):
        player_rect = pygame.Rect(player.x, player.y, 150, 150)
        return self.rect.colliderect(player_rect)

    def handle_collisions(self, jugador1, jugador2, screen_height):
        if not self.active:
            return

        # --- Colisión con jugador 1 (arriba) ---
        if jugador1.hitting and self.collides_with(jugador1):
            offset = (self.x - (jugador1.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = abs(self.speed * math.cos(angle))  # hacia abajo
            self.vel_z = 8  # salto al golpear

        # --- Colisión con jugador 2 (abajo) ---
        elif jugador2.hitting and self.collides_with(jugador2):
            offset = (self.x - (jugador2.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = -abs(self.speed * math.cos(angle))  # hacia arriba
            self.vel_z = 8  # salto también

        # --- Bordes superior/inferior → punto terminado ---
        if self.y <= 0 or self.y >= screen_height:
            self.active = False
