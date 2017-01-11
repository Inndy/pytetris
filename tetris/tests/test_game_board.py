from copy import deepcopy
from tetris import game
from tetris.game.game_board import State
import unittest

class TestBoardPublicAPI(unittest.TestCase):
    def setUp(self):
        self.gameboard = game.GameBoard()
        block = game.blocks.get_block('O')
        self.gameboard.current_block = block

    def test_block_next_tick(self):
        pos = self.gameboard.current_block_pos
        expect_pos = (pos[0]+1, pos[1])
        self.gameboard.next_tick()

        self.assertEqual(expect_pos, self.gameboard.current_block_pos)

    def test_deposit_test(self):
        self.gameboard.deposit()

        self.assertEqual(self.gameboard._board[-3][5], 0)
        self.assertEqual(self.gameboard._board[-3][6], 0)
        self.assertEqual(self.gameboard._board[-3][7], 0)
        self.assertEqual(self.gameboard._board[-2][5], 1)
        self.assertEqual(self.gameboard._board[-2][6], 1)
        self.assertEqual(self.gameboard._board[-2][7], 0)
        self.assertEqual(self.gameboard._board[-1][5], 1)
        self.assertEqual(self.gameboard._board[-1][6], 1)
        self.assertEqual(self.gameboard._board[-1][7], 0)

    def test_swap_block(self):
        block = self.gameboard.current_block
        self.gameboard.swap_block()
        self.gameboard.swap_block()

        self.assertEqual(str(self.gameboard.current_block), str(block))

    def test_is_gameover(self):
        self.assertFalse(self.gameboard.is_gameover())
        self.gameboard._make_deposit()
        self.assertTrue(self.gameboard.is_gameover())


class TestBlocksMoving(unittest.TestCase):
    def setUp(self):
        self.gameboard = game.GameBoard()
        block = game.blocks.get_block('O')
        self.gameboard.current_block = block

    def test_basic_move(self):
        pos = self.gameboard.current_block_pos
        self.gameboard.move('left')
        self.gameboard.move('right')
        self.assertEqual(self.gameboard.current_block_pos, pos)

    def test_move_fail_left_edge(self):
        self.gameboard.current_block_pos = (0, 0)
        pos = self.gameboard.current_block_pos
        self.gameboard.move('left')
        self.assertEqual(self.gameboard.current_block_pos, pos)

    def test_move_fail_right_edge(self):
        self.gameboard.current_block_pos = (0, self.gameboard.width-2)
        pos = self.gameboard.current_block_pos
        self.gameboard.move('right')
        self.assertEqual(self.gameboard.current_block_pos, pos)

    def test_move_fail_right_blocks(self):
        self.gameboard._board[-3] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-2] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-1] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard.current_block_pos = (self.gameboard._height-3 ,4)
        pos = self.gameboard.current_block_pos
        
        # test target
        self.gameboard.move('right')
        self.assertEqual(self.gameboard.current_block_pos, pos)

    def test_move_fail_left_blocks(self):
        self.gameboard._board[-3] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-2] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-1] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard.current_block_pos = (self.gameboard._height-3 ,4)
        pos = self.gameboard.current_block_pos
        
        # test target
        self.gameboard.move('left')
        self.assertEqual(self.gameboard.current_block_pos, pos)

    def test_move_fail_left_blocks(self):
        self.gameboard._board[-3] = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]
        self.gameboard._board[-3] = [1, 1, 1, 1, 0, 0, 0, 1, 1, 1]
        self.gameboard._board[-2] = [1, 1, 1, 1, 0, 0, 0, 1, 1, 1]
        self.gameboard._board[-1] = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]
        self.gameboard.current_block_pos = (self.gameboard._height-3 ,4)
        pos = self.gameboard.current_block_pos

        # test target
        self.gameboard.move('right')
        self.assertEqual(self.gameboard.current_block_pos, (pos[0], pos[1]+1))

    def test_down(self):
        pos = self.gameboard.current_block_pos

        self.gameboard.down()
        self.assertEqual(self.gameboard.current_block_pos, (pos[0]+1, pos[1]))

    def test_down_and_deposit(self):
        self.gameboard.current_block_pos = (self.gameboard._height-2 ,4)
        self.gameboard.down()
        self.gameboard._board[-2] = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
        self.gameboard._board[-1] = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]


