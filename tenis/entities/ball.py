import math
import pygame
from engine.game_object import GameObject

import pygame


class Ball:
    def __init__(self, x, y, color=(255, 255, 255), speed=10):
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

    # Métodos básicos
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self, dt):
        """Actualiza la posición de la pelota."""
        if not self.active:
            return
        self.x += self.vel_x
        self.y += self.vel_y
        self.update_rect()

    def update_rect(self):
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    # Control de estado
    def launch(self, direction="down_right"):
        """Activa la pelota con movimiento inicial controlado."""
        self.active = True

        angle = 0
        if direction == "down":
            angle = 0
        elif direction == "down_right":
            angle = math.radians(30)
        elif direction == "down_left":
            angle = math.radians(-30)
        elif direction == "up_right":
            angle = math.radians(-150)
        elif direction == "up_left":
            angle = math.radians(150)

        # Velocidades iniciales
        self.vel_x = self.speed * math.sin(angle)
        self.vel_y = abs(self.speed * math.cos(angle))

    def stop(self):
        """Detiene la pelota (sin resetear posiciones)."""
        self.active = False
        self.vel_x = 0
        self.vel_y = 0

    # Colisiones
    def collides_with(self, player):
        """Colisión simple basada en rectángulos."""
        player_rect = pygame.Rect(player.x, player.y, 150, 150)
        return self.rect.colliderect(player_rect)

    def handle_collisions(self, jugador1, jugador2, screen_height):
        if not self.active:
            return

        # --- Colisión con jugador 1 (arriba) ---
        if jugador1.hitting and self.collides_with(jugador1):
            offset = (self.x - (jugador1.x + 75)) / 75  # -1 izq, 1 der
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)  # máx 45°
            speed = self.speed
            self.vel_x = speed * math.sin(angle)
            self.vel_y = abs(speed * math.cos(angle))  # hacia abajo

        # --- Colisión con jugador 2 (abajo) ---
        elif jugador2.hitting and self.collides_with(jugador2):
            offset = (self.x - (jugador2.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            speed = self.speed
            self.vel_x = speed * math.sin(angle)
            self.vel_y = -abs(speed * math.cos(angle))  # hacia arriba

        # --- Bordes superior/inferior → punto terminado ---
        if self.y <= 0 or self.y >= screen_height:
            self.active = False