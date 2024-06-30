import pygame
import random
import copy
import json

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 400, 500
TILE_SIZE = WIDTH // 4
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
FONT = pygame.font.SysFont('arial', 40)
SMALL_FONT = pygame.font.SysFont('arial', 24)

def draw_board(screen, board, score, high_score):
    screen.fill(BACKGROUND_COLOR)
    for i in range(4):
        for j in range(4):
            value = board[i][j]
            color = TILE_COLORS.get(value, TILE_COLORS[2048])
            pygame.draw.rect(screen, color, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if value != 0:
                text = FONT.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=(j * TILE_SIZE + TILE_SIZE / 2, i * TILE_SIZE + TILE_SIZE / 2))
                screen.blit(text, text_rect)

    score_text = SMALL_FONT.render(f"Score: {score}", True, (0, 0, 0))
    high_score_text = SMALL_FONT.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(score_text, (10, HEIGHT - 90))
    screen.blit(high_score_text, (10, HEIGHT - 60))
    pygame.display.update()

def initialize_board():
    board = [[0] * 4 for _ in range(4)]
    return board

def add_random_tile(board):
    empty_positions = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_positions:
        i, j = random.choice(empty_positions)
        board[i][j] = random.choice([2, 4])

def move_left(board):
    new_board = []
    score = 0
    for row in board:
        new_row = [num for num in row if num != 0]
        for i in range(len(new_row) - 1):
            if new_row[i] == new_row[i + 1]:
                new_row[i] *= 2
                score += new_row[i]
                new_row[i + 1] = 0
        new_row = [num for num in new_row if num != 0]
        new_row += [0] * (4 - len(new_row))
        new_board.append(new_row)
    return new_board, score

def move_right(board):
    reversed_board = [row[::-1] for row in board]
    new_board, score = move_left(reversed_board)
    return [row[::-1] for row in new_board], score

def transpose(board):
    return [list(row) for row in zip(*board)]

def move_up(board):
    transposed_board = transpose(board)
    new_board, score = move_left(transposed_board)
    return transpose(new_board), score

def move_down(board):
    transposed_board = transpose(board)
    new_board, score = move_right(transposed_board)
    return transpose(new_board), score

def handle_input(board, move):
    if move == pygame.K_w or move == pygame.K_UP:
        return move_up(board)
    elif move == pygame.K_s or move == pygame.K_DOWN:
        return move_down(board)
    elif move == pygame.K_a or move == pygame.K_LEFT:
        return move_left(board)
    elif move == pygame.K_d or move == pygame.K_RIGHT:
        return move_right(board)
    return board, 0

def is_game_over(board):
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return False
            if i < 3 and board[i][j] == board[i + 1][j]:
                return False
            if j < 3 and board[i][j] == board[i][j + 1]:
                return False
    return True

def save_game(board, score, high_score):
    game_state = {
        'board': board,
        'score': score,
        'high_score': high_score
    }
    with open('savegame.json', 'w') as f:
        json.dump(game_state, f)
    print("Game saved!")

def load_game():
    try:
        with open('savegame.json', 'r') as f:
            game_state = json.load(f)
        return game_state['board'], game_state['score'], game_state['high_score']
    except FileNotFoundError:
        print("No saved game found!")
        return initialize_board(), 0, 0

def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        print(f"New High Score: {high_score}")
    return high_score

def animate_move(screen, old_board, new_board, score, high_score, direction):
    steps = 10
    delay = 20  # milliseconds

    old_positions = {(i, j): (i, j) for i in range(4) for j in range(4) if old_board[i][j] != 0}
    for step in range(steps + 1):
        screen.fill(BACKGROUND_COLOR)
        for i in range(4):
            for j in range(4):
                value = old_board[i][j]
                if value != 0:
                    start_pos = old_positions[(i, j)]
                    end_pos = (i, j)
                    if direction == 'left':
                        new_pos = (start_pos[0], start_pos[1] - (start_pos[1] - end_pos[1]) * step / steps)
                    elif direction == 'right':
                        new_pos = (start_pos[0], start_pos[1] + (end_pos[1] - start_pos[1]) * step / steps)
                    elif direction == 'up':
                        new_pos = (start_pos[0] - (start_pos[0] - end_pos[0]) * step / steps, start_pos[1])
                    elif direction == 'down':
                        new_pos = (start_pos[0] + (end_pos[0] - start_pos[0]) * step / steps, start_pos[1])

                    new_pos = (int(new_pos[0] * TILE_SIZE), int(new_pos[1] * TILE_SIZE))
                    color = TILE_COLORS.get(value, TILE_COLORS[2048])
                    pygame.draw.rect(screen, color, (new_pos[1], new_pos[0], TILE_SIZE, TILE_SIZE))
                    text = FONT.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(new_pos[1] + TILE_SIZE / 2, new_pos[0] + TILE_SIZE / 2))
                    screen.blit(text, text_rect)

        score_text = SMALL_FONT.render(f"Score: {score}", True, (0, 0, 0))
        high_score_text = SMALL_FONT.render(f"High Score: {high_score}", True, (0, 0, 0))
        screen.blit(score_text, (10, HEIGHT - 90))
        screen.blit(high_score_text, (10, HEIGHT - 60))
        pygame.display.update()
        pygame.time.delay(delay)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('2048')
    clock = pygame.time.Clock()

    load = input("Load saved game? (y/n): ")
    if load.lower() == 'y':
        game_board, score, high_score = load_game()
    else:
        game_board = initialize_board()
        add_random_tile(game_board)
        add_random_tile(game_board)
        score = 0
        high_score = 0

    draw_board(screen, game_board, score, high_score)
    print(f"Score: {score}")
    print(f"High Score: {high_score}")

    previous_board = copy.deepcopy(game_board)
    previous_score = score

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    previous_board = copy.deepcopy(game_board)
                    previous_score = score

                    new_board, move_score = handle_input(game_board, event.key)
                    if new_board != game_board:
                        direction = None
                        if event.key in [pygame.K_w, pygame.K_UP]:
                            direction = 'up'
                        elif event.key in [pygame.K_s, pygame.K_DOWN]:
                            direction = 'down'
                        elif event.key in [pygame.K_a, pygame.K_LEFT]:
                            direction = 'left'
                        elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                            direction = 'right'

                        animate_move(screen, game_board, new_board, score, high_score, direction)
                        
                        game_board = new_board
                        score += move_score
                        add_random_tile(game_board)
                        draw_board(screen, game_board, score, high_score)
                        high_score = update_high_score(score, high_score)
                        if is_game_over(game_board):
                            print("Game Over! No more moves possible.")
                            print(f"Final Score: {score}")
                            running = False
                    else:
                        print("No valid move in that direction!")
                elif event.key == pygame.K_u:
                    game_board = previous_board
                    score = previous_score
                    draw_board(screen, game_board, score, high_score)
                elif event.key == pygame.K_s:
                    save_game(game_board, score, high_score)
                    print(f"Score: {score}")
                    print(f"High Score: {high_score}")

        draw_board(screen, game_board, score, high_score)
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
