import pygame
import random
import math
from engine.ui import Scene
from tenis.entities.player import Player
from tenis.entities.ball import Ball


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
            # En modo 1 jugador:
            # - character1 es el que eligió el usuario, pero debe ser el Player 2 (abajo)
            # - Player 1 (arriba, CPU) debe ser aleatorio

            # Generar variante aleatoria para la CPU (Player 1)
            variant1 = random.randint(1, 4)  # Ajusta el rango según tus variantes disponibles

            # El personaje elegido por el usuario va al Player 2
            variant2 = character1 if character1 is not None else 1

            print(f"   Modo 1 jugador:")
            print(f"   Player 1 (CPU): aleatorio = {variant1}")
            print(f"   Player 2 (Usuario): elegido = {variant2}")

        else:
            # En modo 2 jugadores: ambos son elegidos por los usuarios
            variant1 = character1 if character1 is not None else 1
            variant2 = character2 if character2 is not None else 1

            print(f"   Modo 2 jugadores:")
            print(f"   Player 1: {variant1}")
            print(f"   Player 2: {variant2}")

        # Crear Player 1 (arriba)
        print(f"   Creando Player 1: player_number=1, variant={variant1}")
        self.player1 = Player(
            450, 50,
            player_number=1,
            variant=variant1,
            control_scheme='wasd'  # Siempre WASD + V
        )
        self.players.append(self.player1)
        self.player1.print_available_animations()

        # Crear Player 2 (abajo)
        print(f"   Creando Player 2: player_number=2, variant={variant2}")

        # Determinar control_scheme según el modo
        if num_players == 1:
            # En modo 1 jugador: Player 2 es el usuario con Flechas + Espacio
            control = 'arrows_space'
        else:
            # En modo 2 jugadores: Player 2 usa Flechas + L
            control = 'arrows'

        self.player2 = Player(
            1100, 750,
            player_number=2,
            variant=variant2,
            control_scheme=control
        )
        self.players.append(self.player2)
        self.player2.print_available_animations()

        # red y colisión
        self.red_y = self.game.height // 2
        self.red_height = 20

        # acá se crean 2 rectángulos con los que colisiona cada player, están en distinta posición para permitir
        # movimiento más realista (player1 puede quedar "atrás" de la red, player2 la tapa si se aproxima
        self.red_top_surf = pygame.Surface((self.game.width, self.red_height), pygame.SRCALPHA)
        self.red_top_surf.fill((255, 255, 255, 255))
        self.red_top_mask = pygame.mask.from_surface(self.red_top_surf)
        self.red_top_rect = pygame.Rect(0, self.red_y - self.red_height + 50, self.game.width, self.red_height)

        self.red_bottom_surf = pygame.Surface((self.game.width, self.red_height), pygame.SRCALPHA)
        self.red_bottom_surf.fill((255, 255, 255, 255))
        self.red_bottom_mask = pygame.mask.from_surface(self.red_bottom_surf)
        self.red_bottom_rect = pygame.Rect(0, self.red_y - 30, self.game.width, self.red_height)

        self.test_timer = pygame.time.get_ticks()
        self.test_duration = 3000  # 3 segundos
        # Pelota
        self.ball = Ball(self.game.width // 2, self.game.height // 2, speed=6)

        # --- Sistema de puntuación ---
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
        self.server_text_timer = 2000  # 2 segundos

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
            print(f"🎾 Jugador {winner} ganó el set {self.sets[winner]}")

            if self.sets[winner] >= self.max_sets // 2 + 1:
                print(f"🏆 Jugador {winner} ganó el partido!")
                self.game.change_scene('gameover', num_players=self.num_players, winner=winner)

        # mostrar texto de nuevo saque
        self.show_server_text = True
        self.server_start_time = pygame.time.get_ticks()
        self.reset_point()

    def reset_point(self):
        """Reinicia pelota y posiciones de jugadores al comenzar un nuevo punto."""
        self.ball.stop()

        # Posiciones FIJAS de saque (no dependen del jugador)
        if self.current_server == 1:
            self.ball.x, self.ball.y = 650, 300  # saque superior
        else:
            self.ball.x, self.ball.y = 1300, 900  # saque inferior

        # Altura inicial (en el aire)
        self.ball.z = self.ball.max_z * 0.8
        self.ball.vel_z = 0
        self.ball.rect.x = self.ball.x
        self.ball.rect.y = self.ball.y

        # Reset posiciones de jugadores (no se mueven antes del saque)
        self.player1.x, self.player1.y = 450, 50
        self.player1.rect.topleft = (self.player1.x, self.player1.y)
        self.player2.x, self.player2.y = 1300, 750
        self.player2.rect.topleft = (self.player2.x, self.player2.y)

        # Bloquear movimiento hasta que se saque
        self.waiting_for_serve = True
        self.show_server_text = True
        self.server_start_time = pygame.time.get_ticks()

    def _handle_events_impl(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene('menu')

                # Saque según el jugador que sirve
                if self.waiting_for_serve and not self.show_server_text:
                    if self.current_server == 1 and event.key == pygame.K_v:
                        self.ball.launch()
                        self.waiting_for_serve = False
                    elif self.current_server == 2 and event.key == pygame.K_l:
                        self.ball.launch()
                        self.waiting_for_serve = False

                # Solo permitir movimiento si no se está esperando el saque
                if not self.waiting_for_serve:
                    for player in self.players:
                        player.handle_keydown(event.key)

    def _update_impl(self, dt):
        keys = pygame.key.get_pressed()

        # Control del texto de “Saque jugador X”
        if self.show_server_text:
            now = pygame.time.get_ticks()
            if now - self.server_start_time > self.server_text_timer:
                self.show_server_text = False

        # Actualizar jugadores (solo si ya se sacó)
        if not self.waiting_for_serve:
            for player in self.players:
                player.prev_x, player.prev_y = player.x, player.y
                player.update(dt, keys)

        # Actualizar pelota
        was_active = self.ball.active
        self.ball.update(dt)
        self.ball.handle_collisions(self.player1, self.player2, self.game.height)

        # Punto terminado
        if was_active and not self.ball.active:
            if self.ball.y < self.game.height // 2:
                self.add_point(2)
            else:
                self.add_point(1)

        self.handle_net_collision()
        self.handle_gradas_collision()
        self.handle_screen_bounds()

        # ========== PARA TESTEAR EL GAMEOVER ==========
        #  now = pygame.time.get_ticks()
        #   if now - self.test_timer >= self.test_duration:
            # CASO 1: 2 jugadores, gana jugador 1
            # self.game.change_scene('gameover', num_players=2, winner=1)

            # CASO 2: 2 jugadores, gana jugador 2
            # self.game.change_scene('gameover', num_players=2, winner=2)

            # CASO 3: 1 jugador, gana la CPU (jugador 1)
        #     self.game.change_scene('gameover', num_players=1, winner=1)

            # CASO 4: 1 jugador, gana el humano (jugador 2)
            # self.game.change_scene('gameover', num_players=1, winner=2)

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

        # Separar jugadores según sus pies (foot_y)
        players_behind = []
        players_front = []

        # Ajustar el umbral visual donde realmente se ve la red
        # La red visual puede estar más arriba o abajo que self.red_y
        net_visual_y = self.red_y + 200

        for p in self.players:
            foot_y = p.y + getattr(p, 'foot_offset', p.rect.height)

            # Debug: imprime las posiciones
            # print(f"Player {p.player_number}: y={p.y}, foot_y={foot_y}, net_y={net_visual_y}")

            if foot_y < net_visual_y:
                players_behind.append(p)
            else:
                players_front.append(p)

        # Dibujar jugadores detrás de la red
        for p in players_behind:
            p.draw(surface)

        # Dibujar la red
        surface.blit(self.red, (0, 0))

        # Dibujar la pelota(por ahora siempre se ve por arriba de la red)
        self.ball.draw(surface)

        # Dibujar jugadores delante de la red
        for p in players_front:
            p.draw(surface)




        # MARCADOR lateral
        panel_x = self.game.width - 290
        panel_y = 90
        panel_w, panel_h = 280, 90

        # superficie con transparencia
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 180), (0, 0, panel_w, panel_h), border_radius=12)
        surface.blit(panel_surface, (panel_x, panel_y))

        # texto marcador
        text_p1 = self.font_score.render(f"P1: {self.score[1]}  (Sets {self.sets[1]})", True, (93, 56, 255))
        text_p2 = self.font_score.render(f"P2: {self.score[2]}  (Sets {self.sets[2]})", True, (93, 56, 255))

        surface.blit(text_p1, (panel_x + 20, panel_y + 10))
        surface.blit(text_p2, (panel_x + 20, panel_y + 45))

        #TEXTO DE SAQUE con efecto FADE / PARPADEO
        if self.show_server_text:
            elapsed = pygame.time.get_ticks() - self.server_start_time
            alpha = int(255 * abs(math.sin(elapsed / 300)))  # efecto parpadeo suave

            serve_text = f"Saque Jugador {self.current_server}"
            text_surface = self.font_serve.render(serve_text, True, (93, 56, 255))
            text_surface.set_alpha(alpha)

            # dibujar en el centro superior
            text_x = self.game.width // 2 - text_surface.get_width() // 2
            text_y = self.game.height // 2 - text_surface.get_height() // 2
            surface.blit(text_surface, (text_x, text_y))

        # Debug FPS
        if hasattr(self.game, 'clock'):
            fps = int(self.game.clock.get_fps())
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f'FPS: {fps}', True, (255, 255, 255))
            surface.blit(fps_text, (10, 10))