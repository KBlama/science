import pygame
import random
import math
import time
import sys
import os
from pygame.locals import *

# 初始化pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=4, buffer=1024)

# 屏幕设置
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("池塘夜降彩色雨")

# 颜色定义
DARK_BLUE = (10, 10, 30)
POND_BLUE = (20, 40, 100)
LIGHT_BLUE = (100, 100, 200)
WHITE = (255, 255, 255)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
FISH_COLOR = (255, 150, 50)


# 音效管理类
class SoundManager:
    def __init__(self):
        self.rain_sound = None
        self.thunder_sound = None
        self.rain_channel = None
        self.thunder_channel = None
        self.load_sounds()

    def load_sounds(self):
        """加载音效文件"""
        try:
            # 尝试加载雨声音效
            if os.path.exists("rain.wav"):
                self.rain_sound = pygame.mixer.Sound("rain.wav")
                print("成功加载雨声音效")
            else:
                # 创建虚拟雨声音效
                self.create_dummy_rain_sound()
                print("使用虚拟雨声音效")

            # 尝试加载雷声音效
            if os.path.exists("thunder.wav"):
                self.thunder_sound = pygame.mixer.Sound("thunder.wav")
                print("成功加载雷声音效")
            else:
                # 创建虚拟雷声音效
                self.create_dummy_thunder_sound()
                print("使用虚拟雷声音效")

        except Exception as e:
            print(f"加载音效时出错: {e}")
            self.create_dummy_sounds()

    def create_dummy_rain_sound(self):
        """创建虚拟雨声音效"""
        # 创建一个简短的静音作为虚拟音效
        self.rain_sound = pygame.mixer.Sound(buffer=bytes([0] * 1000))

    def create_dummy_thunder_sound(self):
        """创建虚拟雷声音效"""
        # 创建一个简短的静音作为虚拟音效
        self.thunder_sound = pygame.mixer.Sound(buffer=bytes([0] * 1000))

    def create_dummy_sounds(self):
        """创建所有虚拟音效"""
        self.create_dummy_rain_sound()
        self.create_dummy_thunder_sound()

    def play_rain(self):
        """播放雨声（循环播放）"""
        if self.rain_sound and not self.rain_channel:
            try:
                self.rain_channel = pygame.mixer.Channel(0)
                self.rain_channel.set_volume(0.3)
                self.rain_channel.play(self.rain_sound, loops=-1)
            except Exception as e:
                print(f"播放雨声失败: {e}")

    def stop_rain(self):
        """停止雨声"""
        if self.rain_channel:
            self.rain_channel.stop()
            self.rain_channel = None

    def play_thunder(self):
        """播放雷声"""
        if self.thunder_sound:
            try:
                # 使用专用频道播放雷声
                if not self.thunder_channel:
                    self.thunder_channel = pygame.mixer.Channel(1)
                    self.thunder_channel.set_volume(0.8)

                # 确保频道空闲
                if not self.thunder_channel.get_busy():
                    self.thunder_channel.play(self.thunder_sound)
                    print("雷声音效播放成功")
                else:
                    # 如果频道忙，尝试使用其他频道
                    channel = pygame.mixer.find_channel(True)
                    if channel:
                        channel.set_volume(0.8)
                        channel.play(self.thunder_sound)
                        print("使用备用频道播放雷声")
            except Exception as e:
                print(f"播放雷声失败: {e}")


# 创建渐变背景表面
def create_gradient_background(width, height):
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(DARK_BLUE[0] * (1 - ratio))
        g = int(DARK_BLUE[1] * (1 - ratio))
        b = int(DARK_BLUE[2] * (1 - ratio))
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient


# 创建池塘表面
def create_pond_surface(width, height):
    pond = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        ratio = y / height
        r = int(POND_BLUE[0] * (1 - ratio * 0.5))
        g = int(POND_BLUE[1] * (1 - ratio * 0.5))
        b = int(POND_BLUE[2] * (1 - ratio * 0.3))
        alpha = 150 + int(100 * ratio)
        pygame.draw.line(pond, (r, g, b, alpha), (0, y), (width, y))
    return pond