class TestBlockRotate(unittest.TestCase):
    def setUp(self):
        self.gameboard = game.GameBoard()
        self.gameboard.current_block = game.blocks.get_block('I')

    def test_success(self):
        block = self.gameboard.current_block
        self.gameboard.rotate('left')
        self.assertEqual(str(self.gameboard.current_block), str(block.rotate('left')))

    def test_rotate_deposit(self):
        self.gameboard.rotate('left')
        self.gameboard.deposit()
        self.assertEqual(self.gameboard._board[-1][5], 1)
        self.assertEqual(self.gameboard._board[-1][6], 1)
        self.assertEqual(self.gameboard._board[-1][7], 1)
        self.assertEqual(self.gameboard._board[-1][8], 1)

    def test_exception(self):
        with self.assertRaises(ValueError):
            self.gameboard.rotate('error_command')

    def test_fail(self):
        self.gameboard.current_block_pos = (self.gameboard.current_block_pos[0], self.gameboard.width - 1)
        self.assertEqual(self.gameboard._conflict_detect(), State.AllGreen)
        
        block = self.gameboard.current_block
        self.gameboard.rotate('left')
        self.assertEqual(str(self.gameboard.current_block), str(block)) # reject rotate

    def test_reject_rotate(self):
        self.gameboard._board[-3] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-2] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
        self.gameboard._board[-1] = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1]

        self.gameboard.current_block = game.blocks.get_block('S')
        self.gameboard.rotate('left')
        block = self.gameboard.current_block
        self.gameboard.current_block_pos = (self.gameboard._height-3 ,4)

        # test target
        self.gameboard.rotate('left')

        self.assertEqual(str(self.gameboard.current_block), str(block))


class TestBoardHelperFunctions(unittest.TestCase):
    def setUp(self):
        self.gameboard = game.GameBoard()
        block = game.blocks.get_block('O')
        self.gameboard.current_block = block

    def test_deposit_test(self):
        block = game.blocks.get_block('O')
        self.gameboard.current_block = block
        self.gameboard.current_block_pos = (20, 0)
        self.gameboard._make_deposit()

        self.assertEqual(self.gameboard._board[20][0], 1)
        self.assertEqual(self.gameboard._board[20][1], 1)
        self.assertEqual(self.gameboard._board[20][2], 0)
        self.assertEqual(self.gameboard._board[21][0], 1)
        self.assertEqual(self.gameboard._board[21][1], 1)
        self.assertEqual(self.gameboard._board[21][2], 0)
        self.assertEqual(self.gameboard._board[22][0], 0)
        self.assertEqual(self.gameboard._board[22][1], 0)
        self.assertEqual(self.gameboard._board[22][2], 0)


    def test_bottom_conflict_test(self):
        block = game.blocks.get_block('O')
        c_pos = (40, 0)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.OutOfBoard)

        c_pos = (self.gameboard._height, 0)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.OutOfBoard)

        c_pos = (10, 0)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.AllGreen)

    def test_edge_conflict_test(self):
        block = game.blocks.get_block('O')
        c_pos = (10, self.gameboard.width)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.OutOfBoard)

        c_pos = (10, -1)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.OutOfBoard)

        c_pos = (10, self.gameboard.width-2)
        self.assertEqual(self.gameboard._conflict_detect(block, c_pos), State.AllGreen)

        block = game.blocks.get_block('I')
        c_pos = (0, self.gameboard.width-1)
        self.assertEqual(self.gameboard._conflict_detect(), State.AllGreen)

    def test_block_conflict_test(self):
        block = game.blocks.get_block('O')
        pos = (20, 0)
        self.gameboard.current_block = block
        self.gameboard.current_block_pos = pos
        self.gameboard._make_deposit(block, pos)

        self.assertEqual(
            self.gameboard._conflict_detect(block, pos),
            State.ConflictWithBlock
        )

    def test_line_erase(self):
        block = game.blocks.get_block('O')
        top = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0]
        full = [1] * self.gameboard.width
        nfull = deepcopy(full)
        nfull[0] = 0
        self.assertNotEqual(full, nfull)

        self.gameboard._board[-1] = deepcopy(full)
        self.gameboard._board[-2] = deepcopy(full)
        self.gameboard._board[-3] = deepcopy(nfull)
        self.gameboard._board[-4] = deepcopy(full)
        self.gameboard._board[-5] = deepcopy(nfull)

        self.gameboard.deposit()

        self.assertEqual(self.gameboard._board[-1], nfull)
        self.assertEqual(self.gameboard._board[-2], nfull)
        self.assertEqual(self.gameboard._board[-3], top)

    def test_board_api(self):
        self.assertEqual(self.gameboard.get_board_copy(), self.gameboard._board)

