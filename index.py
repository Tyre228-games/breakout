import pygame
import time

pygame.init()
pygame.joystick.init()

# screen set up
SCREEN_WIDTH, SCREEN_HEIGHT = 700, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout")


# paddle
class Paddle():
    COLOR = (255, 255, 255)
    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.direction = None
        self.speed = 5
        self.increment_speed_counter = 0
        
    def move(self):
        if self.direction == "left" and self.x - self.speed > 0:
            self.x -= self.speed
        elif self.direction == "right" and self.x + self.width + self.speed < SCREEN_WIDTH:
            self.x += self.speed

    def increment_speed(self):
        if self.speed < 10:
            if self.increment_speed_counter >= 100:
                self.speed += 0.1
                self.increment_speed_counter = 0
            else:
                self.increment_speed_counter += 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.COLOR, (self.x, self.y, self.width, self.height))
        self.increment_speed()

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.speed = 5


# ball
class Ball():
    COLOR = (255, 255, 255)
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 5.1
        self.speed_y = -5.1
        self.acceleration_x = 0
        self.speed_increment_counter = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.COLOR, (self.x, self.y), self.radius)

    def increment_speed(self):
        if self.speed_x < 10:
            if self.speed_increment_counter >= 100:
                self.speed_increment_counter = 0
                
                if self.speed_x < 0:
                    self.speed_x -= 0.1
                else:
                    self.speed_x += 0.1
            else:
                self.speed_increment_counter += 1
        if self.speed_y < 10:
            if self.speed_increment_counter >= 100:
                self.speed_increment_counter = 0
                self.acceleration_x += 0.1
            elif self.speed_x >= 10:
                self.speed_increment_counter += 1

    def reset(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.speed_x = 5.1
        self.speed_y = -5.1

    def move(self):
        # update old x and y
        self.old_x = self.x
        self.old_y = self.y

        # check for colision with borders
        if self.is_colision_with_side_borders():
            self.speed_x *= -1
        elif self.is_colision_with_top_border():
            self.speed_y *= -1
        
        # move
        self.x += self.speed_x
        self.y += self.speed_y
        self.increment_speed()

    def is_colision_with_side_borders(self):
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            return True
        else:
            return False
        
    def is_colision_with_top_border(self):
        if self.y <= 0:
            return True
        else:
            return False
        
    def is_colision_with_bottom_border(self):
        if self.y >= SCREEN_HEIGHT:
            return True
        else:
            return False
        
    def handle_colision_with_blocks(self, blocks):
        for block_index, block in enumerate(blocks):
            if self.x + self.radius*2 >= block.x and self.x <= block.x + block.width:
                if self.y <= block.y + block.height and self.y + self.radius*2 >= block.y:
                    self.speed_y *= -1
                    blocks.pop(block_index)

    def handle_colision_with_paddle(self, paddle):
        if self.y + self.radius >= paddle.y and self.y < paddle.y + paddle.height:
            if self.x + self.radius*2 >= paddle.x and self.x <= paddle.x + paddle.width:
                self.speed_y *= -1 

                middle_x = paddle.x + paddle.width//2
                difference_in_x = middle_x - self.x / 2
                reduction_factor = (paddle.width//2)
                speed_x = difference_in_x / reduction_factor + self.acceleration_x
                self.speed_x = -1 * speed_x            


# block
class Block():
    COLOR = (255, 255, 255)
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, self.COLOR, (self.x, self.y, self.width, self.height))



# game loop variables
FPS = 60
running = True
clock = pygame.time.Clock()
blocks = []
attempts = 5
reseted_before = False
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

for row_index in range(5):
    for cell_index in range(SCREEN_WIDTH//100):
        blocks.append(Block(cell_index*100 + 2, row_index*25 + 2, 96, 21))


paddle = Paddle(SCREEN_WIDTH//2 - 47, SCREEN_HEIGHT - 51, 96, 21)
ball = Ball(paddle.x-paddle.width//2, paddle.y-30, 15)
font = pygame.font.Font(None, 36)
endgame_message = font.render("", True, (255, 255, 255))


# game loop
while running:
    screen.fill((0, 0, 0))
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                paddle.direction = "left"
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                paddle.direction = "right"
        if event.type == pygame.KEYUP:
            paddle.direction = None
        
        if event.type == pygame.JOYAXISMOTION:
            if joysticks[0].get_axis(0) > 0.4:
                paddle.direction = "right"
            elif joysticks[0].get_axis(0) < -0.4:
                paddle.direction = "left"
            else:
                paddle.direction = None

    

    paddle.move()
    ball.move()
    ball.handle_colision_with_blocks(blocks)
    ball.handle_colision_with_paddle(paddle)

    # check for win condition
    if len(blocks) <= 0:
        endgame_message = font.render("You won", True, (255, 255, 255))


    # if ball colides with bottom border
    if ball.is_colision_with_bottom_border():
        attempts -= 1
        reseted_before = True
        if attempts <= 0:
            endgame_message = font.render("You lost", True, (255, 255, 255))
        else:
            ball.reset(paddle.x+paddle.width//2, paddle.y-20)
    
    attempt_message = font.render(f"Attempts: {attempts}", True, (255, 255, 255))

    # draw
    paddle.draw(screen)
    ball.draw(screen)
    for block in blocks:
        block.draw(screen)
    screen.blit(attempt_message, (5, SCREEN_HEIGHT-5-attempt_message.get_height()))
    screen.blit(endgame_message, (SCREEN_WIDTH//2-endgame_message.get_width()//2, SCREEN_HEIGHT//2-endgame_message.get_height()//2))


    # if you lose
    if attempts <= 0:
        pygame.display.flip()
        time.sleep(3)
        paddle.reset()
        ball.reset(paddle.x-paddle.width//2, paddle.y-30)
        endgame_message = font.render("", True, (255))
        attempts = 5
        for row_index in range(5):
            for cell_index in range(SCREEN_WIDTH//100):
                blocks.append(Block(cell_index*100 + 2, row_index*25 + 2, 96, 21))
    

    # if player won
    if len(blocks) <= 0:
        pygame.display.flip()
        time.sleep(3)
        paddle.reset()
        ball.reset(paddle.x-paddle.width//2, paddle.y-30)
        endgame_message = font.render("", True, (255))
        attempts = 5
        for row_index in range(5):
            for cell_index in range(SCREEN_WIDTH//100):
                blocks.append(Block(cell_index*100 + 2, row_index*25 + 2, 96, 21))

    
    pygame.display.flip()
    if reseted_before == True:
        time.sleep(0.5)
        reseted_before = False
    clock.tick(FPS)