# 荷叶类
class LotusLeaf:
    def __init__(self, pond_top, pond_height, existing_leaves=None):
        self.radius = random.randint(30, 50)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(pond_top + self.radius, pond_top + pond_height - self.radius)
        self.color = DARK_GREEN
        self.water_drops = []

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, GREEN, (self.x, self.y), self.radius, 2)

        for i in range(8):
            angle = i * math.pi / 4
            end_x = self.x + self.radius * 0.8 * math.cos(angle)
            end_y = self.y + self.radius * 0.8 * math.sin(angle)
            pygame.draw.line(surface, GREEN, (self.x, self.y), (end_x, end_y), 1)

        for drop in self.water_drops:
            pygame.draw.circle(surface, LIGHT_BLUE, (int(drop[0]), int(drop[1])), int(drop[2]))

    def add_water_drop(self, x, y):
        self.water_drops.append([x, y, 3])
        if len(self.water_drops) > 10:
            self.water_drops.pop(0)

    def update_water_drops(self):
        for drop in self.water_drops:
            drop[1] -= 0.5
            drop[2] = max(1, drop[2] - 0.1)


# 鱼类
class Fish:
    def __init__(self, pond_top, pond_height):
        self.pond_top = pond_top
        self.pond_height = pond_height
        self.length = random.randint(20, 40)
        self.speed = random.uniform(0.5, 2.0)
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(pond_top + 20, pond_top + pond_height - 20)
        self.direction = random.uniform(0, 2 * math.pi)
        self.color = FISH_COLOR
        self.tail_phase = random.uniform(0, 2 * math.pi)
        self.tail_speed = random.uniform(0.1, 0.3)

    def update(self):
        if random.random() < 0.02:
            self.direction += random.uniform(-0.5, 0.5)

        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

        if self.x < 20 or self.x > WIDTH - 20:
            self.direction = math.pi - self.direction
        if self.y < self.pond_top + 20 or self.y > self.pond_top + self.pond_height - 20:
            self.direction = -self.direction

        self.x = max(20, min(WIDTH - 20, self.x))
        self.y = max(self.pond_top + 20, min(self.pond_top + self.pond_height - 20, self.y))
        self.tail_phase += self.tail_speed

    def draw(self, surface):
        head_x = self.x + math.cos(self.direction) * self.length / 2
        head_y = self.y + math.sin(self.direction) * self.length / 2
        tail_x = self.x - math.cos(self.direction) * self.length / 2
        tail_y = self.y - math.sin(self.direction) * self.length / 2
        tail_offset = math.sin(self.tail_phase) * 5
        tail_side_x = tail_x + math.cos(self.direction + math.pi / 2) * tail_offset
        tail_side_y = tail_y + math.sin(self.direction + math.pi / 2) * tail_offset

        pygame.draw.line(surface, self.color, (head_x, head_y), (tail_x, tail_y), 3)
        pygame.draw.polygon(surface, self.color, [
            (tail_x, tail_y),
            (tail_side_x, tail_side_y),
            (tail_x - math.cos(self.direction) * 10, tail_y - math.sin(self.direction) * 10)
        ])

        eye_x = head_x - math.cos(self.direction) * 5
        eye_y = head_y - math.sin(self.direction) * 5
        pygame.draw.circle(surface, WHITE, (int(eye_x), int(eye_y)), 3)


