import os
import math
import pygame
from engine.game_object import GameObject
from tenis.entities.bot_player import BotPlayer


class Ball(GameObject):
    def __init__(self, x, y, speed=12):
        json_path = os.path.join("assets", "sprites", "pelota.json")
        super().__init__(x, y, json_path, player_number=0, variant="ball")

        self.speed = speed
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0
        self.z = 0
        self.gravity = -0.25
        self.bounce = 0.8
        self.min_rebound = 5
        self.max_z = 200
        self.active = False
        self.last_hit_by = None  # 1 o 2
        self.bounce_count = 0
        self.in_bounds = True
        self.first_bounce_registered = False
        self.first_bounce_in_bounds = True
        self.first_bounce_side = None  # 'top' | 'bottom'
        self.prev_x = x
        self.prev_y = y
        self.hit_net = False
        self.end_reason = None  # 'net' | 'first_bounce_out' | 'double_bounce' | 'out_top' | 'out_bottom'
        self.hit_lock_until = 0  # cooldown de golpe (ms)
        self.bounce_lock_until = 0  # ms
        self.colliding_p1 = False  # estado de contacto previo con P1
        self.colliding_p2 = False  # estado de contacto previo con P2

        print(f"🎾 Pelota cargada. Animaciones: {list(self.animations.keys())}")

    def update(self, dt):
        if not self.active:
            return
        super().update(dt)

        # guardar Y previa ANTES de mover (se usa para chequear cruce de red)
        prev_y = getattr(self, "prev_y", self.y)
        prev_z = self.z

        # Movimiento plano
        self.x += self.vel_x
        self.y += self.vel_y

        # Movimiento vertical
        self.vel_z += self.gravity
        self.z += self.vel_z

        scene = getattr(self.game, "current_scene", None)
        # EDGE de pique: cruza de z>0 a z<=0
        just_touched_ground = (prev_z > 0 and self.z <= 0)

        if scene and just_touched_ground:
            now = pygame.time.get_ticks()
            if now >= getattr(self, "bounce_lock_until", 0):
                # igual que el HIT: una sola línea
                scene.sfx_bounce.play()
                # pequeño lock para evitar dobles si el frame siguiente también cae en 0
                self.bounce_lock_until = now + 80

        #RED solo en el aire y antes del primer pique
        if scene and self.bounce_count == 0:
            red_y = scene.red_y
            crossed = (prev_y - red_y) * (self.y - red_y) <= 0
            if crossed and self.z >= getattr(scene, "net_clearance", 8):
                self.passed_net = True
            band = 12
            if crossed and ((abs(self.y - red_y) <= band) or (abs(prev_y - red_y) <= band)) \
                    and (0.1 < self.z < getattr(scene, "net_clearance", 8)):
                self.hit_net = True
                self.active = False
                self.rect.x = self.x
                self.rect.y = self.y - self.z
                self.prev_y = self.y
                return

        #si la pelota se pierde de la pantalla
        screen_w = getattr(self.game, "width", 99999)
        screen_h = getattr(self.game, "height", 99999)

        # margen para que "desaparezca"
        off_margin = 90
        out_of_view = (
                self.x < -off_margin or self.x > screen_w + off_margin or
                self.y < -off_margin or self.y > screen_h + off_margin
        )

        if out_of_view:
            if self.bounce_count == 0:
                # se fue antes del primer pique → falta del sacador (la escena lo resuelve)
                self.end_reason = "serve_out"
                self.active = False
            else:
                # se fue luego del 1er pique → contarlo como doble pique
                self.bounce_count = max(self.bounce_count, 2)
                self.end_reason = "out_after_first"
                self.active = False
            # asegurá rect para cálculo/dibujo siguiente ciclo (opcional)
            self.rect.x = self.x
            self.rect.y = self.y - self.z
            return

        # Bote
        if self.z <= 0:
            self.z = 0
            self.vel_z *= -self.bounce
            if self.vel_z < self.min_rebound:
                self.vel_z = self.min_rebound
            self.bounce_count += 1
            self.last_bounce_pos = (self.x, self.y)

            # lado del pique con la línea horizontal
            if scene:
                self.court_side = 'top' if self.y < scene.red_y else 'bottom'
            else:
                self.court_side = 'top' if self.y < (self.game.height / 2) else 'bottom'

            # primer pique
            if not self.first_bounce_registered:
                self.first_bounce_registered = True
                self.first_bounce_in_bounds = self.in_bounds
                self.first_bounce_side = self.court_side

            #primer pique malo
            if (hasattr(self, "hit_side") and
                    self.first_bounce_side == self.hit_side and
                    not getattr(self, "passed_net", False)):
                self.end_reason = "same_side_first_bounce"
                self.active = False
                # asegurar rect y cortar el update
                self.rect.x = self.x
                self.rect.y = self.y - self.z
                return

            # Dentro / fuera (polígono)
            self.in_bounds = self.check_in_bounds()

            # Primer pique
            if not self.first_bounce_registered:
                self.first_bounce_registered = True
                self.first_bounce_in_bounds = self.in_bounds
                self.first_bounce_side = self.court_side

            # Primer pique fuera → fin del rally
            if self.bounce_count == 1 and not self.in_bounds:
                self.active = False

            #Doble pique → fin del rally (la escena define el ganador con last_hit_by)
            elif self.bounce_count >= 2:
                self.active = False

        # Actualizar rect SIEMPRE
        self.rect.x = self.x
        self.rect.y = self.y - self.z
        self.prev_y = self.y

    def draw(self, surface):
        if self.current_animation not in self.animations:
            return

        # Frame según altura (0..3)
        frame_index = int((self.z / self.max_z) * 3)
        frame_index = max(0, min(frame_index, 3))

        x, y, w, h = self.animations[self.current_animation][frame_index]
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w, h))

        #calcular "suelo" exacto del sprite usando mask
        mask = pygame.mask.from_surface(frame)
        rects = mask.get_bounding_rects()
        if rects:
            bbox = rects[0]
            bottom_in_frame = bbox.bottom
        else:
            bottom_in_frame = h

        # top-left donde se blitea el frame en pantalla
        screen_y = self.y - self.z
        draw_top = screen_y - h // 2

        # y del contacto con el suelo en pantalla
        ground_y = draw_top + bottom_in_frame

        #sombra con desplazamiento por altura
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

        #dibujar pelota
        surface.blit(frame, (self.x - w // 2, draw_top))

    def launch(self, direction=None):
        """Saque con un poco más de potencia SOLO en el launch."""
        self.active = True
        self.set_animation("bounce", loop=True)
        #simular golpe al sacar

        scene = getattr(self.game, "current_scene", None)
        if scene and hasattr(scene, "sfx_hit"):
            scene.sfx_hit.play()

        # Más diagonal
        angle_deg = 40
        rad = math.radians(angle_deg)

        #boost solo para el saque
        launch_boost = 1.20

        s = float(self.speed) * launch_boost

        if direction is None:
            direction = "down_right" if self.y < self.game.height / 2 else "up_left"

        if direction == "down_right":
            self.vel_x = s * math.cos(rad)
            self.vel_y = s * math.sin(rad)
        elif direction == "up_left":
            self.vel_x = -s * math.cos(rad)
            self.vel_y = -s * math.sin(rad)
        else:
            self.vel_x = 0
            self.vel_y = s

        self.vel_z = 10

    def stop(self):
        self.active = False
        self.vel_x = self.vel_y = self.vel_z = 0
        self.z = 0

    def collides_with(self, player):
        #collider más grande (centrado)
        size = 70
        half = size // 2
        ball_rect = pygame.Rect(int(self.x) - half, int(self.y - self.z) - half, size, size)
        player_rect = player.get_hitbox()
        return ball_rect.colliderect(player_rect)

    def handle_collisions(self, jugador1, jugador2, screen_height):
        if not self.active:
            return
        now = pygame.time.get_ticks()
        scene = getattr(self.game, "current_scene", None)


        #detectar intersección
        c1 = jugador1.hitting and self.collides_with(jugador1)
        c2 = jugador2.hitting and self.collides_with(jugador2)
        # JUGADOR 1
        if c1 and not self.colliding_p1 and now >= self.hit_lock_until:
            #no permitir golpes antes del primer pique
            if self.bounce_count == 0:
                return
            # (edge-trigger: acabamos de entrar en contacto)
            offset = (self.x - (jugador1.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = abs(self.speed * math.cos(angle))
            self.vel_z = 8
            self.bounce_count = 0
            self.last_hit_by = 1
            hit_side = 'top' if (scene and (self.y < scene.red_y)) else \
                ('top' if self.y < (self.game.height / 2) else 'bottom')
            self.hit_side = hit_side
            self.passed_net = False
            #lock de golpe para evitar dobles sonidos
            self.hit_lock_until = now + 140
            #El bot tiene mas fuerza
            if isinstance(jugador1, BotPlayer):
                self.vel_y *= 1.16
                self.vel_z += 2.3
            #SFX HIT (una sola vez)
            if scene:
                scene.sfx_hit.play()

        #JUGADOR 2
        elif c2 and not self.colliding_p2 and now >= self.hit_lock_until:
            #no permitir golpes antes del primer pique
            if self.bounce_count == 0:
                return
            offset = (self.x - (jugador2.x + 75)) / 75
            offset = max(-1, min(1, offset))
            angle = offset * (math.pi / 4)
            self.vel_x = self.speed * math.sin(angle)
            self.vel_y = -abs(self.speed * math.cos(angle))
            self.vel_z = 8
            self.bounce_count = 0
            self.last_hit_by = 2
            hit_side = 'top' if (scene and (self.y < scene.red_y)) else \
                ('top' if self.y < (self.game.height / 2) else 'bottom')
            self.hit_side = hit_side
            self.passed_net = False
            self.hit_lock_until = now + 140
            if scene:
                scene.sfx_hit.play()

        # Actualizar flags de contacto
        self.colliding_p1 = c1
        self.colliding_p2 = c2

    def check_in_bounds(self):
        """Verifica si la pelota picó dentro del polígono de la cancha."""
        scene = getattr(self.game, "current_scene", None)
        if not scene or not hasattr(scene, "court_polygon"):
            return True  # fallback por si no hay cancha definida

        poly = scene.court_polygon
        x, y = self.x, self.y
        inside = False

        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-6) + xi):
                inside = not inside
            j = i
        return inside


