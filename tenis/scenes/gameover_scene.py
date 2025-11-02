import pygame
import os
from engine.ui import Scene


class GameOverScene(Scene):
    """Escena de Game Over con botones y mensajes personalizados"""

    def __init__(self, game, num_players=1, winner=1):
        super().__init__(game)
        self.game = game
        self.num_players = num_players
        self.winner = winner

        # Fuente para el mensaje
        base_path = os.path.dirname(os.path.dirname(__file__))
        font_path = os.path.join(base_path, "assets", "fonts", "Minecraft.ttf")
        self.font = pygame.font.Font(font_path, 60)

        # Cargar imágenes
        self._load_images()

        # Cargar sonidos
        self._load_sounds()

        # Crear máscaras para los botones
        self.mask_menu = pygame.mask.from_surface(self.boton_menu)
        self.mask_salir = pygame.mask.from_surface(self.boton_salir)

        # Generar mensaje y reproducir sonido según resultado
        self._setup_result()

    def _load_images(self):
        img_path = "assets/img"
        size = (self.game.width, self.game.height)

        def load_scale(filename, convert_alpha=False):
            img = pygame.image.load(os.path.join(img_path, filename))
            img = img.convert_alpha() if convert_alpha else img.convert()
            return pygame.transform.scale(img, size)

        self.background = load_scale("utuTenisPantalla.png")
        self.game_over_img = load_scale("game_over.png", True)

        self.boton_menu = load_scale("botonMenu.png", True)
        self.boton_menu_apretado = load_scale("botonMenuAPRETADO.png", True)
        self.boton_salir = load_scale("botonSalir.png", True)
        self.boton_salir_apretado = load_scale("botonSalirAPRETADO.png", True)

    def _load_sounds(self):
        sound_path = "assets/sonidos"

        self.level_up_sound = pygame.mixer.Sound(os.path.join(sound_path, "level-up-05.mp3"))
        self.losing_sound = pygame.mixer.Sound(os.path.join(sound_path, "losing-horn.mp3"))
        self.cheers_sound = pygame.mixer.Sound(os.path.join(sound_path, "crowd-cheers.mp3"))
        self.click_sound = pygame.mixer.Sound(os.path.join(sound_path, "mouse-click.mp3"))

    def _setup_result(self):
        if self.num_players == 2:
            self.message = f"Felicitaciones Jugador {self.winner}, ganaste!"
            self.level_up_sound.play()
        else:
            if self.winner == 2:
                self.message = "Ganaste! :)"
                self.cheers_sound.play()
            else:
                self.message = "Perdiste! :("
                self.losing_sound.play()

        self.message_surf = self.font.render(self.message, True, (255, 255, 255))

        print(f"\n🎮 GAME OVER:")
        print(f"   Jugadores: {self.num_players}")
        print(f"   Ganador: {self.winner}")
        print(f"   Mensaje: {self.message}\n")

    def _mouse_local(self):
        mx, my = pygame.mouse.get_pos()
        return int(mx), int(my)

    def _check_button_hover(self, mask):
        local_x, local_y = self._mouse_local()
        w, h = mask.get_size()
        if 0 <= local_x < w and 0 <= local_y < h:
            try:
                return mask.get_at((local_x, local_y))
            except IndexError:
                return False
        return False

    def _handle_events_impl(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._check_button_hover(self.mask_menu):
                    self.click_sound.play()
                    pygame.time.wait(200)
                    self.game.change_scene('menu')

                elif self._check_button_hover(self.mask_salir):
                    self.click_sound.play()
                    pygame.time.wait(200)
                    pygame.quit()
                    exit()

    def _update_impl(self, dt):
        pass

    def _draw_impl(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.game_over_img, (0, 0))

        boton_menu_actual = (self.boton_menu_apretado if self._check_button_hover(self.mask_menu)
                             else self.boton_menu)
        boton_salir_actual = (self.boton_salir_apretado if self._check_button_hover(self.mask_salir)
                              else self.boton_salir)

        surface.blit(boton_menu_actual, (0, 0))
        surface.blit(boton_salir_actual, (0, 0))

        message_rect = self.message_surf.get_rect(
            center=(self.game.width // 2, self.game.height // 1.33)
        )
        surface.blit(self.message_surf, message_rect)