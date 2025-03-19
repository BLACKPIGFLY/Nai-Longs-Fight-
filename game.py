import pygame
import random
import sys
import time, math
from pygame.locals import *
pygame.init()  # 初始化 Pygame 的所有模块
pygame.font.init()  # 显式初始化字体模块
pygame.mixer.init()
# 定义窗口变量
WORLDWIDTH = 1500  # 世界宽度
WORLDHEIGHT = 1500  # 世界高度
HALFWWIDTH = int(WORLDWIDTH // 2)
HALFWHEIGHT = int(WORLDHEIGHT // 2)
WIDTH = 800  # 窗口宽度
HEIGHT = 500  # 窗口高度
CENTERWIDTH = int(WIDTH // 2)
CENTERHEIGHT = int(HEIGHT // 2)
FPS = 30  # 帧率
SPLITBASE = 1.01  # 分裂基数
pi = math.pi#pi常量，用来画圆
INITIALWEIGHT = 20  # 初始重量
BALLCOLOR: tuple[int, int, int] = (0, 0, 0 )

# 定义颜色变量
LIGHTBLACK = (10, 51, 71)#根据三原色值调出背景色
LIGHTBLUE = (51, 102, 205)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)



# 定义键盘控制方向变量
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

#字体
fontObj = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 20)  # 字体对象，用的是系统字体
winfont = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 36)
large_fontObj = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 48)  # 加大的字体

background = pygame.image.load('nailong2.png')#初始化加载页面图片
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # 调整图像大小以适应屏幕
photo= pygame.image.load('nailong3.png')

pygame.mixer.music.load('music.mp3')
pygame.mixer.music.play(loops=-1, start=0.0)  # 无限循环播放背景音乐

text = fontObj.render("按任意键开始游戏", True, (255, 255, 0))  # 白色文字
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  # 文字居中
pygame.display.set_caption("奶龙大作战")#窗口名称
class Joystick:#定义摇杆控制类
    def __init__(self, center_x, center_y, outer_radius, inner_radius):
        self.center_x = center_x#中心坐标
        self.center_y = center_y
        self.outer_radius = outer_radius#摇杆外圈半径
        self.inner_radius = inner_radius#摇杆内圈半径
        self.stick_x = center_x#中杆中心坐标同上
        self.stick_y = center_y
        self.joystick_angle = 0#偏移角度
        self.joystick_distance = 0#偏移距离
        self.active = False  # 是否激活摇杆

    def _is_inside_outer_circle(self, x, y):#摇杆控制函数，判读鼠标是否在摇杆范围内
        return math.hypot(x - self.center_x, y - self.center_y) <= self.outer_radius

    def _calculate_angle_distance(self, x, y):#角度计算函数
        dx = x - self.center_x
        dy = y - self.center_y
        angle = math.atan2(dy, dx)
        distance = min(math.hypot(dx, dy), self.outer_radius - self.inner_radius)
        return angle, distance

    def handle_event(self, event):#监测鼠标事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self._is_inside_outer_circle(mouse_x, mouse_y):
                self.active = True
        elif event.type == pygame.MOUSEMOTION and self.active:
            mouse_x, mouse_y = event.pos
            self.joystick_angle, self.joystick_distance = self._calculate_angle_distance(mouse_x, mouse_y)
            self.stick_x = self.center_x + self.joystick_distance * math.cos(self.joystick_angle)#更新中杆位置
            self.stick_y = self.center_y + self.joystick_distance * math.sin(self.joystick_angle)
        elif event.type == pygame.MOUSEBUTTONUP:#松开重置
            self.active = False
            self.stick_x, self.stick_y = self.center_x, self.center_y
            self.joystick_angle, self.joystick_distance = 0, 0

    def draw(self, screen):#绘图函数
        # 绘制外圆
        pygame.draw.circle(screen, (200, 200, 200), (self.center_x, self.center_y), self.outer_radius, 2)
        # 绘制内圆
        pygame.draw.circle(screen, (255, 255, 255), (int(self.stick_x), int(self.stick_y)), self.inner_radius)


