import pygame
import os
from engine.ui import Scene


class MenuScene(Scene):
    """Menú principal con desplazamiento bidireccional fluido"""

    def __init__(self, game):
        super().__init__(game)
        self.game = game

        # Estados
        self.state = "inicio"
        self.selected_players = None
        self.selected_character = None
        self.selected_character2 = None

        # Fade out
        self.fade_alpha = 0
        self.fading = False

        # Fuente
        base_path = os.path.dirname(os.path.dirname(__file__))
        font_path = os.path.join(base_path, "assets", "fonts", "Minecraft.ttf")
        self.font = pygame.font.Font(font_path, 50)
        self.title_surf = self.font.render(
            "Presiona 'ENTER' para continuar", True, (255, 255, 255)
        )

        # Cargar imágenes
        self._load_images()

        # Cargar sonidos
        self._load_sounds()

        # Máscaras hover
        self.mask_boton1 = pygame.mask.from_surface(self.boton1)
        self.mask_boton2 = pygame.mask.from_surface(self.boton2)
        self.personaje_masks = [pygame.mask.from_surface(img) for img in self.personajes_normales]

        # Scroll
        self.x_offset = 0
        self.scroll_speed = 20

        # Timer para pantallas fijas
        self.timer = 0
        self.wait_duration_jugador = 500  # 0.5 segundos para pantallas de jugador
        self.wait_duration_controles = 2500  # 2.5 segundos para pantalla de controles

        # Sistema de columnas dinámico
        self.columns = ["inicio", "seleccion_jugadores"]  # Comienza con estas dos
        self.current_col_index = 0
        self.next_col_index = None

        # Parpadeo del texto de inicio
        self.blink_timer = 0
        self.blink_interval = 500  # 500ms = 0.5 segundos
        self.show_text = True

        # Iniciar música de fondo
        self.background_music.play(loops=-1)  # -1 = loop infinito

    # -------------------- Carga de imágenes --------------------
    def _load_images(self):
        img_path = "assets/img"
        size = (self.game.width, self.game.height)

        def load_scale(filename, convert_alpha=False):
            img = pygame.image.load(os.path.join(img_path, filename))
            img = img.convert_alpha() if convert_alpha else img.convert()
            return pygame.transform.scale(img, size)

        # Fondos y pantallas
        self.background = load_scale("utuTenisPantalla.png")
        self.titulo = load_scale("utuTenisTexto.png", True)
        self.titulojugadores = load_scale("tituloJugadores.png", True)
        self.cancha = load_scale("cancha.png", True)

        # Pantallas intermedias
        self.jugador1_img = load_scale("JUGADOR1.png", True)
        self.jugador2_img = load_scale("JUGADOR2.png", True)
        self.controles1 = load_scale("Controles1.png", True)
        self.controles2 = load_scale("Controles2.png", True)

        # Botones
        self.boton1 = load_scale("boton1jugador.png", True)
        self.boton1apretado = load_scale("boton1jugadorAPRETADO.png", True)
        self.boton2 = load_scale("boton2jugadores.png", True)
        self.boton2apretado = load_scale("boton2jugadoresAPRETADO.png", True)

        # Personajes
        self.personajes_normales = [load_scale(f"J{i}.1.png", True) for i in range(1, 7)]
        self.personajes_hover = [load_scale(f"J{i}.2.png", True) for i in range(1, 7)]

    # -------------------- Carga de sonidos --------------------
    def _load_sounds(self):
        """Carga los efectos de sonido y música de fondo"""
        sound_path = "assets/sonidos"

        # Efecto de clic
        self.click_sound = pygame.mixer.Sound(os.path.join(sound_path, "mouse-click.mp3"))

        # Música de fondo
        pygame.mixer.music.load(os.path.join(sound_path, "game-music-loop-7.mp3"))
        pygame.mixer.music.set_volume(0.1)  # Volumen al 40% !!!!!!!!!!!!!!!

        # Guardar referencia para detener después
        self.background_music = pygame.mixer.music

    # -------------------- Helpers --------------------
    def _mouse_local(self, offset_x):
        mx, my = pygame.mouse.get_pos()
        return int(mx - offset_x), int(my)

    def _check_button_hover(self, mask, offset_x):
        local_x, local_y = self._mouse_local(offset_x)
        w, h = mask.get_size()
        if 0 <= local_x < w and 0 <= local_y < h:
            try:
                return mask.get_at((local_x, local_y))
            except IndexError:
                return False
        return False

    def _check_personaje_hover(self, index, offset_x):
        mask = self.personaje_masks[index]
        local_x, local_y = self._mouse_local(offset_x)
        w, h = mask.get_size()
        if 0 <= local_x < w and 0 <= local_y < h:
            try:
                return mask.get_at((local_x, local_y))
            except IndexError:
                return False
        return False

    # -------------------- Construir flujo dinámico --------------------
    def _build_flow(self, num_players):
        """Construye el flujo de pantallas según la cantidad de jugadores elegida"""
        if num_players == 1:
            # Flujo 1 jugador: inicio -> jugadores -> personaje -> controles
            self.columns = [
                "inicio",
                "seleccion_jugadores",
                "seleccion_personaje_1",
                "controles"
            ]
        else:  # 2 jugadores
            # Flujo 2 jugadores: inicio -> jugadores -> jugador1 -> personaje1 -> jugador2 -> personaje2 -> controles
            self.columns = [
                "inicio",
                "seleccion_jugadores",
                "mostrar_jugador1",
                "seleccion_personaje_1",
                "mostrar_jugador2",
                "seleccion_personaje_2",
                "controles"
            ]

    # -------------------- Eventos --------------------
    def handle_events(self, events):
        current_screen = self.columns[self.current_col_index]

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if current_screen == "inicio":
                    self._start_scroll(self.current_col_index + 1)
                elif current_screen == "controles" and not self.fading:
                    self.fading = True

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col_offset = self.x_offset + self.game.width * self.current_col_index

                # ---------------- Selección de jugadores ----------------
                if current_screen == "seleccion_jugadores":
                    if self._check_button_hover(self.mask_boton1, col_offset):
                        self.click_sound.play()
                        self.selected_players = 1
                        self._build_flow(1)
                        self._start_scroll(self.current_col_index + 1)
                    elif self._check_button_hover(self.mask_boton2, col_offset):
                        self.click_sound.play()
                        self.selected_players = 2
                        self._build_flow(2)
                        self._start_scroll(self.current_col_index + 1)

                # ---------------- Selección personajes ----------------
                elif current_screen in ["seleccion_personaje_1", "seleccion_personaje_2"]:
                    for i in range(6):
                        if self._check_personaje_hover(i, col_offset):
                            self.click_sound.play()
                            if current_screen == "seleccion_personaje_1":
                                self.selected_character = i + 1
                            else:
                                self.selected_character2 = i + 1
                            self._start_scroll(self.current_col_index + 1)
                            break

    # -------------------- Scroll --------------------
    def _start_scroll(self, next_index):
        """Inicia un desplazamiento a la siguiente pantalla"""
        if next_index < len(self.columns):
            self.next_col_index = next_index
            self.state = "desplazando"

    # -------------------- Update --------------------
    def update(self, dt):
        current_screen = self.columns[self.current_col_index]

        # Parpadeo del texto en la pantalla de inicio
        if current_screen == "inicio":
            self.blink_timer += dt
            if self.blink_timer >= self.blink_interval:
                self.show_text = not self.show_text
                self.blink_timer = 0

        # Desplazamiento
        if self.state == "desplazando" and self.next_col_index is not None:
            target_offset = -self.next_col_index * self.game.width
            diff = target_offset - self.x_offset

            # Movimiento suave
            move = max(min(abs(diff), self.scroll_speed), 1) * (1 if diff > 0 else -1)
            self.x_offset += move

            # Chequear si llegó
            if abs(self.x_offset - target_offset) <= 1:
                self.x_offset = target_offset
                self.current_col_index = self.next_col_index
                self.next_col_index = None
                self._on_scroll_end()

        # Pantallas con timer automático (solo mostrar_jugador1 y mostrar_jugador2)
        now = pygame.time.get_ticks()
        if self.state in ["mostrar_jugador1", "mostrar_jugador2"]:
            if now - self.timer >= self.wait_duration_jugador:
                self._start_scroll(self.current_col_index + 1)

        # Pantalla de controles: espera ENTER o 2.5 segundos
        elif self.state == "controles":
            if now - self.timer >= self.wait_duration_controles:
                self.state = "fade_out"
                self.fading = True

        # Fade final
        if self.fading:
            self.fade_alpha += 5
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading = False
                # Detener música antes de cambiar de escena
                pygame.mixer.music.stop()

                print(f"\n🎮 INICIANDO JUEGO:")
                print(f"   Jugadores: {self.selected_players}")
                print(f"   Personaje 1: {self.selected_character}")
                print(f"   Personaje 2: {self.selected_character2}\n")

                self.game.change_scene(
                    "game",
                    num_players=self.selected_players,
                    character1=self.selected_character,
                    character2=self.selected_character2
                )

    # -------------------- Actualización de estado --------------------
    def _on_scroll_end(self):
        """Actualiza el estado después de terminar un desplazamiento"""
        current_screen = self.columns[self.current_col_index]

        if current_screen in ["inicio", "seleccion_jugadores", "seleccion_personaje_1", "seleccion_personaje_2"]:
            self.state = current_screen
        elif current_screen in ["mostrar_jugador1", "mostrar_jugador2", "controles"]:
            self.state = current_screen
            self.timer = pygame.time.get_ticks()

    # -------------------- Draw --------------------
    def draw(self, surface):
        surface.blit(self.background, (0, 0))

        # Dibujar ambas pantallas durante desplazamiento
        if self.state == "desplazando" and self.next_col_index is not None:
            self._draw_screen(surface, self.current_col_index)
            self._draw_screen(surface, self.next_col_index)
        else:
            self._draw_screen(surface, self.current_col_index)

        # Fade final
        if self.fade_alpha > 0:
            fade_surf = self.cancha.copy()
            fade_surf.set_alpha(self.fade_alpha)
            surface.blit(fade_surf, (0, 0))

    # -------------------- Draw por pantalla --------------------
    def _draw_screen(self, surface, col_index):
        """Dibuja una pantalla específica del flujo"""
        if col_index >= len(self.columns):
            return

        screen_name = self.columns[col_index]
        offset = int(self.x_offset + self.game.width * col_index)

        if screen_name == "inicio":
            surface.blit(self.titulo, (offset, 0))
            # Solo dibujar el texto si show_text es True (parpadeo)
            if self.show_text:
                title_rect = self.title_surf.get_rect(
                    center=(surface.get_width() // 2 + self.x_offset, self.game.height // 1.16)
                )
                surface.blit(self.title_surf, title_rect)

        elif screen_name == "seleccion_jugadores":
            surface.blit(self.titulojugadores, (offset, 0))
            boton1_actual = self.boton1apretado if self._check_button_hover(self.mask_boton1, offset) else self.boton1
            boton2_actual = self.boton2apretado if self._check_button_hover(self.mask_boton2, offset) else self.boton2
            surface.blit(boton1_actual, (offset, 0))
            surface.blit(boton2_actual, (offset, 0))

        elif screen_name == "mostrar_jugador1":
            surface.blit(self.jugador1_img, (offset, 0))

        elif screen_name == "mostrar_jugador2":
            surface.blit(self.jugador2_img, (offset, 0))

        elif screen_name in ["seleccion_personaje_1", "seleccion_personaje_2"]:
            for i in range(6):
                img = self.personajes_hover[i] if self._check_personaje_hover(i, offset) else self.personajes_normales[
                    i]
                surface.blit(img, (offset, 0))

        elif screen_name == "controles":
            controles_img = self.controles1 if self.selected_players == 1 else self.controles2
            surface.blit(controles_img, (offset, 0))