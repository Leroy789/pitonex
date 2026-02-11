import pygame
import random
import sys


pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -18
PLAYER_SPEED = 8
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_COUNT = 12


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (60, 179, 113)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
BACKGROUND = (135, 206, 235)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дудл Джамп")
clock = pygame.time.Clock()


font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)

class Player:
    def __init__(self, start_platform_y):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = start_platform_y - self.height - 1
        self.vel_y = 0
        self.vel_x = 0
        self.is_jumping = False
        self.color = RED
        self.invincible = True
        self.invincible_timer = 100
        
    def update(self, platforms):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.color = RED
        
      
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        
        self.x += self.vel_x
        
        
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
            
        
        for platform in platforms:
            if (self.vel_y >= 0 and 
                self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + platform.height + 5 and  
                self.x + self.width > platform.x + 5 and  
                self.x < platform.x + platform.width - 5):
                
               
                self.y = platform.y - self.height
                self.vel_y = JUMP_FORCE 
                self.is_jumping = True
                platform.hit = True
                
        
        if self.y > HEIGHT + 200:  
            return False
            
        return True
        
    def draw(self, surface):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
            
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 0, 10)
        pygame.draw.circle(surface, WHITE, (int(self.x + self.width * 0.3), int(self.y + self.height * 0.3)), 8)
        pygame.draw.circle(surface, WHITE, (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3)), 8)
        pygame.draw.circle(surface, BLACK, (int(self.x + self.width * 0.3), int(self.y + self.height * 0.3)), 4)
        pygame.draw.circle(surface, BLACK, (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3)), 4)

class Platform:
    def __init__(self, x, y, is_start=False):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.color = GREEN if not is_start else BLUE  
        self.hit = False
        self.is_start = is_start
        
    def update(self, player_vel_y):
        if player_vel_y < 0:
            self.y -= player_vel_y
            
    def draw(self, surface):
        color = YELLOW if self.hit else self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height), 0, 5)
        if self.is_start:
            pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 3, 5)

def create_platforms():
    platforms = []
    start_x = WIDTH // 2 - PLATFORM_WIDTH // 2
    start_y = HEIGHT - 150
    start_platform = Platform(start_x, start_y, is_start=True)
    platforms.append(start_platform)
    min_distance = 80 
    max_distance = 150 
    
    current_y = start_y - 100  
    
    for i in range(PLATFORM_COUNT - 1):
        x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
        
      
        platforms.append(Platform(x, current_y))
        
    
        current_y -= random.randint(min_distance, max_distance)
        
       
        if current_y < 100:
            current_y = HEIGHT - 200
        
    return platforms, start_platform.y

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_safe_zone(surface):   
    pygame.draw.rect(surface, (0, 255, 0, 50), (0, HEIGHT - 100, WIDTH, 100))
    draw_text(screen, "БЕЗОПАСНАЯ ЗОНА", small_font, GREEN, WIDTH // 2, HEIGHT - 50)

def main():
    platforms, start_platform_y = create_platforms()
    player = Player(start_platform_y)
    
    score = 0
    game_over = False
    high_score = 0
    safe_zone_active = True
    safe_zone_timer = 300
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.vel_x = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.vel_x = PLAYER_SPEED
                if event.key == pygame.K_SPACE:
                    player.vel_y = JUMP_FORCE * 0.7  
                if event.key == pygame.K_r and game_over:
                    platforms, start_platform_y = create_platforms()
                    player = Player(start_platform_y)
                    score = 0
                    game_over = False
                    safe_zone_active = True
                    safe_zone_timer = 300
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.vel_x = 0
        
        if not game_over:
            if safe_zone_active:
                safe_zone_timer -= 1
                if safe_zone_timer <= 0:
                    safe_zone_active = False
            
            alive = player.update(platforms)
            
            if not alive:
                game_over = True
                if score > high_score:
                    high_score = score
                
            
            for platform in platforms:
                platform.update(player.vel_y)
                
               
                if platform.y > HEIGHT + 100:
                    if not platform.is_start:
                        platform.x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
                        platform.y = -50
                        platform.hit = False
                       
                        rand_color = random.random()
                        if rand_color > 0.8:
                            platform.color = BLUE
                        elif rand_color > 0.6:
                            platform.color = ORANGE
                        else:
                            platform.color = GREEN
                        
                        if not safe_zone_active:  
                            score += 1
            
           
            if player.y < HEIGHT // 3 and player.vel_y < 0:
                for platform in platforms:
                    platform.y -= player.vel_y
                player.y -= player.vel_y
                if not safe_zone_active: 
                    score += 2
        
        
        screen.fill(BACKGROUND)
        
       
        if safe_zone_active:
            draw_safe_zone(screen)
            
        
        for platform in platforms:
            platform.draw(screen)
            
       
        player.draw(screen)
        
        
        draw_text(screen, f"Счет: {score}", font, BLACK, WIDTH // 2, 30)
        draw_text(screen, f"Рекорд: {high_score}", small_font, BLACK, WIDTH // 2, 70)
        
       
        debug_info = f"Y: {int(player.y)}, VelY: {player.vel_y:.1f}"
        draw_text(screen, debug_info, small_font, BLACK, WIDTH // 2, HEIGHT - 100)
        
        
        if not game_over:
            draw_text(screen, "Управление: ← → или A D, Пробел - прыжок", small_font, BLACK, WIDTH // 2, HEIGHT - 40)
            
           
            if safe_zone_active:
                seconds_left = safe_zone_timer // 60
                draw_text(screen, f"Безопасная зона: {seconds_left} сек", small_font, GREEN, WIDTH // 2, 100)
                
           
            if player.invincible:
                draw_text(screen, "СТАРТОВАЯ ПЛАТФОРМА", small_font, BLUE, WIDTH // 2, 130)
        else:
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "ИГРА ОКОНЧЕНА", font, RED, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(screen, f"Ваш счет: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, f"Рекорд: {high_score}", small_font, YELLOW, WIDTH // 2, HEIGHT // 2 + 40)
            draw_text(screen, "Нажмите R для рестарта", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 80)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
