import chess
import berserk
import random


def read_api_key():
    with open("api_key.txt") as f:
        return f.read().strip()

api_key = read_api_key()
session = berserk.TokenSession(api_key)
lichess_api = berserk.Client(session)


def get_leftmost_pawn(board):
    print("get_leftmost_pawn called")
    bot_color = board.turn
    files = range(8) if bot_color else reversed(range(8))
    ranks = range(1, 3) if bot_color else reversed(range(6, 8))

    for rank in ranks:
        for file in files:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == 1 and piece.color == bot_color:
                print(f"Leftmost pawn: {square}")
                return square
    return None


def get_leftmost_pawn_moves(board, leftmost_pawn):
    moves = []

    # En passant left
    en_passant_left = board.find_move(leftmost_pawn, leftmost_pawn + 7, promotion=None)
    moves.append(en_passant_left)
    print(f"En passant left: {en_passant_left}")

    # Capture left
    capture_left = board.find_move(leftmost_pawn, leftmost_pawn + 9, promotion=None)
    moves.append(capture_left)
    print(f"Capture left: {capture_left}")

    # En passant right
    en_passant_right = board.find_move(leftmost_pawn, leftmost_pawn + 9, promotion=None)
    moves.append(en_passant_right)
    print(f"En passant right: {en_passant_right}")

    # Capture right
    capture_right = board.find_move(leftmost_pawn, leftmost_pawn + 7, promotion=None)
    moves.append(capture_right)
    print(f"Capture right: {capture_right}")

    # Advance two squares
    advance_two = board.find_move(leftmost_pawn, leftmost_pawn + 16, promotion=None)
    moves.append(advance_two)
    print(f"Advance two: {advance_two}")

    # Advance one square
    advance_one = board.find_move(leftmost_pawn, leftmost_pawn + 8, promotion=None)
    moves.append(advance_one)
    print(f"Advance one: {advance_one}")

    return moves



def choose_move(moves, board):
    for move in moves:
        if move and board.is_legal(move):
            print(f"Legal move: {move}")
            return move
        elif move:
            print(f"Illegal move: {move}")
    return None


def play_move(game_id, board):
    try:
        update = next(lichess_api.board.stream_game_state(game_id))
        board.set_fen(update["fen"])
        board.turn = update["color"] == "white"  # Set the correct turn

        if board.turn != (board.fen().split()[1] == "w"):
            print("Not our turn. Skipping move.")
            return

        leftmost_pawn = get_leftmost_pawn(board)
        moves = get_leftmost_pawn_moves(board, leftmost_pawn)
        move = choose_move(moves, board)
        if move:
            print(f"Playing move: {move}")
            move_str = move.uci()
            lichess_api.board.make_move(game_id, move_str)
            board.push(move)
        else:
            print("No legal leftmost pawn moves available.")
    except Exception as e:
        print(f"Error in play_move: {e}")




def handle_challenge(event):
    challenge_id = event['challenge']['id']
    print(f"Accepting challenge: {challenge_id}")
    try:
        lichess_api.challenges.accept(challenge_id)
    except berserk.exceptions.ResponseError as e:
        print(f"Failed to accept challenge: {e}")


def main():
    api_key = read_api_key()
    session = berserk.TokenSession(api_key)
    lichess_api = berserk.Client(session)

    for event in lichess_api.board.stream_incoming_events():
        print(f"Event: {event}")
        if event["type"] == "challenge":
            handle_challenge(event)
        elif event["type"] == "gameStart":
            game_id = event
            print(f"Game started: {game_id}")
            board = chess.Board()
            while not board.is_game_over():
                play_move(game_id, board)
                board.push(chess.Move.null())

        elif event["type"] == "gameFinish":
            print(f"Game finished: {event['game']['id']}")


if __name__ == "__main__":
    main()
