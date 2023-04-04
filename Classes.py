class GamingField:
    def __init__(self, *, turn, roll, win_0, win_1):
        self.field = dict(zip(range(15), [None for _ in range(16)]))
        self.player_0 = Player(0, self, roll, win_0)
        self.player_1 = Player(1, self, roll, win_1)
        self.players = {0: self.player_0, 1: self.player_1}
        self.turn = turn
        self.current_player = self.players[self.turn]

        for i in range(5):
            self.field[i] = [None, None]
        for i in range(13, 15):
            self.field[i] = [None, None]

    def restore_piece(self, piece):
        if piece.pos < 5 or piece.pos > 12:
            self.field[piece.pos][piece.player] = piece
        else:
            self.field[piece.pos] = piece

    def place_piece(self, piece):
        if self.field[piece.pos][piece.player] is None:
            self.field[piece.pos][piece.player] = piece
            if piece.pos == 4:
                self.turn = (self.turn + 1) % 2
            return True
        return False

    def move_piece(self, piece):
        if piece.pos in (4, 8, 14):
            self.turn = (self.turn + 1) % 2

        if not self.is_move_valid:
            return False

        elif piece.pos > 14:
            piece_index = self.current_player.active_pieces.index(piece)
            del self.current_player.active_pieces[piece_index]
            return 'win'

        elif piece.pos < 5 or piece.pos > 12 and piece.old_pos > 12:
            self.field[piece.old_pos][piece.player] = None
            self.field[piece.pos][piece.player] = piece

        elif piece.pos > 12 > piece.old_pos:
            self.field[piece.old_pos] = None
            self.field[piece.pos][piece.player] = piece

        elif piece.pos > 4 and piece.old_pos < 5:
            self.field[piece.old_pos][piece.player] = None
            self.field[piece.pos] = piece

        else:
            self.field[piece.old_pos] = None
            self.field[piece.pos] = piece
        return True

    def is_move_valid(self, piece):
        if piece.pos < 5 or piece.pos > 12:
            if self.field[piece.pos][piece.player] is None:
                return True
        else:
            if self.field[piece.pos] is None:
                return True
            elif self.field[piece.pos].player != piece.player:
                if piece.pos == 8 and self.field[piece.pos] is not None:
                    piece.pos += 1
                    self.is_move_valid(piece)
                else:
                    replaced_piece_index = self.current_player.active_pieces.index(self.field[piece.pos])
                    del self.players[(self.turn + 1) % 2].active_pieces[replaced_piece_index]
                    return True
        return False


class Player:
    def __init__(self, num, field, roll, win):
        self.active_pieces = []
        self.num = num
        self.field = field
        self.roll = roll
        self.win = win

    def place_new_piece(self, pos):
        pieces_amount = len(self.active_pieces)
        left = 7 - self.win - pieces_amount
        if left > 0:
            new_piece = Piece(self, pos)
            is_placed = self.field.place_piece(new_piece)
            if is_placed:
                self.active_pieces.append(new_piece)
            return is_placed
        return 'too'

    def restore_piece(self, pos):
        piece = Piece(self, pos)
        self.field.restore_piece(piece)
        self.active_pieces.append(piece)

    def move_piece(self, piece):
        piece.old_pos = piece.pos
        piece.pos += self.roll
        is_moved = self.field.move_piece(piece)
        return is_moved


class Piece:
    def __init__(self, player, pos):
        self.id = len(player.active_pieces) + 1
        self.pos = pos
        self.player = player.num
        self.old_pos = 0