# 雨滴类
class Raindrop:
    def __init__(self, leaves, wind_strength=0, pond_top=0, sound_manager=None):
        self.state = "falling"
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, 0)
        self.fall_speed = random.uniform(5, 15)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.ripple_radius = 0
        self.max_ripple_radius = random.randint(20, 50)
        self.ripple_width = 3
        self.ripple_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.visible = True
        self.next_update_time = time.time() + random.uniform(0.05, 0.2)
        self.wind_effect = wind_strength * random.uniform(0.5, 1.5)
        self.pond_top = pond_top
        self.sound_manager = sound_manager

        self.on_leaf = False
        self.leaf = None
        for leaf in leaves:
            distance = math.sqrt((self.x - leaf.x) ** 2 + (self.y - leaf.y) ** 2)
            if distance < leaf.radius:
                self.on_leaf = True
                self.leaf = leaf
                break

        self.splash_particles = []

    def update(self, leaves, wind_strength):
        current_time = time.time()

        if self.state == "falling":
            self.wind_effect = wind_strength * random.uniform(0.5, 1.5)
            self.y += self.fall_speed
            self.x += self.wind_effect

            if current_time > self.next_update_time:
                self.visible = not self.visible
                self.next_update_time = current_time + random.uniform(0.05, 0.2)

            if self.y >= self.pond_top or (self.on_leaf and self.y >= self.leaf.y):
                self.state = "splash" if not self.on_leaf else "leaf_splash"
                self.splash_time = current_time

                # 播放雨声音效
                if not self.on_leaf and self.sound_manager and self.sound_manager.rain_sound:
                    try:
                        # 使用雨声频道播放
                        channel = pygame.mixer.Channel(2)
                        if not channel.get_busy():
                            channel.play(self.sound_manager.rain_sound)
                    except:
                        pass

                if self.on_leaf and self.leaf:
                    self.leaf.add_water_drop(self.x, self.y)

        elif self.state == "splash":
            if current_time - self.splash_time > 0.1:
                self.state = "ripple"
                self.ripple_start_time = current_time

        elif self.state == "leaf_splash":
            if len(self.splash_particles) == 0:
                for _ in range(8):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 8)
                    self.splash_particles.append({
                        'x': self.x,
                        'y': self.y,
                        'vx': speed * math.cos(angle),
                        'vy': speed * math.sin(angle),
                        'life': 1.0
                    })

            for particle in self.splash_particles:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.2
                particle['life'] -= 0.05

            self.splash_particles = [p for p in self.splash_particles if p['life'] > 0]

            if len(self.splash_particles) == 0:
                self.state = "ripple"
                self.ripple_start_time = current_time

        elif self.state == "ripple":
            self.ripple_radius += 0.8
            self.ripple_width = max(1, self.ripple_width - 0.03)

            if self.ripple_radius > self.max_ripple_radius or self.ripple_width <= 0:
                return False

        return True

    def draw(self, surface):
        if self.state == "falling" and self.visible:
            pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), (int(self.x), int(self.y + 10)), 2)

        elif self.state == "splash":
            for i in range(5):
                angle = random.uniform(0, 2 * math.pi)
                length = random.uniform(5, 15)
                end_x = self.x + length * math.cos(angle)
                end_y = self.y + length * math.sin(angle)
                pygame.draw.line(surface, self.ripple_color, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)

        elif self.state == "leaf_splash":
            for particle in self.splash_particles:
                alpha = int(255 * particle['life'])
                r = min(255, self.ripple_color[0] + alpha // 3)
                g = min(255, self.ripple_color[1] + alpha // 3)
                b = min(255, self.ripple_color[2] + alpha // 3)
                color = (r, g, b)
                pygame.draw.circle(surface, color, (int(particle['x']), int(particle['y'])), 3)

        elif self.state == "ripple":
            alpha = int(255 * (1 - self.ripple_radius / self.max_ripple_radius))
            if alpha > 0:
                temp_surface = pygame.Surface((self.max_ripple_radius * 2, self.max_ripple_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (*self.ripple_color, alpha),
                                   (self.max_ripple_radius, self.max_ripple_radius),
                                   int(self.ripple_radius), int(self.ripple_width))
                surface.blit(temp_surface, (int(self.x - self.max_ripple_radius),
                                            int(self.y - self.max_ripple_radius)))


# 闪电类
class Lightning:
    def __init__(self, sound_manager=None):
        self.active = False
        self.start_time = 0
        self.duration = 0.2
        self.branches = []
        self.last_strike_time = 0
        self.min_interval = 15
        self.sound_manager = sound_manager
        self.thunder_played = False

    def strike(self):
        current_time = time.time()
        if current_time - self.last_strike_time < self.min_interval:
            return False

        self.active = True
        self.start_time = current_time
        self.last_strike_time = current_time
        self.thunder_played = False
        self.branches = []

        start_x = random.randint(100, WIDTH - 100)
        main_branch = self.create_branch(start_x, 0, start_x + random.randint(-100, 100), HEIGHT // 3, 5)
        self.branches.append(main_branch)

        for _ in range(random.randint(3, 8)):
            branch_point = random.choice(main_branch)
            end_x = branch_point[0] + random.randint(-80, 80)
            end_y = branch_point[1] + random.randint(20, 100)
            branch = self.create_branch(branch_point[0], branch_point[1], end_x, end_y, 3)
            self.branches.append(branch)

        return True

    def create_branch(self, start_x, start_y, end_x, end_y, segments):
        branch = []
        branch.append((start_x, start_y))

        for i in range(1, segments):
            t = i / segments
            x = start_x + (end_x - start_x) * t + random.randint(-20, 20)
            y = start_y + (end_y - start_y) * t + random.randint(-10, 10)
            branch.append((x, y))

        branch.append((end_x, end_y))
        return branch

    def update(self):
        current_time = time.time()

        # 在闪电开始后短暂延迟播放雷声
        if self.active and not self.thunder_played and current_time - self.start_time > 0.1:
            if self.sound_manager:
                self.sound_manager.play_thunder()
            self.thunder_played = True

        if self.active and current_time - self.start_time > self.duration:
            self.active = False

    def draw(self, surface):
        if self.active:
            for branch in self.branches:
                for i in range(len(branch) - 1):
                    pygame.draw.line(surface, WHITE, branch[i], branch[i + 1], 2)


# 主函数
def main():
    clock = pygame.time.Clock()
    raindrops = []
    leaves = []

    # 创建音效管理器
    sound_manager = SoundManager()
    sound_manager.play_rain()  # 开始播放背景雨声

    lightning = Lightning(sound_manager)

    # 池塘参数
    pond_height = 150
    pond_top = HEIGHT - pond_height

    # 创建渐变背景
    gradient_bg = create_gradient_background(WIDTH, HEIGHT)

    # 创建池塘表面
    pond_surface = create_pond_surface(WIDTH, pond_height)

    # 创建荷叶
    for _ in range(6):
        leaves.append(LotusLeaf(pond_top, pond_height, leaves))

    # 创建两条鱼
    fishes = []
    for _ in range(2):
        fishes.append(Fish(pond_top, pond_height))

    # 天气参数
    rain_density = 0.5
    wind_strength = 0
    weather_change_timer = 0
    weather_state = "normal"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_t:  # 按T键测试闪电
                    lightning.strike()

        # 随机天气变化
        weather_change_timer += 1
        if weather_change_timer > 300:
            weather_change_timer = 0
            if random.random() < 0.3:
                if weather_state == "normal":
                    weather_state = random.choice(["heavy", "light"])
                else:
                    weather_state = "normal"

                if weather_state == "heavy":
                    rain_density = 0.9
                    wind_strength = random.randint(2, 5) * random.choice([-1, 1])
                elif weather_state == "light":
                    rain_density = 0.2
                    wind_strength = random.randint(0, 1) * random.choice([-1, 1])
                else:
                    rain_density = 0.5
                    wind_strength = random.randint(0, 2) * random.choice([-1, 1])

        # 随机闪电
        if random.random() < 0.002:
            lightning.strike()

        # 生成新雨滴
        if random.random() < rain_density:
            raindrops.append(Raindrop(leaves, wind_strength, pond_top, sound_manager))

        # 更新雨滴
        raindrops = [drop for drop in raindrops if drop.update(leaves, wind_strength)]

        # 更新荷叶上的水珠
        for leaf in leaves:
            leaf.update_water_drops()

        # 更新鱼
        for fish in fishes:
            fish.update()

        # 更新闪电
        lightning.update()

        # 绘制
        screen.blit(gradient_bg, (0, 0))
        screen.blit(pond_surface, (0, pond_top))

        for leaf in leaves:
            leaf.draw(screen)

        for fish in fishes:
            fish.draw(screen)

        for drop in raindrops:
            drop.draw(screen)

        lightning.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    # 停止雨声
    sound_manager.stop_rain()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()