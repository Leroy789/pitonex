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
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
BACKGROUND = (135, 206, 235)
DARK_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Типы платформ
class PlatformType(Enum):
    NORMAL = 1
    MOVING = 2
    FRAGILE = 3
    BOUNCE = 4
    ICE = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дудл Джамп - Расширенная версия")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 72)

# Звуки (заглушки, т.к. нет файлов)
try:
    jump_sound = pygame.mixer.Sound("jump.wav")
    coin_sound = pygame.mixer.Sound("coin.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
    game_over_sound = pygame.mixer.Sound("gameover.wav")
except:
    jump_sound = None
    coin_sound = None
    powerup_sound = None
    game_over_sound = None

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.initial_lifetime = lifetime
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.initial_lifetime))
        color = (*self.color, alpha)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.type = power_type
        self.animation_frame = 0
        self.collected = False
        
    def update(self):
        self.animation_frame += 0.2
        
    def draw(self, surface):
        if self.collected:
            return
            
        # Анимация парения
        y_offset = math.sin(self.animation_frame) * 5
        
        if self.type == "speed":
            color = CYAN
            symbol = "⚡"
        elif self.type == "shield":
            color = BLUE
            symbol = "🛡"
        elif self.type == "magnet":
            color = GOLD
            symbol = "🧲"
        else:
            color = PINK
            symbol = "⭐"
            
        pygame.draw.rect(surface, color, (self.x, self.y + y_offset, self.width, self.height), 0, 5)
        text = small_font.render(symbol, True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2 + y_offset))
        surface.blit(text, text_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.animation_frame = 0
        self.collected = False
        
    def update(self):
        self.animation_frame += 0.1
        
    def draw(self, surface):
        if self.collected:
            return
            
        # Анимация вращения монеты
        angle = math.sin(self.animation_frame) * 0.5
        scale = 0.8 + math.sin(self.animation_frame * 2) * 0.2
        
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), int(self.radius * scale))
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), int(self.radius * scale * 0.7))
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

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
        
        # Новые параметры
        self.speed_boost = 1.0
        self.speed_boost_timer = 0
        self.shield = False
        self.shield_timer = 0
        self.magnet = False
        self.magnet_timer = 0
        self.particles = []
        self.animation_offset = 0
        
    def add_particles(self, x, y):
        for _ in range(10):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            self.particles.append(Particle(x, y, vx, vy, RED))
            
    def update(self, platforms, coins, powerups):
        # Обновление таймеров бонусов
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = 1.0
                
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False
                
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet = False
            else:
                # Магнит притягивает монеты
                for coin in coins:
                    if not coin.collected:
                        dx = (self.x + self.width//2) - coin.x
                        dy = (self.y + self.height//2) - coin.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 200:
                            coin.x += dx * 0.1
                            coin.y += dy * 0.1
        
        # Инвincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.color = RED
        
        # Физика
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.x += self.vel_x * self.speed_boost
        
        # Границы экрана
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
            
        # Анимация
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.01) * 2
        
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
                    self.add_particles(self.x + self.width//2, self.y + self.height)
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
                    
                self.is_jumping = True
                platform.hit = True
                
                if jump_sound:
                    jump_sound.play()
                
        # Обновление частиц
        self.particles = [p for p in self.particles if p.update()]
        
        if self.y > HEIGHT + 200:
            return False
        return True
        
    def collect_powerup(self, powerup):
        if powerup.type == "speed":
            self.speed_boost = 1.5
            self.speed_boost_timer = 300
        elif powerup.type == "shield":
            self.shield = True
            self.shield_timer = 600
        elif powerup.type == "magnet":
            self.magnet = True
            self.magnet_timer = 300
            
        if powerup_sound:
            powerup_sound.play()
        
    def draw(self, surface):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
            
        # Рисование щита
        if self.shield:
            shield_radius = max(self.width, self.height) // 2 + 5
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 100, 255, 100), 
                             (shield_radius, shield_radius), shield_radius)
            surface.blit(shield_surface, (self.x + self.width//2 - shield_radius, 
                                         self.y + self.height//2 - shield_radius))
        
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
        
        # Рисование частиц
        for particle in self.particles:
            particle.draw(surface)

class Platform:
    def __init__(self, x, y, is_start=False, platform_type=PlatformType.NORMAL):
        self.x = x
        self.y = y
        self.width = PLATFORM_WIDTH
        self.height = PLATFORM_HEIGHT
        self.platform_type = platform_type
        self.is_start = is_start
        self.hit = False
        self.is_broken = False
        self.hit_count = 0
        self.move_direction = 1
        self.move_speed = 2
        self.original_x = x
        
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
            
        # Эффект при попадании
        if self.hit:
            color = YELLOW
            self.hit = False
        else:
            color = self.color
            
        # Отрисовка платформы
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height), 0, 5)
        
        # Детали для разных типов
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
    coins = []
    powerups = []
    
    start_x = WIDTH // 2 - PLATFORM_WIDTH // 2
    start_y = HEIGHT - 150
    start_platform = Platform(start_x, start_y, is_start=True)
    platforms.append(start_platform)
    
    min_distance = 80
    max_distance = 150
    current_y = start_y - 100
    
    for i in range(PLATFORM_COUNT - 1):
        x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
        
        # Выбор типа платформы
        rand_type = random.random()
        if rand_type < 0.7:
            platform_type = PlatformType.NORMAL
        elif rand_type < 0.85:
            platform_type = PlatformType.MOVING
        elif rand_type < 0.95:
            platform_type = PlatformType.BOUNCE
        else:
            platform_type = PlatformType.ICE
            
        platform = Platform(x, current_y, platform_type=platform_type)
        platforms.append(platform)
        
        # Добавление монет на платформы
        if random.random() < 0.4 and not platform.is_start:
            coin_x = platform.x + platform.width//2
            coin_y = platform.y - 15
            coins.append(Coin(coin_x, coin_y))
            
        # Добавление бонусов
        if random.random() < 0.2 and not platform.is_start and i > 3:
            powerup_x = platform.x + platform.width//2 - 12
            powerup_y = platform.y - 25
            power_type = random.choice(["speed", "shield", "magnet"])
            powerups.append(PowerUp(powerup_x, powerup_y, power_type))
        
        current_y -= random.randint(min_distance, max_distance)
        
        if current_y < 100:
            current_y = HEIGHT - 200
            
    return platforms, coins, powerups, start_platform.y

