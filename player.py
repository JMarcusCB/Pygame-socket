import pygame

class Player():
    def __init__(self, x, y, tamanho: tuple, id) -> None:
        self.id = id
        try:
            # DISPLAY SURFACE
            self.surface = pygame.display.get_surface()

            # RECT
            self.image = pygame.Surface((tamanho[0], tamanho[1]))
            self.rect = self.image.get_rect()

            self.rect.x = x
            self.rect.y = y

            self.speed = 3
            self.direction = pygame.Vector2(x/self.speed, y/self.speed)
        except pygame.error as e:
            print("Erro ao inicializar o jogador:", e)

    def update(self):
        try:
            self.rect.x = self.direction.x * self.speed
            self.rect.y = self.direction.y * self.speed
            self.move()
        except AttributeError as e:
            print("Erro ao atualizar jogador:", e)

    def set_position(self, x, y):
        try:
            self.rect.x = int(x)
            self.rect.y = int(y)
            return {"pos": {"x": self.rect.x, "y": self.rect.y}}
        except ValueError as e:
            print("Erro ao definir posição do jogador:", e)
            return None

    def get_position(self):
        return {"pos": {"x": self.rect.x, "y": self.rect.y}}

    def move(self):
        try:
            key = pygame.key.get_pressed()

            if key[pygame.K_UP]:
                self.direction.y -= 1

            if key[pygame.K_DOWN]:
                self.direction.y += 1

            if key[pygame.K_LEFT]:
                self.direction.x -= 1

            if key[pygame.K_RIGHT]:
                self.direction.x += 1

            if key[pygame.K_i]:
                print(self.id)
        except pygame.error as e:
            print("Erro ao mover jogador:", e)

    def draw(self):
        try:
            self.image.fill((255, 255, 255))
            self.surface.blit(self.image, (self.rect.x, self.rect.y))
        except pygame.error as e:
            print("Erro ao desenhar jogador:", e)
