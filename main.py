from abc import ABC, abstractmethod
from typing import ClassVar
import pygame
from math import pi, sin, cos, tan, sqrt
pygame.init()

# creating the window
WINDOW_WIDTH: int = 700
WINDOW_HEIGHT: int = 500
WINDOW: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# setting the title of the window
pygame.display.set_caption("Pong")

# setting the limit on frames per second
# we will have this many 'ticks' every second
FPS: int = 60

# the score to win the game
WINNING_SCORE = 10

# initialising the score font
SCORE_FONT = pygame.font.SysFont("Consolas", 200)
WINNER_FONT = pygame.font.SysFont("Consolas", 50)

# initialising colors to be used in the project
WHITE_COLOR: tuple[int, int, int] = (255, 255, 255)
BLACK_COLOR: tuple[int, int, int] = (  0,   0,   0)
GRAY_COLOR: tuple[int, int, int]  = ( 32,  32,  32)

# initialising numarical constants
HORIZONTAL_PADDING: int = 30
VERTICAL_PADDING: int = 30


class Drawable(ABC):
    
    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass


class Paddle(Drawable):
    WIDTH_DEFAULT: ClassVar[int] = 20
    HEIGHT_DEFAULT: ClassVar[int] = 100
    START_X = HORIZONTAL_PADDING
    START_Y = WINDOW_HEIGHT / 2 - HEIGHT_DEFAULT / 2
    COLOR_DEFAULT: ClassVar[tuple[int, int, int]] = (255, 255, 255)
    count = 0
    speed = 4
    
    def __init__(self, x, y, width=WIDTH_DEFAULT, height=HEIGHT_DEFAULT, color=WHITE_COLOR):
        # NOTE: x and y refer to the top-left coordinate
        Paddle.count += 1
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.number = Paddle.count
        self.score = 0
        self.hits = 0
        
    def draw(self, window=WINDOW):
        pygame.draw.rect(
            window, 
            self.color, 
            (self.x, self.y, self.width, self.height)
        )
        
    def moveY(self, up=True):
        if up:
            self.y = max(self.y - Paddle.speed, 0)
        else:
            self.y = min(self.y + Paddle.speed, WINDOW_HEIGHT - self.height)
            
    def reset(self):
        self.y = Paddle.START_Y


class Ball(Drawable):
    RADIUS_DEFAULT: float = 10
    START_MAX_SPEED: float = 5
    ANGLE_RANGE = 45
    START_X = WINDOW_WIDTH / 2
    START_Y = WINDOW_HEIGHT / 2
    
    def __init__(self, x=START_X, y=START_Y, radius=RADIUS_DEFAULT):
        # NOTE: x and y refer to the centre coordinate
        self.x: float = x
        self.y: float = y 
        self.radius: float = radius
        self.speedMax: float = Ball.START_MAX_SPEED
        self.speedX: float = Ball.START_MAX_SPEED
        self.speedY: float = 0
        
    def draw(self, window: pygame.Surface = WINDOW):
        pygame.draw.circle(
            window,
            WHITE_COLOR,
            (self.x, self.y),
            self.radius
        )
    
    def move(self):
        self.x += self.speedX
        self.y += self.speedY
        
        # keeping the ball within the screen
        self.x = min(WINDOW_WIDTH - self.radius, self.x)
        self.x = max(self.radius, self.x)
        self.y = min(WINDOW_HEIGHT - self.radius, self.y)
        self.y = max(self.radius, self.y)
        
    def reset(self):
        self.x = Ball.START_X
        self.y = Ball.START_Y
        self.speedMax = Ball.START_MAX_SPEED
        self.speedX = Ball.START_MAX_SPEED if self.speedX < 0 else -Ball.START_MAX_SPEED
        self.speedY = 0
  
# draws the dashes in the middle
def drawDashes(window):
    DASH_COUNT = 41
    DASH_HEIGHT = WINDOW_HEIGHT / DASH_COUNT
    DASH_WIDTH = DASH_HEIGHT / 2
    dashX = WINDOW_WIDTH / 2 - DASH_WIDTH / 2
    for i in range(DASH_COUNT):
        if i % 2:
            continue
        dashY = i * DASH_HEIGHT
        pygame.draw.rect(
            window, 
            GRAY_COLOR, 
            (dashX, dashY, DASH_WIDTH, DASH_HEIGHT)
        )


def drawScores(window: pygame.Surface, scoreleft: int, scoreright: int):
    scoreTextLeft = SCORE_FONT.render(f"{scoreleft}", 1, GRAY_COLOR)
    scoreTextRight = SCORE_FONT.render(f"{scoreright}", 1, GRAY_COLOR)
    positionLeft: tuple[float, float] = (
        WINDOW_WIDTH / 4 - scoreTextLeft.get_width() / 2, 
        WINDOW_HEIGHT / 2 - scoreTextLeft.get_height() / 2
    )
    positionRight: tuple[float, float] = (
        3 * WINDOW_WIDTH / 4 - scoreTextRight.get_width() / 2,
        WINDOW_HEIGHT / 2 - scoreTextRight.get_height() / 2
    )
    window.blit(
        scoreTextLeft, 
        positionLeft
    )
    window.blit(
        scoreTextRight, 
        positionRight
    )

