import pygame
import sys
import ctypes
from utils.config import HEIGHT, WIDTH, GAP, Color, river_words
from game.board import Board
from game.menu import Menu
from .game_window import create_windown
from .menu_renderer import MenuRenderer

ctypes.windll.user32.SetProcessDPIAware()

class GameUI:
    def __init__(self):
        pygame.init()
        WIN = create_windown()
        self.win = WIN
        self.width = WIDTH
        self.height = HEIGHT
        self.menu = Menu()
        self.menu_renderer = MenuRenderer(self.win, self.menu)
        self.board = None
        self.running = False
        # Initialize buttons
        self.buttons = [
            {"text": "Undo", "rect": pygame.Rect(9.5 * GAP, 2 * GAP, 1.5 * GAP, GAP), "action": "undo"},
            {"text": "Reset", "rect": pygame.Rect(9.5 * GAP, 4 * GAP, 1.5 * GAP, GAP), "action": "reset"},
            {"text": "Quit", "rect": pygame.Rect(9.5 * GAP, 6 * GAP, 1.5 * GAP, GAP), "action": "quit"}
        ]

    def update_display(self, gameState: list, board):
        """
        Update and draw the game interface.
        """
        self.width = min(pygame.display.get_surface().get_width(),
                         pygame.display.get_surface().get_height()*9//10)
        PIECE_SIZE = GAP * 0.8
        current_turn = board.current_turn
        possible_moves, fromPos, lastPos, picked_up_piece, mouse_pos = gameState
        line_width = GAP//20

        # Draw board and frame
        self.win.fill((153, 204, 255))
        pygame.draw.rect(self.win, Color.SHADOW, (0.1*GAP, 0.1*GAP, 9.1*GAP, 10.1*GAP), border_radius=10)
        pygame.draw.rect(self.win, Color.ORANGE, (0, 0, 9*GAP, 10*GAP))
        pygame.draw.rect(self.win, Color.DARK_YELLOW, (0.5*GAP, 0.5*GAP, 8*GAP, 9*GAP))

        # Draw horizontal grid lines
        for i in range(10):
            pygame.draw.line(self.win, Color.BLACK, (0.5 * GAP, (i+0.5) * GAP),
                             (8.5 * GAP, (i+0.5) * GAP), width=line_width)
        
        # Draw vertical grid lines
        for j in range(9):
            pygame.draw.line(self.win, Color.BLACK, ((j+0.5) * GAP, 0.5 * GAP),
                             ((j+0.5) * GAP, 4.5 * GAP), width=line_width)
            pygame.draw.line(self.win, Color.BLACK, ((j+0.5) * GAP, 5.5 * GAP),
                             ((j+0.5) * GAP, 9.5 * GAP), width=line_width)
        
        # Draw the two diagonals inside the palace
        pygame.draw.line(self.win, Color.BLACK, (3.5 * GAP, 0.5 * GAP),
                         (5.5 * GAP, 2.5 * GAP), width=line_width)
        pygame.draw.line(self.win, Color.BLACK, (5.5 * GAP, 0.5 * GAP),
                         (3.5 * GAP, 2.5 * GAP), width=line_width)
        pygame.draw.line(self.win, Color.BLACK, (3.5 * GAP, 9.5 * GAP),
                         (5.5 * GAP, 7.5 * GAP), width=line_width)
        pygame.draw.line(self.win, Color.BLACK, (5.5 * GAP, 9.5 * GAP),
                         (3.5 * GAP, 7.5 * GAP), width=line_width)
        
        # Draw the pieces
        for i in range(10):
            for j in range(9):
                if board.config[i][j] and board.config[i][j] != picked_up_piece:
                    piece_gap = (GAP - PIECE_SIZE) // 2
                    center = ((j+0.5)*GAP, (i+0.56)*GAP)
                    pygame.draw.circle(self.win, Color.SHADOW, center, PIECE_SIZE//2)
                    image = pygame.transform.scale(
                        board.config[i][j].image, (PIECE_SIZE, PIECE_SIZE))
                    self.win.blit(
                        image, (piece_gap + j*GAP, piece_gap + i*GAP))
                    
        # Draw the piece being dragged by the mouse
        if picked_up_piece:
            image = pygame.transform.scale(
                picked_up_piece.image, (PIECE_SIZE, PIECE_SIZE))
            self.win.blit(
                image, (mouse_pos[0] - PIECE_SIZE//2, mouse_pos[1] - PIECE_SIZE//2))

        # Display valid moves for the currently selected piece
        for i in range(10):
            for j in range(9):
                if (i, j) in possible_moves:
                    center = ((j+0.5)*GAP, (i+0.5)*GAP)
                    radius = GAP*0.2
                    target_rect = pygame.Rect(center, (0, 0)).inflate(
                        (radius * 2, radius * 2))
                    shape_surf = pygame.Surface(
                        target_rect.size, pygame.SRCALPHA)
                    pygame.draw.circle(shape_surf, Color.GREEN,
                                       (radius, radius), radius)
                    self.win.blit(shape_surf, target_rect)

        # Highlight last position and new position of the piece
        if fromPos:
            center = ((fromPos[1]+0.5)*GAP, (fromPos[0]+0.5)*GAP)
            pygame.draw.circle(self.win, Color.PURPLE, center,
                               PIECE_SIZE*0.4, line_width)
        if lastPos:
            center = ((lastPos[1]+0.5)*GAP, (lastPos[0]+0.5)*GAP)
            radius = GAP*0.3
            target_rect = pygame.Rect(center, (0, 0)).inflate(
                (radius * 2, radius * 2))
            shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
            pygame.draw.circle(shape_surf, Color.BLUE, (radius, radius), radius)
            self.win.blit(shape_surf, target_rect)

        # Warn the player when the general is in check
        if board.is_inCheck(current_turn):
            i, j = board.find_General(current_turn)
            center = ((j+0.5)*GAP, (i+0.5)*GAP)
            radius = GAP*0.5
            target_rect = pygame.Rect(center, (0, 0)).inflate(
                (radius * 2, radius * 2))
            shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
            pygame.draw.circle(shape_surf, Color.RED, (radius, radius), radius)
            self.win.blit(shape_surf, target_rect)

        # Draw buttons
        for button in self.buttons:
            pygame.draw.rect(self.win, Color.ORANGE, button["rect"], border_radius=10)
            pygame.draw.rect(self.win, Color.DARK_YELLOW, button["rect"].inflate(-10, -10))
            text_surface = pygame.font.Font("assets/font/svn bango.ttf", 30).render(
                button["text"], True, Color.BLACK)
            text_rect = text_surface.get_rect(center=button["rect"].center)
            self.win.blit(text_surface, text_rect)

        pygame.display.update()

    def handle_button_click(self, pos):
        """
        Check if a button was clicked and perform the corresponding action.
        """
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "undo":
                    self.board.undo_move()
                elif button["action"] == "reset":
                    self.board.reset_board()
                elif button["action"] == "quit":
                    self.running = False
                    pygame.quit()
                    sys.exit()

    def play_sound(self, action: str):
        pass
