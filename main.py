import pygame


pygame.init()

WIDTH, HEIGHT = 675, 500

attempts = 3 # Change the value to -1 for infinite attempts

# Set the caption
pygame.display.set_caption("Brick Breaker")

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load all the necessary images
game_over_screen = pygame.image.load("images/game_over.png")
paused_screen = pygame.image.load("images/paused_screen.png")
finished_screen = pygame.image.load("images/finished_screen.png")

# Load sound effects
fall_sound = pygame.mixer.Sound("audio/fall.wav")
collide = pygame.mixer.Sound("audio/collision.wav")
win = pygame.mixer.Sound("audio/win.mp3")
brick_sound = pygame.mixer.Sound("audio/brick.mp3")

# Add a semi-tranparent effect on the pause screen
shade_surface = pygame.Surface((WIDTH, HEIGHT)) 
shade_surface.set_alpha(150)    

paused = False
win_music = True


class Player:   
    def __init__(self):
        self.x = WIDTH//2-90
        self.y = HEIGHT-12
        self.width = 8
        self.length = 90
        self.speed = 10
        self.attempt = attempts

    def render(self):   # Renders the player
        rect_player = pygame.Rect(player.x, player.y, player.length, player.width)
        pygame.draw.rect(screen, (255, 255, 255), rect_player)
    
    def move(self):     # Controls player movement
        if keys[pygame.K_d] and player.x + player.length < WIDTH:
            player.x += player.speed
            if ball.spawned:
                ball.speed = [4, 4]     # If the player moves right, the ball will go right
                ball.spawned = False
        
        if keys[pygame.K_a] and player.x > 0:
            player.x -= player.speed
            if ball.spawned:
                ball.speed = [ -4, 4]   # If the player moves left, the ball will go left
                ball.spawned = False
    
    def respawn(self):
        player.attempt = attempts
        player.x = WIDTH//2-90
        player.y = HEIGHT-12


class Ball:
    def __init__(self):
        self.x = player.x+50
        self.y = player.y-7
        self.radius = 7
        self.speed = [0, 0]
        self.spawned = True
    
    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), (ball.x, ball.y), ball.radius)

    
    def move(self):     # Controls the ball movement
        ball.x += ball.speed[0]
        ball.y += ball.speed[1]

        if ball.x >= WIDTH or ball.x <= 0:
            pygame.mixer.Sound.play(collide)
            ball.speed[0] *= -1 # If the ball hits any of the sides, its direction in x axis will be reversed
        
        if ball.y <= 0:
            pygame.mixer.Sound.play(collide)
            ball.speed[1] *= -1 # If the ball hits the ceiling, its direction in y axis will be reversed
        
        if ball.x >= player.x and ball.x <= player.x + player.length:   # Checks for collision between the player and the ball
            if ball.y >= player.y and ball.y <= player.y + player.width:
                pygame.mixer.Sound.play(collide)
                ball.speed[1] *= -1
    
    def respawn(self):
        ball.x = player.x+50
        ball.y = player.y-ball.radius
        ball.speed = [0, 0] # The ball will not move after respawn unless the player moves
        ball.spawned = True


class Bricks:
    def __init__(self):
        self.width = 10
        self.length = 25
        self.positions = []
    
    def render_pos(self):   # Calculates the position of all the bricks
        for col in range(10, 665, 35):
            for row in range(10, 210, 20):
                bricks.positions.append((col, row, bricks.length, bricks.width))
    
    def render(self):   # Renders the bricks
        for position in bricks.positions:
            pygame.draw.rect(screen, (180, 200, 150), position)

    def collision(self):    # Checks for collision between the ball and the bricks
        if ball.y <= 210:
            rect_ball = pygame.Rect(ball.x, ball.y, ball.radius, ball.radius)
            collided_bricks = rect_ball.collideobjectsall(bricks.positions)
            if len(collided_bricks) != 0:
                for brick in collided_bricks:
                    bricks.positions.remove(brick)  # The brick will disappear upon collision
                    pygame.mixer.Sound.play(brick_sound)
                ball.speed[1] *= -1


def pause():
    clock.tick(12)  # Lower the fps when not needed
    screen.blit(shade_surface, (0, 0))
    screen.blit(paused_screen, (0, 0))

def retry():    # Returns everything back to normal
    player.respawn()
    ball.respawn()
    bricks.render_pos()

def is_finished():
    if len(bricks.positions) == 0:  # If all the bricks are gone, the game is finished
        return True
    return False

def is_game_over():
    if player.attempt == 0: # If the player runs out of attempts, the game is over
        return True
    return False


player = Player()
ball = Ball()
bricks = Bricks()

bricks.render_pos()

clock = pygame.time.Clock()
running = True

while running:
    if not paused and not is_game_over():
        clock.tick(60)
    
    screen.fill((0, 0, 0))
    
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if paused and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False  # Unpauses the game
            elif event.key == pygame.K_ESCAPE and not is_game_over() and not is_finished():
                paused = True   # Pauses the game
            elif is_game_over() and event.key == pygame.K_SPACE:
                retry()
            elif is_finished() and event.key == pygame.K_ESCAPE:  # Closes the game
                running = False
            elif is_finished() and event.key == pygame.K_SPACE:   # Starts the game again
                retry()
                win_music = True
            elif is_game_over() and event.key == pygame.K_ESCAPE:
                running = False

    if not is_game_over():
        
        # Render everything
        player.render()
        ball.render()
        bricks.render()

        if not paused:
            player.move()
            ball.move()
            bricks.collision()

            if ball.y > HEIGHT:
                pygame.mixer.Sound.play(fall_sound)
                if not is_finished():  # don't count attempts if the game is finished
                    player.attempt -= 1
                ball.respawn()

            if is_finished():
                if win_music:
                    pygame.mixer.Sound.play(win)
                    win_music = False
                screen.blit(finished_screen, (0, 0))

        elif paused:
            pause()
        
    else:
        clock.tick(12)
        screen.blit(game_over_screen, (0, 0))
        if keys[pygame.K_SPACE]:
            retry()

    pygame.display.update()
