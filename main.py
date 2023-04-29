import random
import berserk
from chess import Board, Move, SQUARES

def read_api_key(file_name):
    with open(file_name, 'r') as f:
        return f.readline().strip()

api_key_file = 'api_key.txt'
TOKEN = read_api_key(api_key_file)
lichess_api = berserk.Client(berserk.TokenSession(TOKEN))


def get_leftmost_pawn(board, start_square=0):
    bot_color = board.turn
    for sq in range(start_square, 64):
        piece = board.piece_at(sq)
        if piece and piece.piece_type == 1 and piece.color == bot_color:
            return sq
    return None

def get_leftmost_pawn_moves(board, leftmost_pawn):
    moves = []
    for move in board.legal_moves:
        if move.from_square == leftmost_pawn:
            moves.append(move)
    return moves

def get_move_priority(move, board):
    priorities = {'enpassent_left': 1, 'left': 2, 'enpassent_right': 3, 'right': 4, 'advance_two': 5, 'advance_one': 6}
    board.push(move)
    if board.is_en_passant(move):
        if move.to_square % 8 < move.from_square % 8:
            priority = 'enpassent_left'
        else:
            priority = 'enpassent_right'
    elif move.to_square % 8 < move.from_square % 8:
        priority = 'left'
    elif move.to_square % 8 > move.from_square % 8:
        priority = 'right'
    elif move.to_square - move.from_square == 16:
        priority = 'advance_two'
    else:
        priority = 'advance_one'
    board.pop()
    return priorities[priority]

def choose_move(moves, board):
    if not moves:
        return None
    return min(moves, key=lambda move: get_move_priority(move, board))

def play_random_move(board):
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves) if legal_moves else None

def play_move(game_id, board):
    if board.turn and not board.is_game_over():
        leftmost_pawn = get_leftmost_pawn(board)
        while leftmost_pawn is not None:
            moves = get_leftmost_pawn_moves(board, leftmost_pawn)
            move = choose_move(moves, board)
            if move:
                lichess_api.board.make_move(game_id, move)
                break
            else:
                leftmost_pawn = get_leftmost_pawn(board, start_square=leftmost_pawn + 1)


def get_leftmost_pawn(board, start_square=0):
    bot_color = board.turn
    for sq in range(start_square, 64):
        piece = board.piece_at(sq)
        if piece and piece.piece_type == 1 and piece.color == bot_color:
            return sq
    return None



def main():
    for event in lichess_api.board.stream_incoming_events():
        if event['type'] == 'challenge':
            challenge_id = event['challenge']['id']
            lichess_api.challenges.accept(challenge_id)
        elif event['type'] == 'gameStart':
            game_id = event['game']['id']
            board = Board()
            while not board.is_game_over():
                updates = lichess_api.board.stream_game_state(game_id)
                for update in updates:
                    if update['type'] == 'gameFull' or update['type'] == 'gameState':
                        if 'moves' in update:
                            moves = update['moves'].split(' ')
                            new_moves = moves[len(board.move_stack):]
                            for move in new_moves:
                                board.push_san(move)
                        if board.turn and not board.is_game_over():
                            play_move(game_id, board)



if __name__ == '__main__':
    main()
