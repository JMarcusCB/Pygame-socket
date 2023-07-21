import pygame
pygame.init()

# Configurações do botão
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = (255, 255, 255)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT = "Clique aqui"
BUTTON_TEXT_COLOR = (0, 0, 0)
BUTTON_FONT_SIZE = 24
BUTTON_FONT = pygame.font.Font(None, BUTTON_FONT_SIZE)

class Button:
    def __init__(self, x, y, action, 
                 width = BUTTON_WIDTH, height = BUTTON_HEIGHT, 
                 color = BUTTON_COLOR, hover_color = BUTTON_HOVER_COLOR, 
                 text= BUTTON_TEXT, text_color= BUTTON_TEXT_COLOR, 
                 font = BUTTON_FONT):
        
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = font
        self.action = action
        self.is_hovered = False

    def draw(self, screen):
        try:
            if self.is_hovered:
                pygame.draw.rect(screen, self.hover_color, self.rect)
            else:
                pygame.draw.rect(screen, self.color, self.rect)

            font_surface = self.font.render(self.text, True, self.text_color)
            font_rect = font_surface.get_rect(center=self.rect.center)
            screen.blit(font_surface, font_rect)
        except pygame.error:
            pass

        

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()

                