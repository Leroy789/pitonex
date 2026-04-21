import pygame
import random
import sys
import math
from enum import Enum

pygame.init()

# Константы игры
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -18
PLAYER_SPEED = 8
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
PLATFORM_COUNT = 12

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (60, 179, 113)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)
BACKGROUND = (135, 206, 235)
DARK_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)

# Типы платформ
class PlatformType(Enum):
    NORMAL = 1
    MOVING = 2
    FRAGILE = 3
    BOUNCE = 4
    ICE = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дудл Джамп")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 72)

class Player:
    def __init__(self, start_platform_y):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = start_platform_y - self.height - 1
        self.vel_y = 0
        self.vel_x = 0
        self.color = RED
        self.on_ground = True
        self.can_jump = True
        self.animation_offset = 0
        self.invincible = True
        self.invincible_timer = 100
        
    def update(self, platforms):
        # Неуязвимость после старта
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Физика
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.x += self.vel_x
        
        # Границы экрана
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
        
        # Анимация
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.01) * 2
        
        # Сбрасываем флаг перед проверкой
        self.on_ground = False
            
        # Проверка столкновений с платформами
        for platform in platforms:
            if (self.vel_y >= 0 and 
                self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + platform.height + 5 and  
                self.x + self.width > platform.x + 5 and  
                self.x < platform.x + platform.width - 5):
                
                self.y = platform.y - self.height
                
                # Разные типы платформ
                if platform.platform_type == PlatformType.BOUNCE:
                    self.vel_y = JUMP_FORCE * 1.5
                elif platform.platform_type == PlatformType.ICE:
                    self.vel_y = JUMP_FORCE
                    self.vel_x *= 1.2
                elif platform.platform_type == PlatformType.FRAGILE:
                    self.vel_y = JUMP_FORCE
                    platform.hit_count += 1
                    if platform.hit_count >= 2:
                        platform.is_broken = True
                else:
                    self.vel_y = JUMP_FORCE
                    
                platform.hit = True
                self.on_ground = True
                self.can_jump = True
                
        if not self.on_ground:
            self.can_jump = False
                
        if self.y > HEIGHT + 200:
            return False
        return True
    
    def jump(self):
        if self.can_jump:
            self.vel_y = JUMP_FORCE
            self.can_jump = False
            self.on_ground = False
            return True
        return False
        
    def draw(self, surface):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
            
        # Рисование игрока
        pygame.draw.rect(surface, self.color, 
                        (self.x, self.y + self.animation_offset, self.width, self.height), 0, 10)
        
        # Глаза
        eye_offset = self.animation_offset
        pygame.draw.circle(surface, WHITE, 
                          (int(self.x + self.width * 0.3), int(self.y + self.height * 0.3 + eye_offset)), 8)
        pygame.draw.circle(surface, WHITE, 
                          (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3 + eye_offset)), 8)
        pygame.draw.circle(surface, BLACK, 
                          (int(self.x + self.width * 0.3), int(self.y + self.height * 0.3 + eye_offset)), 4)
        pygame.draw.circle(surface, BLACK, 
                          (int(self.x + self.width * 0.7), int(self.y + self.height * 0.3 + eye_offset)), 4)