# this function will call the draw functions of each object
def draw(window: pygame.Surface, objects: list[Drawable], scoreleft: int, scoreRight: int):
    
    # filling in the background color
    window.fill(BLACK_COLOR)
    
    # drawing the dashed line in the middle
    drawDashes(window)
    
    # drawing the scores
    drawScores(window, scoreleft, scoreRight)
    
    # drawing the paddles
    for object in objects:
        object.draw()
    
    # updating the display applies all of the drawing
    # this is the most resource intensive function, so we want to use it the least
    pygame.display.update()

# checks for keypresses and moves the paddles
def handlePaddleMovement(keys: pygame.key.ScancodeWrapper, paddleLeft: Paddle, paddleRight: Paddle):
    
    # checking the keys for movement of the left paddle
    if keys[pygame.K_w]:
        paddleLeft.moveY(up=True)
    if keys[pygame.K_s]:
        paddleLeft.moveY(up=False)
    
    # checking for movement of the right paddle
    if keys[pygame.K_UP]:
        paddleRight.moveY(up=True)
    if keys[pygame.K_DOWN]:
        paddleRight.moveY(up=False)

# checks for ball collisions with the top, bottom, and paddles
def handleBallCollisions(ball: Ball, paddles: list[Paddle]) -> int:
    
    # collisions with the top and bottom edges of the window
    if ball.y - ball.radius <= 0 or ball.y + ball.radius >= WINDOW_HEIGHT:
        ball.speedY *= -1
        
    # collisions with the left and right edges of the window
    if ball.x + ball.radius >= WINDOW_WIDTH:
        ball.reset()
        return 1
    if ball.x - ball.radius <= 0:
        ball.reset()
        return 2
    
    # collisions with the paddles
    for paddle in paddles:
        if (paddle.x + paddle.width <= ball.x - ball.radius or
            paddle.x >= ball.x + ball.radius or
            paddle.y >= ball.y + ball.radius or
            paddle.y + paddle.height <= ball.y - ball.radius):
            continue
        
        paddle.hits += 1    
        
        # this number will represent the y position of the ball relative to the paddle
        # it will range from [0, 1]
        diff = (ball.y - paddle.y) / paddle.height
        # this will range from [0, 60] --> [-30, 30]
        angleDeg = Ball.ANGLE_RANGE * 2 * diff - Ball.ANGLE_RANGE
        angleRad = pi * angleDeg / 180
        # if the ball is on the left side of the paddle 
        leftward = -1 if ball.x < paddle.x + paddle.width / 2 else 1
        ball.speedX = leftward * ball.speedMax * cos(angleRad)
        ball.speedY = ball.speedMax * sin(angleRad)
        
    return 0


def scoreUpdate(winner: int, paddleLeft: Paddle, paddleRight: Paddle):
    LEFT, RIGHT = 1, 2
    
    if winner == LEFT:
        paddleLeft.score += 1
    elif winner == RIGHT:
        paddleRight.score += 1
    
    if paddleLeft.score >= WINNING_SCORE or paddleRight.score >= WINNING_SCORE:
        endGame(winner, paddleLeft, paddleRight)


def endGame(winner: int, paddleLeft: Paddle, paddleRight: Paddle):
    WINDOW.fill(BLACK_COLOR)
    winnerText: pygame.Surface = WINNER_FONT.render(f"Player-{winner} Won!", 1, WHITE_COLOR)
    position: tuple[float, float] = (
        WINDOW_WIDTH / 2 - winnerText.get_width() / 2,
        WINDOW_HEIGHT / 2 - winnerText.get_height() / 2
    )
    WINDOW.blit(
        winnerText,
        position,
    )
    pygame.display.update()
    pygame.time.delay(3000)
    paddleLeft.score = 0
    paddleRight.score = 0
    paddleLeft.reset()
    paddleRight.reset()
    

def main():
    
    # flag variable to stop the main loop
    running: bool = True
    
    # initialising a Clock object
    clock: pygame.time.Clock = pygame.time.Clock()
    
    # creating the paddles
    paddleLeft = Paddle(
        x = HORIZONTAL_PADDING, 
        y = WINDOW_HEIGHT / 2 - Paddle.HEIGHT_DEFAULT / 2,
    )
    paddleRight = Paddle(
        x = WINDOW_WIDTH - HORIZONTAL_PADDING - Paddle.WIDTH_DEFAULT, 
        y = WINDOW_HEIGHT / 2 - Paddle.HEIGHT_DEFAULT / 2,
    )
    
    # creating the ball
    ball = Ball(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

    # the actual main loop
    while running:
        clock.tick(FPS)
        draw(
            WINDOW, 
            [paddleLeft, paddleRight, ball], 
            paddleLeft.score, paddleRight.score
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
        ball.move()
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        handlePaddleMovement(keys, paddleLeft, paddleRight)
        winner = handleBallCollisions(ball, [paddleLeft, paddleRight])
        if winner:
            scoreUpdate(winner, paddleLeft, paddleRight)
        
            
    pygame.quit()
    
# this ensures that the main loop is only run if this file is run itself
# it prevents the main loop from being run if the file is imported elsewhere
if __name__ == "__main__":
    main()