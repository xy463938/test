# -*- coding: utf-8 -*-
"""
飞机大战游戏
作者：Assistant
"""

import pygame
import random
import sys
from enum import Enum

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("飞机大战")
clock = pygame.time.Clock()

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 创建玩家飞机图像
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(0, 40), (25, 0), (50, 40)])
        pygame.draw.polygon(self.image, CYAN, [(10, 40), (25, 10), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5
        self.shoot_delay = 250  # 毫秒
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.invincible = False
        self.invincible_timer = 0
    def update(self):
        # 无敌时间处理
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
        # 如果飞机隐藏，则不响应控制
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.bottom = SCREEN_HEIGHT - 10
            
        # 获取按键状态
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0 and not self.hidden:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH and not self.hidden:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0 and not self.hidden:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT and not self.hidden:
            self.rect.y += self.speed
    def shoot(self, bullets):
        if not self.hidden and not self.invincible:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.top, -10)
                bullets.add(bullet)
                return True
        return False
                
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.y = SCREEN_HEIGHT + 200  # 将飞机移出屏幕
        
    def make_invincible(self, duration):
        self.invincible = True
        self.invincible_timer = duration

class Enemy(pygame.sprite.Sprite):
# 在Enemy类中修改__init__方法，美化敌机外观
    def __init__(self):
        super().__init__()
        # 创建更美观的敌机图像
        self.image = pygame.Surface((45, 35), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(0, 0), (22, 35), (45, 0)])  # 主体
        pygame.draw.polygon(self.image, YELLOW, [(5, 5), (22, 30), (40, 5)])  # 中间部分
        pygame.draw.circle(self.image, (255, 100, 100), (22, 10), 5)  # 引擎
    
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 8)
        self.speed_x = random.randrange(-3, 3)
        
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        # 如果敌机移出屏幕底部或顶部，重新生成
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.bottom < -10:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)

class Boss(pygame.sprite.Sprite):
    # 在Boss类中修改__init__方法，美化Boss外观
    def __init__(self):
        super().__init__()
    # 创建更美观的Boss图像
        self.image = pygame.Surface((100, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PURPLE, (10, 0, 80, 80))  # 主体
        pygame.draw.rect(self.image, (180, 0, 180), (0, 20, 100, 40))  # 中间部分
        pygame.draw.circle(self.image, RED, (30, 20), 10)  # 左炮台
        pygame.draw.circle(self.image, RED, (70, 20), 10)  # 右炮台
        pygame.draw.circle(self.image, (100, 0, 0), (50, 60), 15)  # 中心核心
    
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - self.rect.width // 2
        self.rect.y = -self.rect.height
        self.speed_y = 1
        self.speed_x = 2
        self.health = 20
        self.max_health = 20
        self.direction = 1
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()
    
        
    def update(self):
        # Boss出现动画
        if self.rect.y < 50:
            self.rect.y += self.speed_y
        else:
            # 左右移动
            self.rect.x += self.speed_x * self.direction
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1
                
    def hit(self):
        self.health -= 1
        return self.health <= 0
        
    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5)  # 向下发射
            bullets.add(bullet)
            return True
        return False