class Platform:
    def __init__(self, x, y, is_start=False, platform_type=PlatformType.NORMAL):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.platform_type = platform_type
        self.is_start = is_start
        self.hit = False
        self.move_direction = 1
        self.move_speed = 2
        self.is_broken = False
        self.hit_count = 0
        
        # Цвета для разных типов
        self.colors = {
            PlatformType.NORMAL: GREEN,
            PlatformType.MOVING: ORANGE,
            PlatformType.FRAGILE: RED,
            PlatformType.BOUNCE: PURPLE,
            PlatformType.ICE: CYAN
        }
        
        if is_start:
            self.color = BLUE
        else:
            self.color = self.colors.get(platform_type, GREEN)
        
    def update(self, player_vel_y):
        if player_vel_y < 0 and not self.is_start:
            self.y -= player_vel_y
            
        # Движущиеся платформы
        if self.platform_type == PlatformType.MOVING and not self.is_start:
            self.x += self.move_speed * self.move_direction
            if self.x <= 50 or self.x + self.width >= WIDTH - 50:
                self.move_direction *= -1
                
    def draw(self, surface):
        if self.is_broken:
            return
            
        color = YELLOW if self.hit else self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height), 0, 5)
        
        # Детали для разных типов платформ
        if self.platform_type == PlatformType.FRAGILE:
            pygame.draw.line(surface, BLACK, (self.x, self.y + self.height//2), 
                           (self.x + self.width, self.y + self.height//2), 2)
        elif self.platform_type == PlatformType.BOUNCE:
            for i in range(3):
                pygame.draw.circle(surface, WHITE, 
                                 (self.x + self.width//2, self.y + self.height - 5), 3)
        elif self.platform_type == PlatformType.ICE:
            pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, 3))
            
        if self.is_start:
            pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 3, 5)

def create_platforms():
    platforms = []
    
    start_x = WIDTH // 2 - PLATFORM_WIDTH // 2
    start_y = HEIGHT - 150
    start_platform = Platform(start_x, start_y, is_start=True)
    platforms.append(start_platform)
    
    # Расстояние между платформами
    min_distance = 100
    max_distance = 200
    
    current_y = start_y - 80
    
    for i in range(PLATFORM_COUNT - 1):
        x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
        
        # Выбор типа платформы
        rand_type = random.random()
        if rand_type < 0.6:
            platform_type = PlatformType.NORMAL
        elif rand_type < 0.75:
            platform_type = PlatformType.MOVING
        elif rand_type < 0.85:
            platform_type = PlatformType.BOUNCE
        elif rand_type < 0.95:
            platform_type = PlatformType.ICE
        else:
            platform_type = PlatformType.FRAGILE
            
        platform = Platform(x, current_y, platform_type=platform_type)
        platforms.append(platform)
        
        current_y -= random.randint(min_distance, max_distance)
        
        if current_y < 80:
            current_y = HEIGHT - 20
        
    return platforms, start_platform.y

def draw_background(surface, scroll):
    """Рисует красивый фон с градиентом и облаками"""
    # Градиентное небо
    for i in range(HEIGHT):
        color_value = 135 + int((i / HEIGHT) * 50)
        color = (color_value, 206 - int((i / HEIGHT) * 50), 235 - int((i / HEIGHT) * 100))
        pygame.draw.line(surface, color, (0, i), (WIDTH, i))
    
    # Облака
    cloud_y = 50 + (scroll * 0.2) % 300
    pygame.draw.ellipse(surface, WHITE, (100, cloud_y, 80, 50))
    pygame.draw.ellipse(surface, WHITE, (140, cloud_y - 20, 80, 50))
    pygame.draw.ellipse(surface, WHITE, (60, cloud_y - 10, 70, 50))
    
    cloud_y2 = 150 + (scroll * 0.3) % 400
    pygame.draw.ellipse(surface, WHITE, (600, cloud_y2, 100, 60))
    pygame.draw.ellipse(surface, WHITE, (650, cloud_y2 - 30, 100, 60))

def draw_text(surface, text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def main():
    platforms, start_platform_y = create_platforms()
    player = Player(start_platform_y)
    
    score = 0
    game_over = False
    high_score = 0
    safe_zone_active = True
    safe_zone_timer = 300
    jump_delay = 0
    jump_cooldown = 10
    scroll_offset = 0
    
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
                    
                if event.key == pygame.K_SPACE and jump_delay <= 0:
                    if player.jump():
                        jump_delay = jump_cooldown
                        
                if event.key == pygame.K_r and game_over:
                    platforms, start_platform_y = create_platforms()
                    player = Player(start_platform_y)
                    score = 0
                    game_over = False
                    safe_zone_active = True
                    safe_zone_timer = 300
                    
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                    player.vel_x = 0
        
        if jump_delay > 0:
            jump_delay -= 1
        
        if not game_over:
            if safe_zone_active:
                safe_zone_timer -= 1
                if safe_zone_timer <= 0:
                    safe_zone_active = False
            
            alive = player.update(platforms)
            scroll_offset = player.y
            
            if not alive:
                game_over = True
                if score > high_score:
                    high_score = score
            
            # Обновление платформ и начисление очков
            for platform in platforms:
                platform.update(player.vel_y)
                
                if platform.y > HEIGHT + 100 and not platform.is_start:
                    platform.x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
                    platform.y = -50
                    platform.hit = False
                    platform.is_broken = False
                    platform.hit_count = 0
                    score += 5
                    
                    # Смена типа при респавне
                    rand_type = random.random()
                    if rand_type < 0.6:
                        platform.platform_type = PlatformType.NORMAL
                    elif rand_type < 0.75:
                        platform.platform_type = PlatformType.MOVING
                    elif rand_type < 0.85:
                        platform.platform_type = PlatformType.BOUNCE
                    elif rand_type < 0.95:
                        platform.platform_type = PlatformType.ICE
                    else:
                        platform.platform_type = PlatformType.FRAGILE
                    platform.color = platform.colors.get(platform.platform_type, GREEN)
            
            if player.y < HEIGHT // 3 and player.vel_y < 0 and not safe_zone_active:
                for platform in platforms:
                    platform.y -= player.vel_y
                player.y -= player.vel_y
                score += 2
        
        # Отрисовка
        draw_background(screen, scroll_offset)
        
        for platform in platforms:
            platform.draw(screen)
        
        player.draw(screen)
        
        # UI
        draw_text(screen, f"Счет: {score}", font, BLACK, WIDTH // 2, 30)
        draw_text(screen, f"Рекорд: {high_score}", small_font, BLACK, WIDTH // 2, 70)
        
        if safe_zone_active and not game_over:
            seconds_left = safe_zone_timer // 60
            draw_text(screen, f"Безопасная зона: {seconds_left} сек", 
                     small_font, GREEN, WIDTH // 2, 110)
        
        if not game_over:
            draw_text(screen, "← → или A D | Пробел - прыжок | R - рестарт", 
                     small_font, BLACK, WIDTH // 2, HEIGHT - 40)
            
            if player.invincible:
                draw_text(screen, "СТАРТОВАЯ ПЛАТФОРМА", small_font, BLUE, WIDTH // 2, 140)
        else:
            # Game Over экран
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "ИГРА ОКОНЧЕНА", big_font, RED, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(screen, f"Ваш счет: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, f"Рекорд: {high_score}", small_font, YELLOW, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text(screen, "Нажмите R для рестарта", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 100)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
