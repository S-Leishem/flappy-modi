import pygame
import sys
import random

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, SCREEN_HEIGHT - 100))
    screen.blit(floor_surface, (floor_x_pos + SCREEN_WIDTH, SCREEN_HEIGHT - 100))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(SCREEN_WIDTH + 100, random_pipe_pos))
    top_pipe = pygame.transform.flip(pipe_surface, False, True).get_rect(midbottom=(SCREEN_WIDTH + 100, random_pipe_pos - PIPE_GAP))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    for i, pipe in enumerate(pipes):
        if i % 2 == 0:
            screen.blit(pipe_surface, pipe)
        else:
            flipped_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flipped_pipe, pipe)

def check_collision(pipes):
    global game_active
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            pygame.mixer.music.stop()
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= SCREEN_HEIGHT - 100:
        pygame.mixer.music.stop()
        return False
    return True

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    score_display('main_game')
    return high_score

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        screen.blit(high_score_surface, high_score_rect)

        game_over_surface = game_font.render('Game Over', True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = game_font.render('Press Space to Restart', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(restart_surface, restart_rect)

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.20
JUMP_STRENGTH = -5
PIPE_SPEED = 2
PIPE_GAP = 180

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Modi")
clock = pygame.time.Clock()
game_font = pygame.font.Font(None, 40)

background_image = pygame.image.load(r'D:\all_files\codes\personal\fun\modi\recs\background.jpeg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

bird_image = pygame.image.load(r'D:\all_files\codes\personal\fun\modi\recs\character.jpg')
bird_image = pygame.transform.scale(bird_image, (40, 40))

pipe_image = pygame.image.load(r'D:\all_files\codes\personal\fun\modi\recs\pipes.jpeg')
pipe_surface = pygame.transform.scale(pipe_image, (60, 350))

pygame.mixer.music.load(r'D:\all_files\codes\personal\fun\modi\recs\audio.mp3')
pygame.mixer.music.play(loops=-1)

game_active = True
score = 0
high_score = 0
pipe_passed = False

bird_rect = bird_image.get_rect(center=(50, SCREEN_HEIGHT // 2))
bird_velocity = 0

pipe_list = []
pipe_height = [250, 300, 350, 400, 450]
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

floor_surface = pygame.Surface((SCREEN_WIDTH, 100))
floor_surface.fill(BROWN)
floor_x_pos = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_velocity = JUMP_STRENGTH
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50, SCREEN_HEIGHT // 2)
                bird_velocity = 0
                score = 0
                pipe_passed = False
                pygame.mixer.music.play(loops=-1)

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())
            pipe_passed = False

    screen.blit(background_image, (0, 0))

    if game_active:
        bird_velocity += GRAVITY
        bird_rect.y += bird_velocity

        game_active = check_collision(pipe_list)

        pipe_list = move_pipes(pipe_list)

        draw_pipes(pipe_list)

        if pipe_list:
            if bird_rect.centerx > pipe_list[0].centerx and not pipe_passed:
                score += 1
                pipe_passed = True
            high_score = update_score(score, high_score)

        screen.blit(bird_image, bird_rect)

    else:
        game_over_surface = game_font.render('Game Over', True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        screen.blit(game_over_surface, game_over_rect)

        restart_surface = game_font.render('Press Space to Restart', True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(restart_surface, restart_rect)

    draw_floor()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

sys.exit()
