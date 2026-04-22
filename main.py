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
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Типы платформ
class PlatformType(Enum):
    NORMAL = 1
    MOVING = 2
    FRAGILE = 3
    BOUNCE = 4
    ICE = 5

# Состояния игры
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дудл Джамп")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 72)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, 0, 10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, 10)
        
        text_surface = small_font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self):
        self.state = GameState.MENU
        self.buttons = []
        self.create_buttons()
        self.particles = []
        self.title_offset = 0
        
    def create_buttons(self):
        button_width = 250
        button_height = 50
        start_y = HEIGHT // 2
        
        # Кнопка "Начать игру"
        start_button = Button(
            WIDTH // 2 - button_width // 2,
            start_y - 40,
            button_width,
            button_height,
            "Начать игру",
            DARK_BLUE,
            BLUE,
            WHITE
        )
        self.buttons.append(start_button)
        
        # Кнопка "Выход"
        exit_button = Button(
            WIDTH // 2 - button_width // 2,
            start_y + 40,
            button_width,
            button_height,
            "Выход",
            DARK_BLUE,
            BLUE,
            WHITE
        )
        self.buttons.append(exit_button)
    
    def update(self):
        # Анимация заголовка
        self.title_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5
        
        # Обновление частиц
        if random.random() < 0.1:
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': HEIGHT,
                'vel_y': random.uniform(-5, -2),
                'vel_x': random.uniform(-1, 1),
                'size': random.randint(2, 5),
                'color': random.choice([BLUE, CYAN, GOLD])
            })
        
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['size'] -= 0.1
            if particle['y'] < 0 or particle['size'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        # Градиентный фон
        for i in range(HEIGHT):
            color_value = 135 + int((i / HEIGHT) * 50)
            color = (color_value, 206 - int((i / HEIGHT) * 50), 235 - int((i / HEIGHT) * 100))
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))
        
        # Звезды на фоне
        for _ in range(50):
            x = (pygame.time.get_ticks() * 0.05 + _ * 100) % WIDTH
            y = (_ * 50) % HEIGHT
            pygame.draw.circle(surface, WHITE, (int(x), int(y)), 1)
        
        # Частицы
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size']))
        
        # Заголовок с анимацией
        title_y = HEIGHT // 4 + self.title_offset
        title_text = big_font.render("ДУДЛ ДЖАМП", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH // 2, title_y))
        surface.blit(title_text, title_rect)
        
        # Подзаголовок
        subtitle_text = small_font.render("Прыгай выше всех!", True, CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, title_y + 50))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Кнопки
        for button in self.buttons:
            button.draw(surface)
        
        # Версия игры
        version_text = small_font.render("Версия 2.0", True, LIGHT_GRAY)
        surface.blit(version_text, (10, HEIGHT - 30))
    
    def handle_event(self, event):
        for i, button in enumerate(self.buttons):
            if button.handle_event(event):
                return i
        return -1

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
    
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2 + self.animation_offset
    
    # Рисуем звезду
        points = []
        outer_radius = self.width // 2
        inner_radius = outer_radius // 2
        num_points = 5
    
        for i in range(num_points * 2):
            angle = math.pi * 2 * i / (num_points * 2) - math.pi / 2
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
    
        pygame.draw.polygon(surface, self.color, points)
    
    # Глаза
        pygame.draw.circle(surface, WHITE, (center_x - 8, center_y - 8), 4)
        pygame.draw.circle(surface, WHITE, (center_x + 8, center_y - 8), 4)
        pygame.draw.circle(surface, BLACK, (center_x - 8, center_y - 8), 2)
        pygame.draw.circle(surface, BLACK, (center_x + 8, center_y - 8), 2)
    

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
        
    return platforms, start_y

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
    menu = Menu()
    game_state = GameState.MENU
    
    platforms = None
    player = None
    score = 0
    high_score = 0
    safe_zone_active = True
    safe_zone_timer = 300
    jump_delay = 0
    jump_cooldown = 10
    scroll_offset = 0
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_state != GameState.MENU:
                    game_state = GameState.MENU
                    game_over = False
                    
            if game_state == GameState.MENU:
                choice = menu.handle_event(event)
                if choice == 0:  # Начать игру
                    platforms, start_platform_y = create_platforms()
                    player = Player(start_platform_y)
                    score = 0
                    game_over = False
                    safe_zone_active = True
                    safe_zone_timer = 300
                    game_state = GameState.PLAYING
                elif choice == 1:  # Выход
                    running = False
                    
            elif game_state == GameState.PLAYING:
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
        
        if game_state == GameState.MENU:
            menu.update()
            menu.draw(screen)
            
        elif game_state == GameState.PLAYING:
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
                draw_text(screen, "← → или A D | ESC - меню", 
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
                draw_text(screen, "Нажмите R для рестарта или ESC для меню", small_font, WHITE, WIDTH // 2, HEIGHT // 2 + 100)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
