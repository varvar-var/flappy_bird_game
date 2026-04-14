import pygame as pg
import pygame.freetype
import random

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
PIPE_GAP = 200
PIPE_FREQUENCY = 2000
MENU_COLOR = (60, 131, 72)
BUTTON_COLOR = (131, 60, 119)
WHITE = (255, 255, 255)

class Bird(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.load_animation()
        self.image = self.animation[0]
        self.rect = self.image.get_rect(center=(50, SCREEN_HEIGHT // 2))
        self.timer = pg.time.get_ticks()
        self.animation_interval = 200
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
            image = pg.transform.scale(image, (tile_scale * tile_size, tile_size * tile_scale))
            self.animation.append(image)

    def update(self):
        self.animate()
        self.apply_gravity()
        self.rect.y += self.speed

    def apply_gravity(self):
        self.speed += self.gravity

    def animate(self):
        current_time = pg.time.get_ticks()
        if current_time - self.timer > self.animation_interval:
            self.current_image = (self.current_image + 1) % len(self.animation)
            self.image = self.animation[self.current_image]
            self.timer = current_time

    def jump(self):
        self.speed = -self.jump_force

    def reset(self):
        self.rect.center = (50, SCREEN_HEIGHT // 2)
        self.speed = 1

class Pipe(pg.sprite.Sprite):
    def __init__(self, game, x, y, is_upper):
        super().__init__()   
        
        self.image = pg.image.load('Flappy Bird Assets\Pipes.png')
        self.image = pg.transform.scale(self.image, (90, 400))
        
        if is_upper:
            self.image = pg.transform.flip(self.image, False, True)
        
        self.speed = 5     
        self.game = game
        self.rect = self.image.get_rect()
        
        if is_upper:
            self.rect.bottomleft = (x, y - PIPE_GAP // 2)
        else:
            self.rect.topleft = (x, y + PIPE_GAP // 2)

    def update(self):
        self.rect.x -= self.speed
        
        if self.rect.right < 0:
            self.game.score += 0.5
            self.kill()

class Button:
    def __init__(self, pos, text, font, width=450, height=100):
        self.rect = pg.Rect(0, 0, width, height)
        self.rect.center = pos
        self.color = BUTTON_COLOR
        self.hover_color = (150, 80, 140)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, target_surf):
        color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(target_surf, color, self.rect, border_radius=12)
        pg.draw.rect(target_surf, WHITE, self.rect, 3, border_radius=12)
        
        text_surf, text_rect = self.font.render(self.text, size=40)
        text_rect.center = self.rect.center
        target_surf.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def check_click(self, pos, event_type):
        return self.rect.collidepoint(pos) and event_type == pg.MOUSEBUTTONDOWN

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Flappy Bird")
        self.clock = pg.time.Clock()
        self.is_running = False
        self.menu_bg = pg.image.load('Flappy Bird Assets/backgraund_menu.jpg')
        self.menu_bg = pg.transform.scale(self.menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.score = 0
        self.font = pygame.freetype.Font('Flappy Bird Assets/ofont.ru_Fet.ttf', 48)
        self.mode = 'GAME'
        
        self.load_backgrounds()
        
        self.bird = Bird()
        self.pipes = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.all_sprites.add(self.bird)
        
        self.restart_button = Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 'Restart', self.font)
        
        self.setup_timers()
        
        self.create_pipe()
        
        self.run()

    def load_backgrounds(self):
        self.backgrounds = []
        for i in range(1, 6):
            bg = pg.image.load(f'Flappy Bird Assets\Background\Background{i}.png')
            bg = pg.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.backgrounds.append(bg)
        
        self.bg_index = 0
        self.background = self.backgrounds[self.bg_index]

    def setup_timers(self):
        self.SPAWN_PIPE = pg.USEREVENT
        self.CHANGE_BG = pg.USEREVENT + 1
        
        pg.time.set_timer(self.SPAWN_PIPE, PIPE_FREQUENCY)
        pg.time.set_timer(self.CHANGE_BG, 5000)

    def run(self):
        self.is_running = True
        while self.is_running:
            self.handle_events()
            
            if self.mode == 'GAME':
                self.update()
                self.draw_game()
            else:
                self.draw_menu()
               
            self.clock.tick(FPS)
        
        pg.quit()

    def draw_menu(self):
        self.screen.blit(self.menu_bg, (0, 0))
        self.font.render_to(self.screen, (10,10), f'record: {self.get_record()}', WHITE)
        self.restart_button.draw(self.screen)
        pg.display.flip()

    def stop_game(self):
        self.pipes.empty()
        self.all_sprites.empty()

    def restart_game(self):
        self.all_sprites.add(self.bird)
        self.bird.reset()
        self.score = 0
        self.create_pipe()

    def handle_events(self):
        mouse_pos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            
            if self.mode == 'GAME':    
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    self.bird.jump()
                elif event.type == self.SPAWN_PIPE:
                    self.create_pipe()
                elif event.type == self.CHANGE_BG:
                    self.change_background()
            else:
                self.restart_button.check_hover(mouse_pos)
                
                if event.type == pg.MOUSEBUTTONDOWN and self.restart_button.check_click(mouse_pos, event.type):
                    self.mode = 'GAME'
                    self.restart_game()

    def change_background(self):
        self.bg_index = (self.bg_index + 1) % len(self.backgrounds)
        self.background = self.backgrounds[self.bg_index]

    def update(self):
        self.all_sprites.update()
        
        if pg.sprite.spritecollide(self.bird, self.pipes, False) or \
           self.bird.rect.top <= 0 or \
           self.bird.rect.bottom >= SCREEN_HEIGHT:
            if self.score > self.get_record():
                self.add_record()
            self.mode = 'MENU'
            self.stop_game()

    def get_record(self):
        with open('record.txt', 'r') as f:
            return int(f.read())       

    def add_record(self):
        with open('record.txt', 'w') as f:
            f.write(str(int(self.score))) 

    def create_pipe(self):
        y_pos = random.randint(200, SCREEN_HEIGHT - 200)
        
        upper_pipe = Pipe(self, SCREEN_WIDTH, y_pos, True)
        lower_pipe = Pipe(self, SCREEN_WIDTH, y_pos, False)
        
        self.all_sprites.add(upper_pipe, lower_pipe)
        self.pipes.add(upper_pipe, lower_pipe)

    def draw_game(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.font.render_to(self.screen, (10, 10), str(int(self.score)), WHITE)
        pg.display.flip()

if __name__ == "__main__":
    game = Game()