# 定义球球类
class Ball():
    def __init__(self, xpos, ypos, weight, color,image):  # 定义球的x，y，重量，颜色
        self.xpos = xpos
        self.ypos = ypos
        self.radius = weightToRadius(weight)
        self.weight = weight
        self.speed = weightToSpeed(weight)
        self.color = color
        if image:
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))  # 调整图像大小
            pygame.display.update()
        else:
            self.image = None

    def move1(self, direction):  # 小球移动
        rec = pygame.Rect(-HALFWWIDTH, -HALFWHEIGHT, WORLDWIDTH, WORLDHEIGHT)
        if direction == UP:#键位控制
            if rec.top < self.ypos - self.radius:  # 限制在上地图（世界）边界以下
                self.ypos -= int(self.speed // 20)#位移变换（包含速度变换）
        elif direction == DOWN:
            if rec.bottom > self.ypos + self.radius:
                self.ypos += int(self.speed // 20)
        elif direction == RIGHT:
            if rec.right > self.xpos + self.radius:
                self.xpos += int(self.speed // 20)
        elif direction == LEFT:
            if rec.left < self.xpos - self.radius:
                self.xpos -= int(self.speed // 20)
    def move2(self, joystick_angle, joystick_distance):
        # 按摇杆方向移动
            self.xpos += self.speed * joystick_distance * math.cos(joystick_angle) / 500
            self.ypos += self.speed * joystick_distance * math.sin(joystick_angle) / 500
            if self.xpos+self.radius>HALFWWIDTH:
                self.xpos=HALFWWIDTH-self.radius
            if self.xpos-self.radius<-HALFWWIDTH:
                self.xpos=-HALFWWIDTH+self.radius
            if self.ypos+self.radius>HALFWHEIGHT:
                self.ypos=HALFWHEIGHT-self.radius
            if self.ypos-self.radius<-HALFWHEIGHT:
                self.ypos =- HALFWHEIGHT+self.radius
    def split1(self, direction):  # 键盘分裂小球函数
        newweight = math.floor((self.weight // 2) * SPLITBASE)#分裂后体重
        newball = Ball(self.xpos, self.ypos, newweight, self.color,'nailong3.png')#应用类函数创建新对象
        if direction == UP:#四个键位操作
            # 分裂流畅动画
            for i in range(10):#调整此处（及以下）可实现分裂距离
                newball.ypos -= round(0.2 * self.radius)
                drawBall(newball)#画出分裂的小球
                pygame.display.update()#展示实例更新
        elif direction == DOWN:
            for i in range(10):
                newball.ypos += round(0.2 * self.radius)
                drawBall(newball)
                pygame.display.update()
        elif direction == LEFT:
            for i in range(10):
                newball.xpos -= round(0.2 * self.radius)
                drawBall(newball)
                pygame.display.update()
        elif direction == RIGHT:
            for i in range(10):
                newball.xpos += round(0.2 * self.radius)
                drawBall(newball)
                pygame.display.update()

        self.setWeight(newweight)  # 分裂完后设置球的重量
        self.image = pygame.transform.scale(pygame.image.load('nailong3.png'),(self.radius * 2, self.radius * 2))  # 调整图像大小
        selfBalls.append(newball)#更新self球
    def split2(self,joystick_angle):
        SPLITBASE = 0.8
        newweight = math.floor((self.weight // 2) * SPLITBASE)
        move_distance = round(0.2 * self.radius)
        newball = Ball(self.xpos, self.ypos, newweight, self.color,'nailong3.png')
        # 分裂 10 次，分布在摇杆的角度方向上
        # random_angle_offset = random.uniform(-0.1, 0.1)  # 随机微调角度
        # joystick_angle += random_angle_offset
        for i in range(10):
            # 计算新位置，使用摇杆角度进行方向偏移
            newball.xpos +=  move_distance * math.cos(joystick_angle)
            newball.ypos +=  move_distance * math.sin(joystick_angle)
            # 绘制小球
            drawBall(newball)
            pygame.display.update()
            # 更新显示
        self.setWeight(newweight)  # 分裂完后设置球的重量
        self.image = pygame.transform.scale(pygame.image.load('nailong3.png'),(self.radius * 2, self.radius * 2))  # 调整图像大小
        selfBalls.append(newball)  # 更新self球



    def setWeight(self, newweight):
        self.weight = newweight
        self.speed = weightToSpeed(newweight)
        self.radius = weightToRadius(newweight)

    def eatFood(self):  # 吃食物
        global foodlist
        selfworldx = self.xpos
        selfworldy = self.ypos
        for food in foodlist:
            distance = math.sqrt((selfworldx - food.xpos) * (selfworldx - food.xpos) + (selfworldy - food.ypos) * (
                        selfworldy - food.ypos))#距离公式
            if distance < self.radius:#吃掉食物/小球
                self.setWeight(self.weight + food.weight)#更新体重
                foodlist.remove(food)#消除食物
                self.image = pygame.transform.scale(pygame.image.load('nailong3.png'), (self.radius * 2, self.radius * 2))  # 调整图像大小

# 食物类
class Food():
    def __init__(self, xpos, ypos, weight, color, radius):
        self.xpos = xpos
        self.ypos = ypos
        self.weight = weight
        self.color = color
        self.radius = radius


# 其他球类
class OtherBall():
    def __init__(self, xpos, ypos, weight, color,image):
        self.xpos = xpos
        self.ypos = ypos
        self.weight = weight
        self.radius = weightToRadius(weight)
        self.speed = weightToSpeed(weight)
        self.color = color
        self.direction = random.uniform(0, 2 * pi)  # 方向角度
        if image:
            self.image_raw = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image_raw, (self.radius * 2, self.radius * 2))  # 调整图像大小
            pygame.display.update()
        else:
            self.image = None

    def eatFood(self):
        global foodlist
        for food in foodlist:
            distance = math.sqrt((self.xpos - food.xpos) ** 2 + (self.ypos - food.ypos) ** 2)
            if distance < self.radius:
                self.setWeight(self.weight + food.weight)
                foodlist.remove(food)
                self.image = pygame.transform.scale(self.image_raw, (self.radius * 2, self.radius * 2))  # 调整图像大小


    def setWeight(self, newweight):
        self.weight = newweight
        self.speed = weightToSpeed(newweight)
        self.radius = weightToRadius(newweight)

    def move(self):  # 使小球能在方框内移动
        rec = pygame.Rect(-HALFWWIDTH, -HALFWHEIGHT, WORLDWIDTH, WORLDHEIGHT)
        if rec.left > self.xpos:
            self.direction = pi - self.direction
            self.xpos += self.speed // 10  # 之前没有这句，小球在碰撞几次墙壁之后就会跳动着出界
        if rec.right < self.xpos:
            self.direction = pi - self.direction
            self.xpos -= self.speed // 10
        if rec.top > self.ypos:
            self.direction = 2 * pi - self.direction
            self.ypos += self.speed // 10
        if rec.bottom < self.ypos:
            self.direction = 2 * pi - self.direction
            self.ypos -= self.speed // 10
        self.xpos += math.floor(math.cos(self.direction) * self.speed // 40)
        self.ypos -= math.floor(math.sin(self.direction) * self.speed // 40)

def showControlSelection():#选择控制方式
    while True:
        keyboard_button = pygame.Rect(WIDTH // 4 - 100, HEIGHT // 2 - 50, 200, 100)  # 创建按钮
        joystick_button = pygame.Rect(3 * WIDTH // 4 - 100, HEIGHT // 2 - 50, 200, 100)
        DISPLAYSURF.blit(background, (0, 0))
        # pygame.draw.rect(DISPLAYSURF, (255, 255, 0), keyboard_button)  # 黄色按钮（键盘控制）
        # pygame.draw.rect(DISPLAYSURF, (255, 255, 0), joystick_button)  # 黄色按钮（摇杆控制）
        # displayText("你要怎么操控奶龙", fontObj, BLACK, WIDTH // 2, HEIGHT // 4)
        pygame.draw.ellipse(DISPLAYSURF, (255, 255, 0), keyboard_button)  # 黄色按钮（键盘控制）
        pygame.draw.ellipse(DISPLAYSURF, (255, 255, 0), joystick_button)  # 黄色按钮（摇杆控制）

        # 绘制按钮边框（可以添加一个边框效果）
        pygame.draw.ellipse(DISPLAYSURF, (0, 0, 0), keyboard_button, 3)  # 黑色边框
        pygame.draw.ellipse(DISPLAYSURF, (0, 0, 0), joystick_button, 3)  # 黑色边框

        displayText("请选择你的奶龙", large_fontObj, (0, 0, 0), WIDTH // 2, HEIGHT // 6)
        displayText("键盘奶龙", fontObj, (0, 0, 0), keyboard_button.centerx, keyboard_button.centery)
        displayText("摇杆奶龙", fontObj, (0, 0, 0), joystick_button.centerx, joystick_button.centery)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if keyboard_button.collidepoint(mouse_x, mouse_y):
                    return "keyboard"
                if joystick_button.collidepoint(mouse_x, mouse_y):
                    return "joystick"
def displayText(text, fontObj, textcolor, xpos, ypos):  # 显示字函数
    textsurf = fontObj.render(text, True, textcolor)
    textRect = textsurf.get_rect()
    textRect.center = (xpos, ypos)
    DISPLAYSURF.blit(textsurf, textRect)


def balleatBall():  # 我方球吃其他球，本游戏不设置其他球互吃
    global selfBalls, otherBalls
    for ball1 in selfBalls:
        for ball2 in otherBalls:
            distance = math.sqrt((ball1.xpos - ball2.xpos) ** 2 + (ball1.ypos - ball2.ypos) ** 2)
            if distance < (ball1.radius + ball2.radius) / 2:
                if ball1.radius > ball2.radius + 3:#数字是吞噬严格程度，越大越容易
                    ball1.setWeight(ball1.weight + ball2.weight)
                    otherBalls.remove(ball2)#清除其他球
                elif ball1.radius + 3 < ball2.radius:
                    ball2.setWeight(ball1.weight + ball2.weight)
                    selfBalls.remove(ball1)


def unite():  # 联合两个小球
    global selfBalls
    for ball1 in selfBalls:
        for ball2 in selfBalls:
            if ball1 != ball2:
                distance = math.sqrt((ball1.xpos - ball2.xpos) ** 2 + (ball1.ypos - ball2.ypos) ** 2)
                if distance < (ball1.radius + ball2.radius) / 2:
                    ball1.setWeight(ball1.weight + ball2.weight)
                    selfBalls.remove(ball2)


def createFood(foodlist):
    xpos = random.randint(-HALFWWIDTH, HALFWWIDTH)
    ypos = random.randint(-HALFWHEIGHT, HALFWHEIGHT)
    weight = 5  # 每个食物的重量
    radius = 3  # 每个食物的半径
    newfood = Food(xpos, ypos, weight, randomColor(), radius)
    foodlist.append(newfood)


def drawFoods(foodlist):
    global camerax, cameray
    for food in foodlist:
        pygame.draw.circle(DISPLAYSURF, food.color, ((food.xpos - camerax), (food.ypos - cameray)), food.radius)


def drawBalls(balls):  # 画所有球
    global camerax, cameray#摄像头视角
    for ball in balls:
        pos = (ball.xpos - camerax, ball.ypos - cameray)
        radius = ball.radius#返回当前球的半径
        if ball.image:  # 如果有图片，绘制图片
            # 计算图片绘制的位置，使得图像的中心与球的中心对齐
            image_rect = ball.image.get_rect(center=pos)
            DISPLAYSURF.blit(ball.image, image_rect.topleft)  # 绘制图片
        else:  # 如果没有图片，绘制颜色圆形
            pygame.draw.circle(DISPLAYSURF, ball.color, pos, radius)  # 绘制圆形
        # color = ball.color  # 如果没有图片，使用颜色绘制圆形
        # pygame.draw.circle(DISPLAYSURF, color, pos, radius)  # 绘制圆形


def weightToSpeed(weight):  # 重量转换为速度
    if weight < 8000:
        return math.floor(-0.02 * weight + 200)
    elif weight >= 8000:
        return 40  # 最低速度为40


def weightToRadius(weight):  # 将小球的重量转化为半径
    if weight < 100:
        return math.floor(0.1 * weight + 10)
    elif weight >= 100:
        return math.floor(2 * math.sqrt(weight))


def drawBorder(rec):  # 画边界
    borderthick = 5#边框厚度
    pygame.draw.rect(DISPLAYSURF, WHITE, rec, borderthick)#死区长宽高计算公式
    recleft = (rec[0] - CENTERWIDTH, rec[1] - CENTERHEIGHT, CENTERWIDTH, WORLDHEIGHT + HEIGHT)
    recright = (rec[0] + WORLDWIDTH, rec[1] - CENTERHEIGHT, CENTERWIDTH, WORLDHEIGHT + HEIGHT)
    rectop = (rec[0], rec[1] - CENTERHEIGHT, WORLDWIDTH, CENTERHEIGHT)
    recbottom = (rec[0], rec[1] + WORLDHEIGHT, WORLDWIDTH, CENTERHEIGHT)
    pygame.draw.rect(DISPLAYSURF, BLACK, recleft, 0)#绘制黑色死区
    pygame.draw.rect(DISPLAYSURF, BLACK, rectop, 0)
    pygame.draw.rect(DISPLAYSURF, BLACK, recright, 0)
    pygame.draw.rect(DISPLAYSURF, BLACK, recbottom, 0)


def drawBall(Obj):

    pygame.draw.circle(DISPLAYSURF, Obj.color, (Obj.xpos, Obj.ypos), Obj.radius)


def randomColor():  # 随机获取颜色
    BALLCOLOR=(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
    if BALLCOLOR!=LIGHTBLACK:
        return BALLCOLOR#防止小球随机色变成背景色


def main():
    global FPSCLOCK, DISPLAYSURF, cameray, camerax, selfBalls, otherBalls, foodlist, rec  # 设置全局变量
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))

    camerax = -CENTERWIDTH
    cameray = -CENTERHEIGHT
    dirction = ''

    control_mode = None  # None 表示还未选择控制方式
    # 定义小球列表
    selfBalls = []
    otherBalls = []
    foodlist = []

    while control_mode is None:

        control_mode = showControlSelection()
    for i in range(5):  # 创建其他小球
        xpos = random.randint(-HALFWWIDTH, HALFWWIDTH)#随机出生在中区
        ypos = random.randint(-HALFWHEIGHT, HALFWHEIGHT)
        otherb = OtherBall(xpos, ypos, INITIALWEIGHT, randomColor(),"nailong3.png")#创建其他小球对象
        otherBalls.append(otherb)

    for i in range(100):  # 初始化创建100个食物
        createFood(foodlist)

    ball = Ball(0, 0, INITIALWEIGHT, randomColor(),"nailong3.png")  # 建立第一个小球，后面参数都有写
    selfBalls.append(ball)#添加进balls列表

    joystick = Joystick(50, 450, 50, 20)

    fontObj = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 20)  # 字体对象，用的是系统字体
    winfont = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 36)

    allweight = 0
    # fontObj = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 20)  # 字体对象，用的是系统字体
    # winfont = pygame.font.Font('C:/Windows/Fonts/msyh.ttc', 36)

    while True:#监视事件
        DISPLAYSURF.fill(LIGHTBLACK)
        # pygame.event.pump()# 背景填充，作为displaysurf的类处理
        for event in pygame.event.get():
            if event.type == QUIT:
                time.sleep(3)
                exit()
            if control_mode=="keyboard":
                if event.type == KEYDOWN:  # 响应键盘
                    if event.key == K_w:
                        dirction = UP
                    elif event.key == K_s:
                        dirction = DOWN
                    elif event.key == K_d:
                        dirction = RIGHT
                    elif event.key == K_a:
                        dirction = LEFT
                    elif event.key == K_j:  # 分裂
                        count = len(selfBalls)
                        if count < 16:
                            for i in range(count):
                                if selfBalls[i].weight > 20:
                                    selfBalls[i].split1(dirction)
            elif control_mode=="joystick":
                if event.type == pygame.KEYDOWN:
                    if event.key == K_j:
                        count = len(selfBalls)
                        if count < 16:
                            for i in range(count):
                                if selfBalls[i].weight > 20:
                                    selfBalls[i].split2(joystick.joystick_angle)
                                    pygame.display.update()
            joystick.handle_event(event)





        rec = pygame.Rect(-(camerax + HALFWHEIGHT), -(cameray + HALFWHEIGHT), WORLDWIDTH, WORLDHEIGHT)  # 边界矩形
        drawBorder(rec)


        text = '重量：' + str(allweight) + '   奶龙还剩：' + str(len(otherBalls))
        displayText(text, fontObj, WHITE, 200, 20)
        if len(foodlist) < 500:  # 当食物数量小于500时，增加食物
            createFood(foodlist)
        drawFoods(foodlist)

        if len(otherBalls) > 0:  # 当其他球还有的时候进行吃球的操作
            balleatBall()
        if len(otherBalls) == 0 or allweight >= 10000:  # 胜利条件
            displayText('你是' + str(allweight) + '斤的奶龙！', winfont, RED, CENTERWIDTH, CENTERHEIGHT)
            pygame.display.update()
            time.sleep(3)
            pygame.quit()
        if len(selfBalls) == 0:
            displayText('你不是奶龙！', winfont, RED, CENTERWIDTH, CENTERHEIGHT)
            pygame.display.update()
            time.sleep(3)
            pygame.quit()
        allweight = 0
        for b in selfBalls:  # 得到所有重量和移动所有球
            allweight += b.weight
            if control_mode == "keyboard":
                b.move1(dirction)
            elif control_mode == "joystick":
                joystick.draw(DISPLAYSURF)
                # pygame.display.flip()
                b.move2(joystick.joystick_angle, joystick.joystick_distance)
        for b in otherBalls:  # 移动其他的球
            b.move()
            b.eatFood()

        drawBalls(selfBalls)

        camerax = selfBalls[0].xpos - CENTERWIDTH
        cameray = selfBalls[0].ypos - CENTERHEIGHT

        for ball in selfBalls:
            ball.eatFood()#使用和吃食物同样的函数来计算吃球

        drawBalls(otherBalls)

        if len(selfBalls) >= 2:
            unite()
        pygame.display.update()
        FPSCLOCK.tick(FPS)



if __name__ == "__main__":
    main()