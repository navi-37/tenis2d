import pygame
from engine.ui import Scene
from tenis.entities.player import Player


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
        self.character1 = character1
        self.character2 = character2

        # Debug: mostrar qué se recibió
        print(f"\n🎮 GameScene inicializado:")
        print(f"   num_players: {num_players}")
        print(f"   character1: {character1}")
        print(f"   character2: {character2}")

        # Crear Player 1
        # El jugador 1 siempre usa sprites de "player 1" con la variante seleccionada
        variant1 = character1 if character1 is not None else 1
        print(f"   Creando Player 1: player_number=1, variant={variant1}")

        self.player1 = Player(
            450, 50,
            player_number=1,
            variant=variant1,
            control_scheme='wasd'
        )
        self.players.append(self.player1)
        self.player1.print_available_animations()

        # Crear Player 2 (si corresponde)
        if num_players == 2:
            # El jugador 2 siempre usa sprites de "player 2" con la variante seleccionada
            variant2 = character2 if character2 is not None else 1
            print(f"   Creando Player 2: player_number=2, variant={variant2}")

            self.player2 = Player(
                1100, 750,
                player_number=2,
                variant=variant2,
                control_scheme='arrows'
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

    def _handle_events_impl(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Pasar al jugador el evento de input
                for player in self.players:
                    player.handle_keydown(event.key)

    def _update_impl(self, dt):
        keys = pygame.key.get_pressed()

        for player in self.players:
            player.prev_x = player.x
            player.prev_y = player.y

        for player in self.players:
            player.update(dt, keys)

        self.handle_net_collision()
        self.handle_gradas_collision()
        self.handle_screen_bounds()

        # ========== PARA TESTEAR EL GAMEOVER ==========
        now = pygame.time.get_ticks()
        if now - self.test_timer >= self.test_duration:

            # CASO 1: 2 jugadores, gana jugador 1
            #self.game.change_scene('gameover', num_players=2, winner=1)

            # CASO 2: 2 jugadores, gana jugador 2
            # self.game.change_scene('gameover', num_players=2, winner=2)

            # CASO 3: 1 jugador, gana el humano (jugador 1)
            # self.game.change_scene('gameover', num_players=1, winner=1)

            # CASO 4: 1 jugador, gana la CPU (jugador 2)
            self.game.change_scene('gameover', num_players=1, winner=2)

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
        for player in self.players:
            # Laterales
            if player.x < 0:
                player.x = 0
            elif player.x + sprite_width > self.game.width:
                player.x = self.game.width - sprite_width

            # Arriba/abajo
            if player.y < 0:
                player.y = 0
            elif player.y + sprite_height > self.game.height:
                player.y = self.game.height - sprite_height

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

        # Dibujar jugadores delante de la red
        for p in players_front:
            p.draw(surface)

        # Debug FPS
        if hasattr(self.game, 'clock'):
            fps = int(self.game.clock.get_fps())
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f'FPS: {fps}', True, (255, 255, 255))
            surface.blit(fps_text, (10, 10))