import pygame as pg
import pygame.freetype
import random

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
TILE_SCALE = 3
PIPE_GAP = 200
PIPE_FREQUENCY = 2000
MENU_COLOR = (60, 131, 72)
BUTTON_COLOR = (131, 60, 119)



class Bird(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.load_animation()
        self.image = self.animation[0]
        self.rect = self.image.get_rect(center=(50,SCREEN_HEIGHT // 2))
        self.timer = pg.time.get_ticks()
        self.interval = 200
        self.current_image = 0

        self.gravity = 0.1
        self.speed = 1
        self.jump_force = 5

    def load_animation(self):
        tile_size = 16
        tile_scale = 4

        self.animation = []
        imagesheet = pg.image.load('Flappy Bird Assets\Player\StyleBird1\Bird1-2.png')
        
        for i in range(4):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = imagesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_scale* tile_size, tile_size * tile_scale))
            self.animation.append(image)

    def update(self):
        self.animate()
        self.speed += self.gravity
        self.rect.y += self.speed

    def animate(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.animation):
                self.current_image = 0
            self.image = self.animation[self.current_image]
            self.timer = pg.time.get_ticks()    

    def jump(self):
        self.speed = -self.jump_force               

class Pipe(pg.sprite.Sprite):
    def __init__(self, game, x, y, is_upper):
        super(Pipe, self).__init__()   
        self.image = pg.image.load('Flappy Bird Assets\Pipes.png') 
        self.image = pg.transform.scale(self.image, (90, 400))
        self.speed = 5     
        self.game = game
        self.rect = self.image.get_rect()
        if is_upper:
            self.rect.bottomleft = (x, y - PIPE_GAP // 2)
        else:
            self.rect.topleft = (x, y + PIPE_GAP // 2)    
        # 80 - высота

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.game.score += 1
            self.kill()

class Button(pg.sprite.Sprite):
    def __init__(self, pos, font):
        super().__init__()
        self.image = pg.Surface((450, 100))
        self.image.fill(BUTTON_COLOR)
        self.rect = self.image.get_rect(center=pos)
        self.text_surf, self.text_rect = font.render('Restart', size=40)
        self.text_rect.center = self.rect.center

    def draw(self, target_surf):
        target_surf.blit(self.image, self.rect)
        target_surf.blit(self.text_surf, self.text_rect)
            

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("FlappyBird")
        self.clock = pg.time.Clock()
        self.is_running = False
        self.score = 0
        self.font = pygame.freetype.Font(None, 48)
        self.button = Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.font)
        self.mode = 'GAME'
        self.backgrounds = [pg.image.load(f'Flappy Bird Assets\Background\Background{i}.png') for i in range(1, 6)]
        self.backgrounds = [pg.transform.scale(i, (SCREEN_WIDTH, SCREEN_HEIGHT)) for i in self.backgrounds]
        self.bg_index = 0
        self.background = self.backgrounds[self.bg_index]

        self.bird = Bird()
        self.pipes = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.bird)

        self.SPAWN_PIPE = pg.USEREVENT
        pg.time.set_timer(self.SPAWN_PIPE, PIPE_FREQUENCY)
        self.CHANGE_BG = pg.USEREVENT + 1
        pg.time.set_timer(self.CHANGE_BG, 5000)


        self.run()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            if self.mode == 'GAME':
                self.update()
                self.draw_game()
            else:
                self.draw_menu() 
               
            self.clock.tick(FPS)
        pg.quit()
        quit()

    def draw_menu(self):
        self.screen.fill(MENU_COLOR)
        self.button.draw(self.screen)
        pg.display.flip()

    def stop_game(self):
        self.pipes.empty()
        self.all_sprites.empty()

    def restart_game(self):
        self.all_sprites.add(self.bird)  
        self.bird.rect.center = (50,SCREEN_HEIGHT // 2)
        self.score = 0      

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if self.mode == 'GAME':    
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.bird.jump() 
                if event.type == self.SPAWN_PIPE:
                    self.create_pipe()
                if event.type == self.CHANGE_BG:
                    self.bg_index += 1
                    if self.bg_index == len(self.backgrounds):
                        self.bg_index = 0
                    self.background = self.backgrounds[self.bg_index]  
            else:
                if event.type == pg.MOUSEBUTTONDOWN and self.button.rect.collidepoint(event.pos):
                    self.mode = 'GAME' 
                    self.restart_game()        

    def update(self):
        self.all_sprites.update()
        if pg.sprite.spritecollide(self.bird, self.pipes, False):
            self.mode = 'MENU'
            self.stop_game() 
        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT:
            self.mode = 'MENU'
            self.stop_game()     
    
    def create_pipe(self):
        y_pos = random.randint(200, SCREEN_HEIGHT - 200) 
        upper_pipe = Pipe(self, SCREEN_WIDTH, y_pos, True) 
        lower_pipe = Pipe(self, SCREEN_WIDTH, y_pos, False)       
        self.all_sprites.add(upper_pipe, lower_pipe)  
        self.pipes.add(upper_pipe, lower_pipe)

    def draw_game(self):
        self.screen.blit(self.background, (0,0))
        self.all_sprites.draw(self.screen)
        self.font.render_to(self.screen, (10, 10), str(self.score), (255, 255, 255))
        pg.display.flip()


if __name__ == "__main__":
    game = Game()