# 修改Bullet类，使其更加明显
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y):
        super().__init__()
        # 增大子弹尺寸使其更明显
        self.width = 8 if speed_y > 0 else 10
        self.height = 25 if speed_y > 0 else 30
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = speed_y
        
        # 绘制更亮的激光样式子弹
        self.draw_laser_bullet()
        
    def draw_laser_bullet(self):
        # 清空表面
        self.image.fill((0, 0, 0, 0))
        
        if self.speed_y < 0:  # 玩家子弹 - 亮黄色激光
            # 添加更强的光晕效果
            pygame.draw.ellipse(self.image, (255, 255, 100, 200), (0, 0, self.width, self.height))  # 强光晕
            pygame.draw.ellipse(self.image, (255, 255, 0), (1, 1, self.width-2, self.height-2))      # 主体
            pygame.draw.ellipse(self.image, (255, 255, 200), (2, 2, self.width-4, self.height//2))   # 高光
            pygame.draw.ellipse(self.image, (255, 255, 255), (3, 3, self.width-6, self.height//4))   # 中心亮点
        else:  # 敌机子弹 - 红色激光
            # 添加更强的光晕效果
            pygame.draw.ellipse(self.image, (255, 100, 100, 200), (0, 0, self.width, self.height))   # 强光晕
            pygame.draw.ellipse(self.image, (255, 0, 0), (1, 1, self.width-2, self.height-2))        # 主体
            pygame.draw.ellipse(self.image, (255, 150, 150), (2, 2, self.width-4, self.height//2))   # 高光
            pygame.draw.ellipse(self.image, (255, 200, 200), (3, 3, self.width-6, self.height//4))   # 中心亮点
        
    def update(self):
        self.rect.y += self.speed_y
        # 如果子弹移出屏幕顶部或底部，删除它
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
# 在PowerUp类中修改__init__方法，美化道具外观
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
    # 绘制更有吸引力的道具
        pygame.draw.circle(self.image, YELLOW, (12, 12), 12)
        pygame.draw.circle(self.image, (255, 200, 0), (12, 12), 9)
        pygame.draw.circle(self.image, WHITE, (12, 12), 5)
        pygame.draw.circle(self.image, YELLOW, (12, 12), 2)
    
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_y = 2
        
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 创建更复杂的爆炸效果
        pygame.draw.circle(self.image, YELLOW, (size//2, size//2), size//2)
        pygame.draw.circle(self.image, RED, (size//2, size//2), size//3)
        pygame.draw.circle(self.image, WHITE, (size//2, size//2), size//6)
    
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.timer = 20  # 延长显示时间
        
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# 修复Star类中的重复方法
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.1, 1)
        self.size = random.randint(1, 3)
        # 添加随机颜色
        colors = [(255, 255, 255), (200, 200, 255), (255, 255, 200)]
        self.color = random.choice(colors)
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class PlaneWarGame:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # 创建星空背景
        self.stars = [Star() for _ in range(100)]
        
        # 创建玩家
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.all_sprites.add(self.player)
        
        # 创建初始敌机
        for i in range(8):
            self.create_enemy()
            
        # 创建Boss
        self.boss = None
        self.boss_appeared = False
        
        self.score = 0
        self.level = 1
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.state = GameState.MENU
        
    def create_enemy(self):
        enemy = Enemy()
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        
    def create_boss(self):
        if not self.boss_appeared:
            self.boss = Boss()
            self.all_sprites.add(self.boss)
            self.enemies.add(self.boss)
            self.boss_appeared = True
            
    def create_powerup(self, x, y):
        if random.random() < 0.3:  # 30%概率生成道具
            powerup = PowerUp(x, y)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)
        
    def run(self):
        running = True
        
        while running:
            # 控制游戏更新速度
            clock.tick(FPS)
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.MENU:
                            self.state = GameState.PLAYING
                        elif self.state == GameState.PLAYING:
                            self.player.shoot(self.bullets)
                        elif self.state == GameState.GAME_OVER:
                            self.__init__()  # 重新开始游戏
                    elif event.key == pygame.K_p and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_p and self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == GameState.MENU:
                            running = False
                        else:
                            self.state = GameState.MENU
                            
            if self.state == GameState.PLAYING:
                self.update_game()
            
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
        
    def update_game(self):
        # 更新游戏对象
        self.all_sprites.update()
        self.bullets.update()  # 确保子弹被更新
        self.explosions.update()
        
        # 检查子弹是否击中敌机
        for bullet in self.bullets:
            # 只有玩家子弹能击中敌机
            if bullet.speed_y < 0:  # 玩家子弹向上
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                for enemy in hit_enemies:
                    # 创建爆炸效果
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 30)
                    self.all_sprites.add(explosion)
                    self.explosions.add(explosion)
                    
                    if isinstance(enemy, Boss):
                        if enemy.hit():
                            enemy.kill()
                            self.score += 100
                            self.boss = None
                            # Boss被击败后生成道具
                            self.create_powerup(enemy.rect.centerx, enemy.rect.centery)
                            # Boss被击败后重新生成普通敌机
                            for _ in range(5):
                                self.create_enemy()
                    else:
                        enemy.kill()
                        self.score += 10
                        self.create_powerup(enemy.rect.centerx, enemy.rect.centery)
                        self.create_enemy()
                        
                    bullet.kill()
        
        # 检查敌机子弹是否击中玩家
        for bullet in self.bullets:
            if bullet.speed_y > 0:  # 敌机子弹向下
                if pygame.sprite.collide_rect(bullet, self.player) and not self.player.invincible:
                    # 创建爆炸效果
                    explosion = Explosion(self.player.rect.centerx, self.player.rect.centery, 50)
                    self.all_sprites.add(explosion)
                    self.explosions.add(explosion)
                    
                    bullet.kill()
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self.state = GameState.GAME_OVER
                    else:
                        self.player.hide()
                        self.player.make_invincible(180)  # 3秒无敌时间
        
        # 检查玩家是否撞到敌机
        if not self.player.invincible:
            hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            for hit in hits:
                # 创建爆炸效果
                explosion = Explosion(self.player.rect.centerx, self.player.rect.centery, 50)
                self.all_sprites.add(explosion)
                self.explosions.add(explosion)
                
                # 创建新的敌机来替代被撞的
                self.create_enemy()
                
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.player.hide()
                    self.player.make_invincible(180)  # 3秒无敌时间
        
        # 检查玩家是否获得道具
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.player.lives = min(self.player.lives + 1, 5)  # 最多5条生命
        
        # 检查是否需要生成Boss
        if self.score >= 500 and not self.boss_appeared:
            self.create_boss()
        
        # 升级机制
        if self.score >= self.level * 500:
            self.level += 1
            # 增加更多敌机
            for _ in range(3):
                self.create_enemy()
    
    def draw(self):
        # 绘制背景
        screen.fill(BLACK)
        
        # 绘制星空背景
        for star in self.stars:
            star.draw(screen)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING or self.state == GameState.PAUSED:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
            
        if self.state == GameState.PAUSED:
            self.draw_pause()
    
    def draw_menu(self):
        title_text = self.big_font.render("飞机大战", True, WHITE)
        start_text = self.font.render("按空格键开始游戏", True, GREEN)
        quit_text = self.font.render("按ESC键退出", True, RED)
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    
    # 在draw_game方法中确保子弹被绘制
    def draw_game(self):
    # 绘制游戏元素 - 确保所有精灵组都被绘制
        self.all_sprites.draw(screen)
        self.bullets.draw(screen)  # 确保子弹被绘制
        self.explosions.draw(screen)
    
    # 显示得分、生命值和等级
        score_text = self.font.render(f"得分: {self.score}", True, WHITE)
        lives_text = self.font.render(f"生命: {self.player.lives}", True, WHITE)
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(level_text, (10, 90))
    
    # 显示控制说明
        control_text1 = self.font.render("方向键: 移动", True, WHITE)
        control_text2 = self.font.render("空格键: 射击", True, WHITE)
        control_text3 = self.font.render("P: 暂停", True, WHITE)
        control_text4 = self.font.render("ESC: 菜单", True, WHITE)
        screen.blit(control_text1, (SCREEN_WIDTH - 150, 10))
        screen.blit(control_text2, (SCREEN_WIDTH - 150, 50))
        screen.blit(control_text3, (SCREEN_WIDTH - 150, 90))
        screen.blit(control_text4, (SCREEN_WIDTH - 150, 130))
    
    # 显示Boss血条
        if self.boss:
            health_ratio = self.boss.health / self.boss.max_health
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - 50, 20, 100, 10))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 50, 20, 100 * health_ratio, 10))
    
    def draw_game_over(self):
        self.draw_game()  # 先绘制游戏画面
        
        # 绘制半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("游戏结束", True, RED)
        restart_text = self.font.render("按空格键重新开始", True, WHITE)
        final_score = self.font.render(f"最终得分: {self.score}", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    
    def draw_pause(self):
        pause_text = self.big_font.render("游戏暂停", True, YELLOW)
        continue_text = self.font.render("按P键继续游戏", True, WHITE)
        
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

# 运行游戏
if __name__ == "__main__":
    print("飞机大战游戏")
    print("正在初始化...")
    
    game = PlaneWarGame()
    game.run()