def draw_text(surface, text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_safe_zone(surface):
    safe_surface = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
    safe_surface.fill((0, 255, 0, 50))
    surface.blit(safe_surface, (0, HEIGHT - 100))
    draw_text(surface, "БЕЗОПАСНАЯ ЗОНА", small_font, GREEN, WIDTH // 2, HEIGHT - 50)

def draw_background(surface, scroll):
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

def main():
    platforms, coins, powerups, start_platform_y = create_platforms()
    player = Player(start_platform_y)
    
    score = 0
    coins_collected = 0
    game_over = False
    high_score = 0
    safe_zone_active = True
    safe_zone_timer = 300
    camera_moved = False
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
                if event.key == pygame.K_SPACE:
                    player.vel_y = JUMP_FORCE
                if event.key == pygame.K_r and game_over:
                    platforms, coins, powerups, start_platform_y = create_platforms()
                    player = Player(start_platform_y)
                    score = 0
                    coins_collected = 0
                    game_over = False
                    safe_zone_active = True
                    safe_zone_timer = 300
                    camera_moved = False
                    
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                    player.vel_x = 0
        
        if not game_over:
            if safe_zone_active:
                safe_zone_timer -= 1
                if safe_zone_timer <= 0:
                    safe_zone_active = False
            
            # Обновление
            alive = player.update(platforms, coins, powerups)
            scroll_offset = player.y
            
            if not alive and not player.shield:
                game_over = True
                if score > high_score:
                    high_score = score
                if game_over_sound:
                    game_over_sound.play()
            
            # Обновление монет и бонусов
            for coin in coins:
                coin.update()
                if not coin.collected and player.x < coin.x + coin.radius and \
                   player.x + player.width > coin.x - coin.radius and \
                   player.y < coin.y + coin.radius and \
                   player.y + player.height > coin.y - coin.radius:
                    coin.collected = True
                    coins_collected += 1
                    score += 10
                    if coin_sound:
                        coin_sound.play()
                        
            for powerup in powerups:
                powerup.update()
                if not powerup.collected and player.x < powerup.x + powerup.width and \
                   player.x + player.width > powerup.x and \
                   player.y < powerup.y + powerup.height and \
                   player.y + player.height > powerup.y:
                    powerup.collected = True
                    player.collect_powerup(powerup)
                    score += 25
            
            # Обновление платформ и начисление очков
            camera_moved = False
            for platform in platforms:
                platform.update(player.vel_y)
                
                if player.y < HEIGHT // 3 and player.vel_y < 0 and not safe_zone_active:
                    platform.y -= player.vel_y
                    camera_moved = True
                
                if platform.y > HEIGHT + 100 and not platform.is_start:
                    platform.x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
                    platform.y = -50
                    platform.hit = False
                    platform.is_broken = False
                    platform.hit_count = 0
                    
                    # Смена типа при респавне
                    rand_type = random.random()
                    if rand_type < 0.7:
                        platform.platform_type = PlatformType.NORMAL
                    elif rand_type < 0.85:
                        platform.platform_type = PlatformType.MOVING
                    elif rand_type < 0.95:
                        platform.platform_type = PlatformType.BOUNCE
                    else:
                        platform.platform_type = PlatformType.ICE
                    platform.color = platform.colors.get(platform.platform_type, GREEN)
                    platform.original_x = platform.x
                    
                    # Добавление новых монет и бонусов
                    if random.random() < 0.3:
                        coin_x = platform.x + platform.width//2
                        coin_y = platform.y - 15
                        coins.append(Coin(coin_x, coin_y))
                        
                    if random.random() < 0.15:
                        powerup_x = platform.x + platform.width//2 - 12
                        powerup_y = platform.y - 25
                        power_type = random.choice(["speed", "shield", "magnet"])
                        powerups.append(PowerUp(powerup_x, powerup_y, power_type))
            
            if camera_moved and not safe_zone_active:
                for platform in platforms:
                    if platform.y + platform.height < player.y and not platform.is_start:
                        if not hasattr(platform, 'scored') or not platform.scored:
                            platform.scored = True
                            score += 5
        
        # Отрисовка
        draw_background(screen, scroll_offset)
        
        if safe_zone_active:
            draw_safe_zone(screen)
        
        # Отрисовка объектов
        for platform in platforms:
            platform.draw(screen)
        for coin in coins:
            if not coin.collected:
                coin.draw(screen)
        for powerup in powerups:
            if not powerup.collected:
                powerup.draw(screen)
        
        player.draw(screen)
        
        # UI
        draw_text(screen, f"Счет: {score}", font, BLACK, WIDTH // 2, 30)
        draw_text(screen, f"Монеты: {coins_collected}", small_font, GOLD, WIDTH // 2, 70)
        draw_text(screen, f"Рекорд: {high_score}", small_font, BLACK, WIDTH // 2, 105)
        
        # Отображение активных бонусов
        y_offset = 140
        if player.speed_boost_timer > 0:
            draw_text(screen, f"Скорость: {player.speed_boost_timer//60}", 
                     small_font, CYAN, WIDTH // 2, y_offset)
            y_offset += 25
        if player.shield_timer > 0:
            draw_text(screen, f"Щит: {player.shield_timer//60}", 
                     small_font, BLUE, WIDTH // 2, y_offset)
            y_offset += 25
        if player.magnet_timer > 0:
            draw_text(screen, f"Магнит: {player.magnet_timer//60}", 
                     small_font, GOLD, WIDTH // 2, y_offset)
        
        # Отладочная информация
        debug_info = f"Y: {int(player.y)}, VelY: {player.vel_y:.1f}"
        draw_text(screen, debug_info, small_font, BLACK, WIDTH // 2, HEIGHT - 100)
        
        if not game_over:
            draw_text(screen, "← → или A D | Пробел - прыжок | R - рестарт", 
                     small_font, BLACK, WIDTH // 2, HEIGHT - 40)
            
            if safe_zone_active:
                seconds_left = safe_zone_timer // 60
                draw_text(screen, f"Безопасная зона: {seconds_left} сек", 
                         small_font, GREEN, WIDTH // 2, 100)
            
            if player.invincible:
                draw_text(screen, "СТАРТОВАЯ ПЛАТФОРМА", small_font, BLUE, WIDTH // 2, 130)
        else:
            # Game Over экран
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "ИГРА ОКОНЧЕНА", big_font, RED, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text(screen, f"Счет: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
            draw_text(screen, f"Монет собрано: {coins_collected}", small_font, GOLD, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(screen, f"Рекорд: {high_score}", small_font, YELLOW, WIDTH // 2, HEIGHT // 2 + 60)
            draw_text(screen, "Нажмите R для рестарта", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 120)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
