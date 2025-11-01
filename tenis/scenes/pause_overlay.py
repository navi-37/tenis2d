import pygame
import os


class PauseOverlay:
    """Overlay de pausa que se muestra sobre cualquier escena al presionar ESC"""

    def __init__(self, game):
        self.game = game
        self.active = False

        # Cargar imágenes de botones y overlay
        self._load_images()

        # Crear máscaras para detección de hover
        self.mask_salir = pygame.mask.from_surface(self.boton_salir)
        self.mask_menu = pygame.mask.from_surface(self.boton_menu)

        # Cargar sonido de clic
        sound_path = "assets/sonidos"
        self.click_sound = pygame.mixer.Sound(os.path.join(sound_path, "mouse-click.mp3"))

        # Captura de pantalla para el fondo congelado
        self.frozen_screen = None

    def _load_images(self):
        """Carga las imágenes de los botones y el overlay"""
        img_path = "assets/img"
        size = (self.game.width, self.game.height)

        def load_scale(filename):
            img = pygame.image.load(os.path.join(img_path, filename))
            img = img.convert_alpha()
            return pygame.transform.scale(img, size)

        # Overlay de fondo
        self.overlay_background = load_scale("FondoCelesteTransparente.png")

        # Botones de pausa
        self.boton_salir = load_scale("botonEscSalir.png")
        self.boton_salir_apretado = load_scale("botonEscSalirAPRETADO.png")
        self.boton_menu = load_scale("botonEscVolverMenu.png")
        self.boton_menu_apretado = load_scale("botonEscVolverMenuAPRETADO.png")

    def toggle(self, current_surface=None):
        """Activa o desactiva la pausa"""
        self.active = not self.active

        # Si se activa la pausa, capturar la pantalla actual
        if self.active and current_surface:
            self.frozen_screen = current_surface.copy()

    def _mouse_local(self):
        """Obtiene la posición del mouse"""
        mx, my = pygame.mouse.get_pos()
        return int(mx), int(my)

    def _check_button_hover(self, mask):
        """Verifica si el mouse está sobre un botón usando su máscara"""
        local_x, local_y = self._mouse_local()
        w, h = mask.get_size()
        if 0 <= local_x < w and 0 <= local_y < h:
            try:
                return mask.get_at((local_x, local_y))
            except IndexError:
                return False
        return False

    def handle_events(self, events):
        """Maneja los eventos cuando la pausa está activa"""
        if not self.active:
            return False  # No consumir eventos si no está activo

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Despausar con ESC
                    self.toggle()
                    return True  # Evento consumido

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Click en botón Salir
                if self._check_button_hover(self.mask_salir):
                    self.click_sound.play()
                    pygame.time.wait(200)
                    pygame.quit()
                    exit()

                # Click en botón Volver al Menú
                elif self._check_button_hover(self.mask_menu):
                    self.click_sound.play()
                    pygame.time.wait(100)
                    self.active = False
                    self.game.change_scene('menu')
                    return True  # Evento consumido

        return True  # Consumir todos los eventos mientras está pausado

    def draw(self, surface):
        """Dibuja el overlay de pausa sobre la escena congelada"""
        if not self.active:
            return

        # Dibujar la pantalla congelada
        if self.frozen_screen:
            surface.blit(self.frozen_screen, (0, 0))

        # Dibujar overlay personalizado con transparencia
        surface.blit(self.overlay_background, (0, 0))

        # Dibujar botones con efecto hover
        boton_salir_actual = (self.boton_salir_apretado if self._check_button_hover(self.mask_salir)
                              else self.boton_salir)
        boton_menu_actual = (self.boton_menu_apretado if self._check_button_hover(self.mask_menu)
                             else self.boton_menu)

        surface.blit(boton_salir_actual, (0, 0))
        surface.blit(boton_menu_actual, (0, 0))