import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
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
BACKGROUND = (135, 206, 235)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дудл Джамп")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)

class Player:
    def __init__(self, start_platform_y):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        # Начинаем прямо на первой платформе
        self.y = start_platform_y - self.height - 1
        self.vel_y = 0
        self.vel_x = 0
        self.is_jumping = False
        self.color = RED
        self.invincible = True
        self.invincible_timer = 100
        
    def update(self, platforms):
        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.color = RED
        
        # Применение гравитации
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Движение по горизонтали
        self.x += self.vel_x
        
        # Проверка границ экрана по горизонтали
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
            
        # Проверка столкновения с платформами
        for platform in platforms:
            # Проверяем, что игрок падает вниз
            if (self.vel_y >= 0 and  # Изменил на >= 0 для лучшего определения
                self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + platform.height + 5 and  # Увеличил диапазон
                self.x + self.width > platform.x + 5 and  # Отступ от краев
                self.x < platform.x + platform.width - 5):
                
                # Ставим игрока точно на платформу
                self.y = platform.y - self.height
                self.vel_y = JUMP_FORCE  # Автоматический прыжок
                self.is_jumping = True
                platform.hit = True
                
        # Проверка выхода за нижнюю границу экрана с запасом
        if self.y > HEIGHT + 200:  # Увеличил запас до 200 пикселей
            return False
            
        return True
        
    def draw(self, surface):
        # Мерцание, если неуязвим
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
            
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), 0, 10)
        # Глаза
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
        self.color = GREEN if not is_start else BLUE  # Стартовая платформа другого цвета
        self.hit = False
        self.is_start = is_start
        
    def update(self, player_vel_y):
        # Платформы двигаются вниз, когда игрок подпрыгивает
        if player_vel_y < 0:
            self.y -= player_vel_y
            
    def draw(self, surface):
        # Стартовая платформа всегда синяя
        color = YELLOW if self.hit else self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height), 0, 5)
        # Обводка для стартовой платформы
        if self.is_start:
            pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 3, 5)

def create_platforms():
    platforms = []
    # Стартовая платформа внизу экрана
    start_x = WIDTH // 2 - PLATFORM_WIDTH // 2
    start_y = HEIGHT - 150
    start_platform = Platform(start_x, start_y, is_start=True)
    platforms.append(start_platform)
    
    # Создание остальных платформ выше
    # Генерируем платформы на разной высоте
    min_distance = 80  # Минимальное расстояние между платформами
    max_distance = 150  # Максимальное расстояние между платформами
    
    current_y = start_y - 100  # Первая платформа выше стартовой
    
    for i in range(PLATFORM_COUNT - 1):
        x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
        
        # Создаем платформу
        platforms.append(Platform(x, current_y))
        
        # Следующая платформа выше
        current_y -= random.randint(min_distance, max_distance)
        
        # Если платформы ушли слишком высоко, начинаем снова снизу
        if current_y < 100:
            current_y = HEIGHT - 200
        
    return platforms, start_platform.y

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_safe_zone(surface):
    # Рисуем безопасную зону (нижнюю часть экрана)
    pygame.draw.rect(surface, (0, 255, 0, 50), (0, HEIGHT - 100, WIDTH, 100))
    draw_text(screen, "БЕЗОПАСНАЯ ЗОНА", small_font, GREEN, WIDTH // 2, HEIGHT - 50)

def main():
    # Создаем платформы и получаем позицию стартовой платформы
    platforms, start_platform_y = create_platforms()
    
    # Создаем игрока на стартовой платформе
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
                
            # Управление с клавиатуры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.vel_x = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.vel_x = PLAYER_SPEED
                if event.key == pygame.K_SPACE:
                    # Прыжок по пробелу
                    player.vel_y = JUMP_FORCE * 0.7  # Меньший прыжок по пробелу
                if event.key == pygame.K_r and game_over:
                    # Рестарт игры
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
            # Обновление безопасной зоны
            if safe_zone_active:
                safe_zone_timer -= 1
                if safe_zone_timer <= 0:
                    safe_zone_active = False
            
            # Обновление игрока
            alive = player.update(platforms)
            
            if not alive:
                game_over = True
                if score > high_score:
                    high_score = score
                
            # Обновление платформ
            for platform in platforms:
                platform.update(player.vel_y)
                
                # Удаление платформ, которые ушли за нижнюю границу
                if platform.y > HEIGHT + 100:
                    # Не удаляем стартовую платформу
                    if not platform.is_start:
                        platform.x = random.randint(50, WIDTH - PLATFORM_WIDTH - 50)
                        platform.y = -50
                        platform.hit = False
                        # Разные цвета платформ
                        rand_color = random.random()
                        if rand_color > 0.8:
                            platform.color = BLUE
                        elif rand_color > 0.6:
                            platform.color = ORANGE
                        else:
                            platform.color = GREEN
                        
                        # Увеличение счета за каждую пройденную платформу
                        if not safe_zone_active:  # Счет только вне безопасной зоны
                            score += 1
            
            # Прокрутка платформ, если игрок поднялся выше трети экрана
            if player.y < HEIGHT // 3 and player.vel_y < 0:
                # Двигаем все платформы вниз
                for platform in platforms:
                    platform.y -= player.vel_y
                # Игрок остается на месте относительно экрана
                player.y -= player.vel_y
                # Увеличение счета за высоту
                if not safe_zone_active:  # Счет только вне безопасной зоны
                    score += 2
        
        # Отрисовка
        screen.fill(BACKGROUND)
        
        # Отрисовка безопасной зоны
        if safe_zone_active:
            draw_safe_zone(screen)
            
        # Отрисовка платформ
        for platform in platforms:
            platform.draw(screen)
            
        # Отрисовка игрока
        player.draw(screen)
        
        # Отрисовка счета
        draw_text(screen, f"Счет: {score}", font, BLACK, WIDTH // 2, 30)
        draw_text(screen, f"Рекорд: {high_score}", small_font, BLACK, WIDTH // 2, 70)
        
        # Отладочная информация (можно убрать)
        debug_info = f"Y: {int(player.y)}, VelY: {player.vel_y:.1f}"
        draw_text(screen, debug_info, small_font, BLACK, WIDTH // 2, HEIGHT - 100)
        
        # Отрисовка инструкций
        if not game_over:
            draw_text(screen, "Управление: ← → или A D, Пробел - прыжок", small_font, BLACK, WIDTH // 2, HEIGHT - 40)
            
            # Показываем таймер безопасной зоны
            if safe_zone_active:
                seconds_left = safe_zone_timer // 60
                draw_text(screen, f"Безопасная зона: {seconds_left} сек", small_font, GREEN, WIDTH // 2, 100)
                
            # Подсказка о стартовой платформе
            if player.invincible:
                draw_text(screen, "СТАРТОВАЯ ПЛАТФОРМА", small_font, BLUE, WIDTH // 2, 130)
        else:
            # Отрисовка экрана окончания игры
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
