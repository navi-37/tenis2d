import math
import pygame
from tenis.entities.player import Player

class BotPlayer(Player):
    """Jugador CPU avanzado (anticipación y posicionamiento profesional mejorado)."""

    def __init__(self, x, y, player_number=1, variant=1):
        super().__init__(x, y, player_number, variant, control_scheme=None)
        self.game = None
        self.velocidad = 8
        self.cooldown_golpe = 0
        self.center_pos = (900, 130)  # posición base en el centro de su cancha
        self.reaccion_y = 450  # cuándo considera que la pelota viene hacia él
        self.anticipacion = 22  # cuánto predice el rebote
        self.dist_golpe = 280  # rango vertical de golpe
        self.reaccion_x = 240  # rango horizontal de golpe
        self.debug = False

    def update(self, dt, keys=None, ball=None):
        super().update(dt)
        scene = getattr(self.game, "current_scene", None)

        if scene and scene.waiting_for_serve and scene.current_server == 2:
            # Corrección de posición solo si el jugador humano saca
            if self.x < 850 or self.y < 100:
                self.x, self.y = 900, 120  # posicionarse correctamente

        # Sincronización de estado de saque y posición inicial (solo una vez)
        if scene and scene.waiting_for_serve:
            if not hasattr(self, "_ya_posicionado") or not self._ya_posicionado:
                self.last_ball_hit = None
                self.target_x_after_hit = None
                self._waiting_state = pygame.time.get_ticks()
                self._ya_posicionado = True  # evita que se repita cada frame

                # Si el humano (jugador 2) saca
                if scene.current_server == 2:
                    self.x = 980
                    self.y = 130
                    self.last_direction = "left"
                    self.set_animation("idle_left")
                    return

                # Si el bot (jugador 1) saca
                elif scene.current_server == 1:
                    self.x = 900
                    self.y = 120
                    self.last_direction = "right"
                    self.set_animation("idle_right")
                    return
        else:
            # Reiniciar flag después del saque
            self._ya_posicionado = False

        # estado recordado del último golpe
        if not hasattr(self, "last_ball_hit"):
            self.last_ball_hit = None
            self.target_x_after_hit = None

        #1)Sin pelota → volver al centro
        if not ball or not ball.active:
            self._volver_al_centro(dt)
            return

        if scene and scene.waiting_for_serve and scene.current_server == 2:
            self.target_x_after_hit = 600
            if self.x > 600:
                self.x -= self.velocidad * 0.4
                self.set_animation("walk_left")

        #2)Detectar nuevo golpe del jugador
        # Si la pelota cambió de "last_hit_by" (el otro jugador golpeó)
        if ball.last_hit_by != self.last_ball_hit and ball.last_hit_by is not None:
            self.last_ball_hit = ball.last_hit_by

            # Si el que pegó es el jugador humano (2)
            if ball.last_hit_by == 2:
                # Predecir trayectoria horizontal
                # Estimamos dónde cruzará la línea del bot (Y menor)
                if ball.vel_y < 0:
                    time_to_reach_bot = abs((self.y - ball.y) / (ball.vel_y if ball.vel_y != 0 else -1))
                    predicted_x = ball.x + ball.vel_x * time_to_reach_bot
                    # limitar para no irse fuera
                    predicted_x = max(400, min(predicted_x, 1500))
                    self.target_x_after_hit = predicted_x
                else:
                    self.target_x_after_hit = ball.x

        #3)Movimiento con predicción acotada y zona segura
        zona_limite_y = 220  # máximo avance permitido del bot
        if self.target_x_after_hit is not None:
            dx = self.target_x_after_hit - self.x
            # Predice con menos agresividad la vertical
            predicted_y = ball.y + (ball.vel_y * 0.3)
            dy = predicted_y - self.y

            if self.y > zona_limite_y:
                self.y = zona_limite_y

            # Velocidad más controlada según dirección de la pelota
            if ball.vel_y < 0:
                speed_factor = 1.0  # pelota viene hacia él → rápido
            else:
                speed_factor = 0.35  # pelota va hacia abajo → tranquilo

            # Movimiento horizontal
            if abs(dx) > 4:
                factor = min(1.1, max(0.4, abs(dx) / 240))  # más piso y menos límite
                step = self.velocidad * factor * (1 if dx > 0 else -1)
                self.x += step
                self.last_direction = "right" if dx > 0 else "left"
                self.set_animation(f'walk_{self.last_direction}')

            # Movimiento vertical
            if abs(dy) > 8 and self.y > 60:
                step_y = self.velocidad * 0.25 * speed_factor * (1 if dy > 0 else -1)
                self.y += step_y

            # Frenar cuando ya está cerca del punto ideal
            if abs(dx) < 6 and abs(dy) < 6:
                self.target_x_after_hit = None
                self.set_animation("idle_right")

        else:
            # Seguimiento continuo en defensa (cuando la pelota viene)
            if ball.vel_y < 0 and ball.y < self.y + self.reaccion_y:
                dx = ball.x - self.x
                dy = ball.y - self.y

                factor = min(1.0, max(0.3, abs(dx) / 320))
                self.x += self.velocidad * factor * (1 if dx > 0 else -1)
                self.last_direction = "right" if dx > 0 else "left"

                # Pequeño ajuste vertical, pero no se acerque demasiado a la red
                if self.y > zona_limite_y:
                    self.y -= self.velocidad * 0.2
                elif abs(dy) > 150:
                    self.y += self.velocidad * 0.15 * (1 if dy > 0 else -1)

                self.set_animation(f'walk_{self.last_direction}')
            else:
                self._volver_al_centro(dt)

        #4) Ajuste leve vertical
        if ball.vel_y < -4 and ball.y < self.y:
            self.y -= self.velocidad * 0.2

        #5) Golpe automático
        if (ball.vel_y < 0 and
                abs(ball.y - self.y) < self.dist_golpe and
                abs(ball.x - self.x) < self.reaccion_x and
                ball.z < 90 and
                self.cooldown_golpe <= 0):
            # Paso hacia adelante antes del golpe
            self.y += 12  # impulso moderado
            self._start_hit()
            self.cooldown_golpe = 520
            self.last_direction = "right" if ball.x > self.x else "left"

        #6) cooldown
        if self.cooldown_golpe > 0:
            self.cooldown_golpe -= dt

    def _volver_al_centro(self, dt):
        """Regresa al centro suavemente sin movimientos bruscos."""
        cx, cy = self.center_pos
        dx, dy = cx - self.x, cy - self.y
        dist = math.hypot(dx, dy)
        if dist > 10:
            self.x += (dx / dist) * (self.velocidad * 0.55)
            self.y += (dy / dist) * (self.velocidad * 0.55)
            self.last_direction = "right" if dx > 0 else "left"
            anim = self.anims.get(f'walk_{self.last_direction}', 'idle')
            self.set_animation(anim)
        else:
            self.set_animation("idle_right")
