# engine/ui.py
import pygame
from tenis.scenes.pause_overlay import PauseOverlay

class Scene:
    def __init__(self, game):
        self.game = game
        # Sistema de pausa integrado en todas las escenas
        self.pause_overlay = PauseOverlay(game)
        self.pausable = False

    def handle_events(self, events):
        """
        Maneja eventos con soporte de pausa integrado.
        """
        # Primero verificar si se presiona ESC para pausar
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not self.pause_overlay.active:
                    self.pause_overlay.toggle(self.game.screen)
                    return

        # Si la pausa está activa, dejar que maneje los eventos
        if self.pause_overlay.handle_events(events):
            return  # Eventos consumidos por la pausa

        # Llamar a la implementación específica de la escena
        self._handle_events_impl(events)

    def update(self, dt):
        """
        Actualiza la escena. No actualiza si está pausado.
        """
        # No actualizar si está pausado
        if self.pause_overlay.active:
            return

        # Llamar a la implementación específica de la escena
        self._update_impl(dt)

    def draw(self, surface):
        """
        Dibuja la escena con la pausa al final.
        """
        # Dibujar la escena normal
        self._draw_impl(surface)

        # Dibujar la pausa al final (sobre todo)
        self.pause_overlay.draw(surface)


class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 40)
        self.color = (50, 50, 80)
        self.hover_color = (80, 80, 110)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))