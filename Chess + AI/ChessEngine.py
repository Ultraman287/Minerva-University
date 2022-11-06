# from selectors import EpollSelector


class GameState():
    def __init__(self) -> None:
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]
        self.WhiteToMove = True
        self.moveLog = []
        self.move_types = {'R':self.get_rook_moves, 'N':self.get_knight_moves,'B':self.get_bishop_moves, 
                           'Q':self.get_queen_moves, 'K':self.get_king_moves, 'p':self.get_pawn_moves}
        self.white_king_loc = (7,4)
        self.black_king_loc = (0,4)
        self.check_mate = False
        self.stale_mate = False
        self.in_check = False
        self.checks = []
        self.pins = []

    '''
    Executes a move except for castling, pawn promotion and en-passant
    '''
    def make_move(self,move):
        self.board[move.startrow][move.startcol] = '--'
        
    
        if move.piecemoved[1] == 'p':

            if move.is_en_passant:
                if self.WhiteToMove: self.board[move.endrow+1][move.endcol] = '--'
                else: self.board[move.endrow-1][move.endcol] = '--'

        self.board[move.endrow][move.endcol] = move.piecemoved
        self.moveLog.append(move)
        self.WhiteToMove = not self.WhiteToMove
        
        
        if move.piecemoved == 'wK':
            self.white_king_loc = (move.endrow,move.endcol)
        elif move.piecemoved == 'bK':
            self.black_king_loc = (move.endrow,move.endcol)
        
        
        #pawn promotion
        if move.is_pawn_promotion:
            self.board[move.endrow][move.endcol] = move.piecemoved[0] + 'Q'
        
    '''
    Undos the last move that was done
    '''
  
    def undo_move(self):
        if not self.moveLog: return
        last_move = self.moveLog.pop()
        self.WhiteToMove = not self.WhiteToMove
        
        self.board[last_move.startrow][last_move.startcol] = last_move.piecemoved
        self.board[last_move.endrow][last_move.endcol] = last_move.piececaptured
        
        if last_move.piecemoved == 'wK':
            self.white_king_loc = (last_move.startrow,last_move.startcol)
        elif last_move.piecemoved == 'bK':
            self.black_king_loc = (last_move.startrow,last_move.startcol)
            
        #passanting
        
        if last_move.piecemoved[1] == 'p':
            if last_move.is_en_passant:
                if self.WhiteToMove: self.board[last_move.endrow+1][last_move.endcol] = 'bp'
                else: self.board[last_move.endrow-1][last_move.endcol] = 'wp'
        
    '''
    All moves with checks
    '''
    
    def get_valid_moves(self):
        
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.WhiteToMove:
            king_row, king_col = self.white_king_loc
        else:
            king_row, king_col = self.black_king_loc
        
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                check_piece = self.board[check_row][check_col]
                valid_squares = []
                if check_piece[1] == 'N':
                    valid_squares = [(check_row,check_col)]
                else:
                    for i in range(1,8):
                        valid_square = (king_row + check[2]*i, king_col + check[3]*i)
                        valid_squares.append(valid_square)
                        if valid_square[0]==check_row and valid_square[1]==check_col:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].piecemoved[1] != 'K':
                        if not (moves[i].endrow, moves[i].endcol) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        
        else:
            moves = self.get_all_possible_moves()
        
        return moves
    
    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.WhiteToMove:
            enemy, ally = 'b','w'
            start_row,start_col = self.white_king_loc[0], self.white_king_loc[1]
        else:
            enemy, ally = 'w','b'
            start_row, start_col = self.black_king_loc[0], self.black_king_loc[1]
        
        directions = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                end_row = start_row + i*d[0]
                end_col = start_col + i*d[1] 
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row,end_col,d[0],d[1])
                        else:
                            break
                    elif end_piece[0] == enemy:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type =='R') or \
                            (j >= 4 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemy == 'b' and 6 <= j <= 7) or (enemy == 'w' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                                    
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row,end_col,d[0],d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break
        
        
        knight_moves = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        for i, j in knight_moves:
            end_row = start_row + i
            end_col = start_col + j
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row,end_col,i,j))
        return in_check, pins, checks
        
        
        
    def is_attacked(self,r,c):
        self.WhiteToMove = not self.WhiteToMove
        
        opp_moves = self.get_all_possible_moves()
        
        self.WhiteToMove = not self.WhiteToMove
        
        for move in opp_moves:
            if move.endrow == r and move.endcol == c:
                return True
        
        return False
        
    '''
    All moves without checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[r][c][1]
                    self.move_types[piece](r,c,moves)
        return moves
                    
    '''
    Get all the valid pawn moves
    '''
    def get_pawn_moves(self,r,c,moves):
        
        pinned = False
        pin_direction = ()
        
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        
        if self.WhiteToMove:
            if self.board[r-1][c] == '--':
                if not pinned or pin_direction == (-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r,c),(r-2,c),self.board))
            if c > 0 and self.board[r-1][c-1][0] == 'b':
                if not pinned or pin_direction == (-1,-1):
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c < 7 and self.board[r-1][c+1][0] == 'b':
                if not pinned or pin_direction == (-1,1):
                    moves.append(Move((r,c),(r-1,c+1),self.board))
            
            # White en passant
            
            if r == 3:
                last_moved = self.moveLog[-1]
                if last_moved.piecemoved == 'bp' and last_moved.endcol == c-1 and last_moved.startrow == 1:
                    cur_move = Move((r,c),(2,c-1),self.board)
                    cur_move.is_en_passant = True
                    moves.append(cur_move)
                if last_moved.piecemoved == 'bp' and last_moved.endcol == c+1 and last_moved.startrow == 1:
                    cur_move = Move((r,c),(2,c+1),self.board)
                    cur_move.is_en_passant = True
                    moves.append(cur_move)
        else:
            if self.board[r+1][c] == '--':
                if not pinned or pin_direction == (1,0):
                    moves.append(Move((r,c),(r+1,c),self.board))
                    if r == 1 and self.board[r+2][c] == '--':
                        moves.append(Move((r,c),(r+2,c),self.board))
            if c > 0 and self.board[r+1][c-1][0] == 'w':
                if not pinned or pin_direction == (1,-1):
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c < 7 and self.board[r+1][c+1][0] == 'w':
                if not pinned or pin_direction == (1,1):
                    moves.append(Move((r,c),(r+1,c+1),self.board))       
            
            # Black en passant
            
            if r == 4:
                last_moved = self.moveLog[-1]
                if last_moved.piecemoved == 'wp' and last_moved.endcol == c-1 and last_moved.startrow == 6:
                    cur_move = Move((r,c),(5,c-1),self.board)
                    cur_move.is_en_passant = True
                    moves.append(cur_move)
                if last_moved.piecemoved == 'wp' and last_moved.endcol == c+1 and last_moved.startrow == 6:
                    cur_move = Move((r,c),(5,c+1),self.board)
                    cur_move.is_en_passant = True
                    moves.append(cur_move)
    '''
    Get all the valid rook moves
    '''
    def get_rook_moves(self,r,c,moves):
        
        pinned = False
        pin_direction = ()
        
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        
        enemy = 'b' if self.WhiteToMove else 'w'
        for i in range(r-1,-1,-1):
            if not pinned or pin_direction == (1,0) or pin_direction == (-1,0):
                if self.board[i][c] != '--':
                    if self.board[i][c][0] == enemy:
                        moves.append(Move((r,c),(i,c),self.board))
                    break
                moves.append(Move((r,c),(i,c),self.board))
        for i in range(r+1,8):
            if not pinned or pin_direction == (1,0) or pin_direction == (-1,0):
                if self.board[i][c] != '--':
                    if self.board[i][c][0] == enemy:
                        moves.append(Move((r,c),(i,c),self.board))
                    break
                moves.append(Move((r,c),(i,c),self.board))
        for i in range(c-1,-1,-1):
            if not pinned or pin_direction == (0,1) or pin_direction == (0,-1):
                if self.board[r][i] != '--':
                    if self.board[r][i][0] == enemy:
                        moves.append(Move((r,c),(r,i),self.board))
                    break
                moves.append(Move((r,c),(r,i),self.board))
        for i in range(c+1,8):
            if not pinned or pin_direction == (0,1) or pin_direction == (0,-1):
                if self.board[r][i] != '--':
                    if self.board[r][i][0] == enemy:
                        moves.append(Move((r,c),(r,i),self.board))
                    break
                moves.append(Move((r,c),(r,i),self.board))
        
    '''
    Get all the valid bishop moves
    '''     
    def get_bishop_moves(self,r,c,moves):
        
        pinned = False
        pin_direction = ()
        
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        enemy = 'b' if self.WhiteToMove else 'w'
        
        directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for d in directions:
            if not pinned or pin_direction == d or pin_direction == (-d[0],-d[1]):
                for i in range(1,8):
                    nr, nc = r+i*d[0], c+i*d[1]
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        if self.board[nr][nc] == '--':
                            moves.append(Move((r,c),(nr,nc),self.board))
                        else:
                            if self.board[nr][nc][0] == enemy:
                                moves.append(Move((r,c),(nr,nc),self.board))
                            break
                

    '''
    Get all the valid knight moves
    '''    
    def get_knight_moves(self,r,c,moves):
        
        pinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        
        steps = [[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],[2,1],[1,2]]
        enemy = 'b' if self.WhiteToMove else 'w'
        if not pinned:    
            for nr,nc in steps:
                if r+nr >= 0 and r+nr < 8 and c+nc >= 0 and c+nc < 8:
                    if self.board[r+nr][c+nc] == '--':
                        moves.append(Move((r,c),(r+nr,c+nc),self.board))
                    elif self.board[r+nr][c+nc][0] == enemy:
                        moves.append(Move((r,c),(r+nr,c+nc),self.board))

    '''
    Get all the valid queen moves
    '''
    def get_queen_moves(self,r,c,moves):
        self.get_rook_moves(r,c,moves)
        self.get_bishop_moves(r,c,moves)
    
    '''
    Get all the valid king moves
    '''
    def get_king_moves(self,r,c,moves):
        steps = [[-1,0],[0,-1],[1,0],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]
        ally = 'w' if self.WhiteToMove else 'b'
        for nr,nc in steps:
            if r+nr >= 0 and r+nr < 8 and c+nc >= 0 and c+nc < 8:
                if self.board[r+nr][c+nc][0] != ally:
                    if ally == 'w': self.white_king_loc = (r+nr,c+nc)
                    else: self.black_king_loc = (r+nr,c+nc)
                    
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    
                    if not in_check:
                        moves.append(Move((r,c),(r+nr,c+nc),self.board))
                    
                    if ally == 'w': self.white_king_loc = (r,c)
                    else: self.black_king_loc = (r,c)
                    

class Move():
    
    ranks_to_rows = {'1': 7,'2':6,'3':5,'4':4,'5':3,'6':2,'7':1,'8':0}
    rows_to_ranks = {v:k for k,v in ranks_to_rows.items()}
    files_to_cols = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}
    
    def __init__(self,start,end,board) -> None:
        self.startrow = start[0]
        self.startcol = start[1]
        self.endrow = end[0]
        self.endcol = end[1]
        
        self.piecemoved = board[self.startrow][self.startcol]
        self.piececaptured = board[self.endrow][self.endcol]
        self.is_pawn_promotion = (self.piecemoved == 'wp' and self.endrow == 0) or (self.piecemoved == 'bp' and self.endrow == 7)
        self.is_en_passant = False
        self.move_id = self.startrow * 1000 + self.startcol*100 + self.endrow*10 + self.endcol
        
        
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.move_id == other.move_id
        return False
        
    def get_chess_notation(self):
        return self.get_rank_file(self.startrow,self.startcol) + self.get_rank_file(self.endrow,self.endcol)
        
    def get_rank_file(self,r,c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]