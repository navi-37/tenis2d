import pygame
import random
import math
from engine.ui import Scene
from tenis.entities.player import Player
from tenis.entities.ball import Ball
from tenis.entities.bot_player import BotPlayer


class GameScene(Scene):
    """Escena principal del juego"""

    def __init__(self, game, num_players=1, character1=None, character2=None):
        super().__init__(game)

        # Para que se pueda pausar
        self.pausable = True

        # fondos por capas
        self.gradas = pygame.image.load("assets/img/gradas.png").convert()
        self.cancha = pygame.image.load("assets/img/fondo.png").convert()
        self.red = pygame.image.load("assets/img/red.png").convert_alpha()
        self.gradas = pygame.image.load("assets/img/gradas.png").convert_alpha()

        self.gradas = pygame.transform.scale(self.gradas, (self.game.width, self.game.height))
        self.cancha = pygame.transform.scale(self.cancha, (self.game.width, self.game.height))
        self.red = pygame.transform.scale(self.red, (self.game.width, self.game.height))
        self.gradas = pygame.transform.scale(self.gradas, (self.game.width, self.game.height))

        self.gradas_mask = pygame.mask.from_surface(self.gradas)
        self.gradas_rect = self.gradas.get_rect()

        # jugadores
        self.players = []
        self.num_players = num_players

        # Debug: mostrar qué se recibió
        print(f"\n🎮 GameScene inicializado:")
        print(f"   num_players: {num_players}")
        print(f"   character1 recibido: {character1}")
        print(f"   character2 recibido: {character2}")

        # ===== LÓGICA CORREGIDA PARA SELECCIÓN DE PERSONAJES =====
        if num_players == 1:
            # --- MODO 1 JUGADOR ---
            variant1 = random.randint(1, 4)  # bot aleatorio
            variant2 = character1 if character1 is not None else 1  # elegido por el usuario

            print(f"   Modo 1 jugador:")
            print(f"   Player 1 (CPU): aleatorio = {variant1}")
            print(f"   Player 2 (Usuario): elegido = {variant2}")

            # Player 1 = BOT
            self.player1 = BotPlayer(450, 50, player_number=1, variant=variant1)
            self.player1.game = self.game
            self.players.append(self.player1)
            self.player1.print_available_animations()

            # Player 2 = Usuario (flechas + espacio)
            self.player2 = Player(
                1100, 750,
                player_number=2,
                variant=variant2,
                control_scheme='arrows_space'
            )
            self.players.append(self.player2)
            self.player2.print_available_animations()

        else:
            # En modo 2 jugadores: ambos son elegidos por los usuarios
            variant1 = character1 if character1 is not None else 1
            variant2 = character2 if character2 is not None else 1

            print(f"   Modo 2 jugadores:")
            print(f"   Player 1: {variant1}")
            print(f"   Player 2: {variant2}")

            # Player 1 = Usuario 1 (WASD + V)
            self.player1 = Player(
                450, 50,
                player_number=1,
                variant=variant1,
                control_scheme='wasd'
            )
            self.players.append(self.player1)
            self.player1.print_available_animations()

            # Crear Player 2 (abajo)
            print(f"   Creando Player 2: player_number=2, variant={variant2}")

            ## Player 2 = Usuario 2 (Flechas + L)
            self.player2 = Player(
                1100, 750,
                player_number=2,
                variant=variant2,
                control_scheme='arrows'
            )
            self.players.append(self.player2)
            self.player2.print_available_animations()

        self.test_timer = pygame.time.get_ticks()
        self.test_duration = 3000  # 3 segundos
        # Pelota
        self.ball = Ball(self.game.width // 2, self.game.height // 2, speed=6)
        self.ball.game = self.game

        #Coordenadas de las 4 esquinas de la cancha
        self.court_polygon = [
            (415, 225),  # esquina superior izquierda
            (1510, 225),  # esquina superior derecha
            (1635, 960),  # esquina inferior derecha
            (280, 960)  # esquina inferior izquierda
        ]

        # === Línea central (la "red" lógica) calculada desde el polígono ===
        # mid-left: punto medio entre esquina sup-izq (0) e inf-izq (3)
        ml_x = (self.court_polygon[0][0] + self.court_polygon[3][0]) / 2
        ml_y = (self.court_polygon[0][1] + self.court_polygon[3][1]) / 2
        # mid-right: punto medio entre esquina sup-der (1) e inf-der (2)
        mr_x = (self.court_polygon[1][0] + self.court_polygon[2][0]) / 2
        mr_y = (self.court_polygon[1][1] + self.court_polygon[2][1]) / 2
        self.net_p1 = (ml_x, ml_y)
        self.net_p2 = (mr_x, mr_y)

        # red y colisión
        self.red_y = self.game.height // 2
        self.red_height = 20

        # ancho “visible” de la red (entre líneas blancas superiores)
        net_x_min = min(self.court_polygon[0][0], self.court_polygon[1][0])
        net_x_max = max(self.court_polygon[0][0], self.court_polygon[1][0])
        net_w = int(net_x_max - net_x_min)

        # TOP
        self.red_top_surf = pygame.Surface((net_w, self.red_height), pygame.SRCALPHA)
        self.red_top_surf.fill((255, 255, 255, 255))
        self.red_top_mask = pygame.mask.from_surface(self.red_top_surf)
        self.red_top_rect = pygame.Rect(net_x_min, self.red_y - self.red_height + 50, net_w, self.red_height)

        # BOTTOM
        self.red_bottom_surf = pygame.Surface((net_w, self.red_height), pygame.SRCALPHA)
        self.red_bottom_surf.fill((255, 255, 255, 255))
        self.red_bottom_mask = pygame.mask.from_surface(self.red_bottom_surf)
        self.red_bottom_rect = pygame.Rect(net_x_min, self.red_y - 30, net_w, self.red_height)

        # variables de control de puntos
        self.last_point_reason = None  # "doble pique", "fuera", "red", etc.

        # Sistema de puntuación
        self.score = {1: 0, 2: 0}
        self.sets = {1: 0, 2: 0}
        self.current_server = 1
        self.max_sets = 3
        self.show_server_text = True
        self.server_text_timer = 2000  # ms
        self.server_start_time = pygame.time.get_ticks()
        self.reset_point()
        # Fuente para marcador y avisos
        self.font_score = pygame.font.Font("assets/fonts/pixelmix_bold.ttf", 24)
        self.font_serve = pygame.font.Font("assets/fonts/pixelmix_bold.ttf", 80)

        # temporizador texto de saque
        self.show_server_text = True
        self.server_start_time = pygame.time.get_ticks()
        self.server_text_timer = 3000
        self.first_start = True

        #Feedback en pantalla
        self.feedback_text = None
        self.feedback_color = (255, 255, 255)
        self.feedback_until = 0

        #Sonido
        self.sfx_hit = pygame.mixer.Sound("assets/sonidos/tennis-ball-hit.mp3")
        self.sfx_bounce = pygame.mixer.Sound("assets/sonidos/tennis-ball-bounce.mp3")
        self.sfx_point = pygame.mixer.Sound("assets/sonidos/level-up-05.mp3")
        self.sfx_crowd = pygame.mixer.Sound("assets/sonidos/crowd-cheers.mp3")
        self.sfx_crowd.set_volume(0.8)
        self.flash_until = 0
        self.sfx_hit.set_volume(0.9)
        self.sfx_bounce.set_volume(1.0)
        self.sfx_point.set_volume(0.9)
        # canales dedicados (evita que se pierda sonidos
        self.chan_bounce = pygame.mixer.Channel(2)
        # anti-spam para piques
        self.last_bounce_sfx_ms = 0
        self.bounce_cooldown_ms = 0
        #modo debug
        self.debug_hitboxes = False

    def _net_y_at(self, x):
        """Devuelve la y sobre la línea central para un x dado (interpolación lineal)."""
        (x1, y1), (x2, y2) = self.net_p1, self.net_p2
        if x2 == x1:
            return (y1 + y2) / 2
        t = (x - x1) / (x2 - x1)
        return y1 + t * (y2 - y1)

    def side_of_point(self, x, y):
        """'top' si está por encima de la línea central; 'bottom' si está por debajo."""
        return 'top' if y < self._net_y_at(x) else 'bottom'


    def add_point(self, winner):
        """Actualiza el marcador según quién ganó el punto"""
        score_order = [0, 15, 30, 45]
        loser = 2 if winner == 1 else 1

        current = self.score[winner]
        if current < 45:
            next_index = score_order.index(current) + 1
            self.score[winner] = score_order[next_index]
        else:
            # gana el set
            self.sets[winner] += 1
            self.score = {1: 0, 2: 0}
            self.current_server = loser
            print(f" Jugador {winner} ganó el set {self.sets[winner]}")
            self.sfx_crowd.play(maxtime=3000)
            self.flash_until = pygame.time.get_ticks() + 1000
            # mostrar texto de saque SOLO al empezar un nuevo set
            self.show_server_text = True
            self.server_start_time = pygame.time.get_ticks()
            # marcar que ya no es el primer inicio (pero sí reiniciar el set)
            self.first_start = False
            if self.sets[winner] >= self.max_sets // 2 + 1:
                print(f"Jugador {winner} ganó el partido!")
                self.game.change_scene('gameover', num_players=self.num_players, winner=winner)

        self.reset_point()

    def reset_point(self):
        """Reinicia pelota y posiciones de jugadores al comenzar un nuevo punto."""
        self.ball.stop()

        # Posición FIJA de saque
        if self.current_server == 1:
            self.ball.x, self.ball.y = 725, 270  # arriba
        else:
            self.ball.x, self.ball.y = 1480, 930  # abajo

        # Pelota Altura inicial (en el aire)
        self.ball.z = self.ball.max_z * 0.8
        self.ball.vel_z = 0
        self.ball.rect.x = self.ball.x
        self.ball.rect.y = self.ball.y

        # Posiciones de jugadores
        self.player1.x, self.player1.y = 450, 20
        self.player1.rect.topleft = (self.player1.x, self.player1.y)
        self.player2.x, self.player2.y = 1300, 750
        self.player2.rect.topleft = (self.player2.x, self.player2.y)

        # Bloquear hasta el saque
        self.waiting_for_serve = True

        # Reset de estado de rally
        self.ball.bounce_count = 0
        self.ball.in_bounds = True
        self.ball.last_hit_by = None
        self.ball.passed_net = False
        self.ball.last_bounce_pos = None
        self.ball.first_bounce_registered = False
        self.ball.first_bounce_in_bounds = True
        self.ball.first_bounce_side = None
        self.ball.hit_net = False
        self.last_point_reason = None
        self.point_processed = False
        # Altura mínima para pasar la red (px de z)
        self.net_clearance = 8
        #asegurar estado limpio tras puntos(controlar bugs)
        if hasattr(self.player1, "last_ball_hit"):
            self.player1.last_ball_hit = None
        if hasattr(self.player1, "target_x_after_hit"):
            self.player1.target_x_after_hit = None
        if hasattr(self.player1, "_ya_posicionado"):
            self.player1._ya_posicionado = False
        if hasattr(self.ball, "last_hit_by"):
            self.ball.last_hit_by = None
            self.ball.active = False

    def _handle_events_impl(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene('menu')

                # Saque según servidor
                if self.waiting_for_serve and not self.show_server_text:
                    # si es modo 1 jugador
                    if self.num_players == 1:
                        if event.key == pygame.K_SPACE:
                            if self.current_server == 1:
                                # le toca al bot (P1)
                                self.player1._start_hit()
                                self.ball.launch("down_right")
                                self.ball.last_hit_by = 1
                                self.waiting_for_serve = False
                            else:
                                # le toca al jugador humano (P2)
                                self.ball.launch("up_left")
                                self.ball.last_hit_by = 2
                                self.waiting_for_serve = False
                    # si es modo 2 jugadores
                    else:
                        if self.current_server == 1 and event.key == pygame.K_v:
                            self.ball.launch()
                            self.ball.last_hit_by = 1
                            self.waiting_for_serve = False
                        elif self.current_server == 2 and event.key == pygame.K_l:
                            self.ball.launch()
                            self.ball.last_hit_by = 2
                            self.waiting_for_serve = False

                # Movimiento solo después del saque
                if not self.waiting_for_serve:
                    for player in self.players:
                        player.handle_keydown(event.key)

                if event.type == pygame.KEYDOWN:
                    # alternar modo debug con F3
                    if event.key == pygame.K_F3:
                        self.debug_hitboxes = not self.debug_hitboxes
                        print(f"Debug hitboxes: {'ON' if self.debug_hitboxes else 'OFF'}")

    def _update_impl(self, dt):
        keys = pygame.key.get_pressed()

        # Texto “Saque…”
        if self.first_start:
            self.show_server_text = True
            self.server_start_time = pygame.time.get_ticks()
            self.first_start = False
        if self.show_server_text:
            now = pygame.time.get_ticks()
            if now - self.server_start_time > self.server_text_timer:
                self.show_server_text = False

        # Jugadores solo se mueven tras el saque
        if not self.waiting_for_serve:
            # Si hay bot en modo 1 jugador
            if isinstance(self.player1, BotPlayer):
                # Player 1 = bot (CPU)
                self.player1.prev_x, self.player1.prev_y = self.player1.x, self.player1.y
                self.player1.update(dt, ball=self.ball)  # pasa la pelota al bot
                # Player 2 = usuario
                self.player2.prev_x, self.player2.prev_y = self.player2.x, self.player2.y
                self.player2.update(dt, keys)
            else:
                # modo 2 jugadores: ambos controlados manualmente
                for player in self.players:
                    player.prev_x, player.prev_y = player.x, player.y
                    player.update(dt, keys)

        # Pelota
        was_active = self.ball.active
        self.ball.update(dt)
        self.ball.handle_collisions(self.player1, self.player2, self.game.height)

        # Evitar doble cómputo
        if getattr(self, "point_processed", False):
            return

        if was_active and not self.ball.active:
            self.point_processed = True
            reason = "desconocido"
            hitter = self.ball.last_hit_by if self.ball.last_hit_by in (1, 2) else self.current_server
            opponent = 2 if hitter == 1 else 1
            winner = None

            # 1) red
            if getattr(self.ball, "hit_net", False):
                reason = "red"
                winner = opponent

            # 2) primer pique en el MISMO lado del que golpeó Y NO pasó la red
            elif (self.ball.first_bounce_registered and
                  hasattr(self.ball, "hit_side") and
                  self.ball.first_bounce_side == self.ball.hit_side and
                  not getattr(self.ball, "passed_net", False)):
                reason = "no pasó la red / picó en su lado"
                winner = opponent

            # 3) primer pique fuera
            elif self.ball.first_bounce_registered and not self.ball.first_bounce_in_bounds:
                reason = "primer pique fuera"
                winner = opponent

            # 4) doble pique
            elif self.ball.bounce_count >= 2:
                reason = "doble pique"
                winner = hitter

            # 5) fallback
            if winner is None:
                reason = "indeterminado"
                winner = opponent

            print(f"🎯 Punto para Jugador {winner} ({reason}) | "
                  f"último golpe: {hitter} | bounces={self.ball.bounce_count} | "
                  f"first_in={self.ball.first_bounce_in_bounds} | first_side={self.ball.first_bounce_side}")

            # Mensaje y color según motivo
            reason_map = {
                "red": ("RED Punto P{w}", (255, 90, 90)),
                "no pasó la red / picó en su lado": ("NO PASA LA RED Punto P{w}", (255, 140, 0)),
                "primer pique fuera": ("FUERA (1er pique) Punto P{w}", (255, 120, 120)),
                "doble pique": ("DOBLE PIQUE Punto P{w}", (90, 200, 255)),
                "fuera tras 1er pique (sin devolución)": ("FUERA Punto P{w}", (255, 160, 120)),
                "saque fuera antes del 1er pique": ("SAQUE FUERA Punto P{w}", (255, 120, 120)),
                "indeterminado": ("FUERA Punto P{w}", (220, 120, 120)),
            }

            msg, col = reason_map.get(reason, ("Punto P{w}", (220, 220, 220)))
            self.show_feedback(msg.format(w=winner), color=col, ms=2000)

            self.last_point_reason = reason
            # sonido fin de punto
            self.sfx_point.play()
            self.add_point(winner)
            return

        self.handle_net_collision()
        self.handle_gradas_collision()
        self.handle_screen_bounds()


    def handle_net_collision(self):
        """Detecta colisiones pixel-perfect con la red según el jugador"""
        for player in self.players:
            if not hasattr(player, 'mask') or not player.mask:
                continue

            # Player 1: zona superior
            if player == self.player1:
                offset = (player.rect.x - self.red_top_rect.x,
                          player.rect.y - self.red_top_rect.y)
                if self.red_top_mask.overlap(player.mask, offset):
                    player.x = player.prev_x
                    player.y = player.prev_y
                    player.rect.x = player.x
                    player.rect.y = player.y
                    player.update_mask()

            # Player 2: zona inferior
            elif hasattr(self, 'player2') and player == self.player2:
                offset = (player.rect.x - self.red_bottom_rect.x,
                          player.rect.y - self.red_bottom_rect.y)
                if self.red_bottom_mask.overlap(player.mask, offset):
                    player.x = player.prev_x
                    player.y = player.prev_y
                    player.rect.x = player.x
                    player.rect.y = player.y
                    player.update_mask()

    def handle_gradas_collision(self):
        """Detecta colisiones pixel-perfect con las gradas para evitar que salgan de la cancha"""
        for player in self.players:
            if not hasattr(player, 'mask') or not player.mask:
                continue

            # Calcular offset entre player y gradas
            offset = (player.rect.x - self.gradas_rect.x,
                      player.rect.y - self.gradas_rect.y)

            # Verificar colisión pixel-perfect
            if self.gradas_mask.overlap(player.mask, offset):
                # Revertir posición
                player.x = player.prev_x
                player.y = player.prev_y
                player.rect.x = player.x
                player.rect.y = player.y
                player.update_mask()

    def handle_screen_bounds(self):
        """Evita que los jugadores salgan de la pantalla usando rects"""

        sprite_width, sprite_height = 300, 300  # tamaño escalado

        margin_left = 15
        margin_right = 50
        margin_top = 75
        margin_bottom = 75

        for player in self.players:
            # Laterales
            if player.x < -margin_left:
                player.x = -margin_left
            elif player.x + sprite_width > self.game.width + margin_right:
                player.x = self.game.width + margin_right - sprite_width

            # Arriba/abajo
            if player.y < -margin_top:
                player.y = -margin_top
            elif player.y + sprite_height > self.game.height + margin_bottom:
                player.y = self.game.height + margin_bottom - sprite_height

            player.rect.x = player.x
            player.rect.y = player.y

    def _draw_impl(self, surface):
        """Dibuja la escena con orden correcto respecto a la red"""

        # Dibujar fondo
        surface.blit(self.gradas, (0, 0))
        surface.blit(self.cancha, (0, 0))

        #Parpadeo al ganar un set
        if pygame.time.get_ticks() < getattr(self, "flash_until", 0):
            elapsed = pygame.time.get_ticks()
            flicker_speed = 200
            phase = (elapsed // flicker_speed) % 2
            if phase == 0:
                flash = pygame.Surface((self.game.width, self.game.height))
                flash.fill((120, 200, 255))
                flash.set_alpha(160)
                surface.blit(flash, (0, 0))

        # Separar jugadores según sus pies (foot_y)
        players_behind = []
        players_front = []

        # Ajustar el visual donde realmente se ve la red
        net_visual_y = self.red_y + 200

        for p in self.players:
            foot_y = p.y + getattr(p, 'foot_offset', p.rect.height)
            if foot_y < net_visual_y:
                players_behind.append(p)
            else:
                players_front.append(p)

        # Dibujar jugadores detrás de la red
        for p in players_behind:
            p.draw(surface)

        # Dibujar la red
        surface.blit(self.red, (0, 0))

        # Dibujar la pelota
        self.ball.draw(surface)

        # Dibujar jugadores delante de la red
        for p in players_front:
            p.draw(surface)

        # MARCADOR lateral
        panel_x = self.game.width - 290
        panel_y = 90
        panel_w, panel_h = 280, 90
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 180), (0, 0, panel_w, panel_h), border_radius=12)
        surface.blit(panel_surface, (panel_x, panel_y))
        text_p1 = self.font_score.render(f"P1: {self.score[1]}  (Sets {self.sets[1]})", True, (90, 200, 255))
        text_p2 = self.font_score.render(f"P2: {self.score[2]}  (Sets {self.sets[2]})", True, (90, 200, 255))
        surface.blit(text_p1, (panel_x + 20, panel_y + 10))
        surface.blit(text_p2, (panel_x + 20, panel_y + 45))

        #texto temporal con el motivo del punto (ej: "Fuera", "Doble pique")
        if self.last_point_reason:
            reason_text = self.font_score.render(self.last_point_reason.upper(), True, (255, 255, 255))
            surface.blit(reason_text, (self.game.width // 2 - reason_text.get_width() // 2, 150))

        #Texto de saque con efecto parpadeo
        if self.show_server_text:
            elapsed = pygame.time.get_ticks() - self.server_start_time
            alpha = int(200 + 55 * math.sin(elapsed / 800))
            alpha = max(0, min(255, alpha))
            serve_text = f"Saque Jugador {self.current_server}"
            text_surface = self.font_serve.render(serve_text, True, (110, 220, 255))  # más brillante
            text_surface.set_alpha(alpha)
            shadow_surface = self.font_serve.render(serve_text, True, (0, 0, 0))
            shadow_surface.set_alpha(int(alpha * 0.6))
            text_x = self.game.width // 2 - text_surface.get_width() // 2
            text_y = self.game.height // 2 - text_surface.get_height() // 2
            surface.blit(shadow_surface, (text_x + 3, text_y + 3))
            surface.blit(text_surface, (text_x, text_y))

        #DEBUG VISUAL DE LA CANCHA, PIQUES Y COLIDERS F3
        if self.debug_hitboxes:
            overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            # Cancha translúcida
            pygame.draw.polygon(overlay, (0, 255, 0, 0), self.court_polygon)  # relleno suave
            pygame.draw.lines(overlay, (255, 255, 255, 100), True, self.court_polygon, 2)  # borde blanco tenue
            # Línea de red
            pygame.draw.line(
                overlay, (255, 255, 255, 100),
                (self.court_polygon[0][0], self.red_y),
                (self.court_polygon[1][0], self.red_y),
                2
            )
            #Jugadores
            pygame.draw.rect(overlay, (255, 0, 0, 160), self.player1.get_hitbox(), 2)
            pygame.draw.rect(overlay, (0, 180, 255, 160), self.player2.get_hitbox(), 2)
            # Pelota
            pygame.draw.circle(overlay, (255, 255, 0, 180), (int(self.ball.x), int(self.ball.y - self.ball.z)), 8)
            pygame.draw.rect(
                overlay, (255, 255, 0, 100),
                pygame.Rect(int(self.ball.x) - 20, int(self.ball.y - self.ball.z) - 20, 40, 40),
                1
            )
            # Último pique (si hay)
            if hasattr(self.ball, "last_bounce_pos") and self.ball.last_bounce_pos:
                bx, by = self.ball.last_bounce_pos
                pygame.draw.circle(overlay, (255, 200, 0, 200), (int(bx), int(by)), 10)
            # Dibujar todo el overlay
            surface.blit(overlay, (0, 0))

        #Mensaje de punto
        now = pygame.time.get_ticks()
        if self.feedback_text and now < self.feedback_until:
            # fade suave (opcional)
            remaining = self.feedback_until - now
            alpha = max(0, min(255, int(255 * (remaining / 300)))) if remaining < 300 else 255
            #contenedor
            pad_x, pad_y = 24, 12
            font = self.font_score  # ya la tenés
            text_surf = font.render(self.feedback_text, True, self.feedback_color)
            bx = self.game.width // 2 - (text_surf.get_width() + pad_x * 2) // 2
            by = 160
            bw = text_surf.get_width() + pad_x * 2
            bh = text_surf.get_height() + pad_y * 2
            box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            # fondo semitransparente
            pygame.draw.rect(box, (0, 0, 0, 180), (0, 0, bw, bh), border_radius=12)
            if alpha < 255:
                box.set_alpha(alpha)
            surface.blit(box, (bx, by))
            surface.blit(text_surf, (bx + pad_x, by + pad_y))
        else:
            #limpiar cuando vence
            self.feedback_text = None

        # Debug FPS
        if hasattr(self.game, 'clock'):
            fps = int(self.game.clock.get_fps())
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f'FPS: {fps}', True, (255, 255, 255))
            surface.blit(fps_text, (10, 10))

    def show_feedback(self, text, color=(255, 255, 255), ms=1400):
        self.feedback_text = text
        self.feedback_color = color
        self.feedback_until = pygame.time.get_ticks() + ms
