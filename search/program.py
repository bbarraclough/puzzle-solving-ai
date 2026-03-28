# COMP30024 Artificial Intelligence, Semester 1 2026
# Project Part A: Single Player Cascade

from .core import BOARD_N, PlayerColor, CellState, Coord, Direction, Action, MoveAction, EatAction, CascadeAction
from .utils import render_board
from datetime import datetime
import heapq
import itertools

def search(
    board: dict[Coord, CellState]
) -> list[Action] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to `CellState` instances (each with a `.color` and
            `.height` attribute).

    Returns:
        A list of actions (MoveAction, EatAction, or CascadeAction), or `None`
        if no solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    search_start_time = datetime.now()

    if check_is_goal(board):
        return []

    found_goal = False

    # for tie-breaking in priority queue using heapq, first added has priority
    counter = itertools.count()

    # create empty priority queue
    # array of tuples: (priority, priority tie-breaker, [actions so far], board)
    pq = []
    heapq.heappush(pq, (0, next(counter), [], board))

    # prevent revisiting states
    visited = set()

    # to count nodes generated and expanded
    nodes_generated = 0
    nodes_expanded = 0

    # continue search
    while (pq and not found_goal):
        # get next path to explore
        cur_state = heapq.heappop(pq)
        switched_key = board_switch_to_key(cur_state[3])

        # if this state has been visited before, skip it
        if switched_key in visited:
            continue
        visited.add(switched_key)

        nodes_expanded += 1

        # stores list(Action)
        try_actions = actions_cando(cur_state[3])

        # test each possible move and insert into priority queue
        for action in try_actions:
            # make move to get board state
            updated_board = actions_result(cur_state[3], action)
            if board_switch_to_key(updated_board) not in visited:
                red_pos = action.coord + action.direction
                priority = f(updated_board, cur_state[2])
                heapq.heappush(pq, (priority, next(counter), cur_state[2] + [action], updated_board))
                found_goal = check_is_goal(updated_board)
                nodes_generated += 1
                if found_goal:
                    solution = cur_state[2] + [action]
                    print(f"Nodes generated: {nodes_generated}")
                    print(f"Nodes expanded: {nodes_expanded}")
                    print(f"Search time: {datetime.now() - search_start_time}")
                    print(f"Solution length: {len(solution)}")
                    return solution
    
    print(f"Nodes generated: {nodes_generated}")
    print(f"Nodes expanded: {nodes_expanded}")
    print(f"Search time: {datetime.now() - search_start_time}")
    
    return None

# changed board dict to a tuple key for visited set
def board_switch_to_key(board: dict[Coord, CellState]):
    save_list = []
    for coords, cells in board.items():
        item = (coords.r, coords.c, cells.color, cells.height)
        save_list.append(item)
    save_list.sort()
    result = tuple(save_list)
    return result
    
# checks given board state for blue stacks, if none then goal is reached
def check_is_goal(board: dict[Coord, CellState])-> bool:
    for cell in board.values():
        if cell.color == PlayerColor.BLUE:
            return False
    return True

# what actions can we do
def actions_cando(board: dict[Coord, CellState]) -> list[Action]:
    react_action = []
    for coords, cells in board.items():
        if cells.color != PlayerColor.RED:
            continue
        for direction_move in Direction:
            try:
                next_step = coords + direction_move
            except ValueError:
                continue
            if next_step is not None:
                if next_step not in board:
                    react_action.append(MoveAction(coords, direction_move))
                elif board[next_step].color == PlayerColor.RED:
                    react_action.append(MoveAction(coords, direction_move))
                elif board[next_step].color == PlayerColor.BLUE:
                    if cells.height >= board[next_step].height:
                        react_action.append(EatAction(coords, direction_move))
                if cells.height >= 2:
                    react_action.append(CascadeAction(coords, direction_move))
                
    return react_action

# what will happen after we did that action
def actions_result(board: dict[Coord, CellState], action: Action) -> dict[Coord, CellState]:
    if isinstance(action, MoveAction):
        return act_move(board, action)
    if isinstance(action, EatAction):
        return act_eat(board, action)
    if isinstance(action, CascadeAction):
        return act_cascade(board, action)
    raise ValueError("dont know which type of move")

# make move to get new board state
def act_move(board: dict[Coord, CellState], actions: MoveAction) -> dict[Coord, CellState]:
    new_board = dict(board)
    start_space = actions.coord
    target_space = start_space + actions.direction
    moving_check = new_board.pop(start_space)
    if target_space in new_board:
        target_stack = new_board[target_space]
        new_board[target_space] = CellState(PlayerColor.RED, target_stack.height + moving_check.height)
    else:
        new_board[target_space] = moving_check
    return new_board

# do eat action to get new board state
def act_eat(board: dict[Coord, CellState], actions: EatAction) -> dict[Coord, CellState]:
    new_board = dict(board)
    start_space = actions.coord
    target_space = start_space + actions.direction
    attack_goal = new_board.pop(start_space)
    new_board.pop(target_space)
    new_board[target_space] = attack_goal
    return new_board

# do cascade action to get new board state
def act_cascade(board: dict[Coord, CellState], actions: CascadeAction) -> dict[Coord, CellState]:
    new_board = dict(board)
    start_space = actions.coord
    action_direct = actions.direction
    cas_attack = new_board.pop(start_space)
    action_height = cas_attack.height
    cas_height = action_height + 1
    for cas_steps in range(1, cas_height):
        try:
            target_space = Coord(start_space.r + action_direct.r * cas_steps, start_space.c + action_direct.c * cas_steps)
        except:
            continue
        if target_space in new_board:
            push_stack_action(new_board, target_space, action_direct)
            new_board[target_space] = CellState(PlayerColor.RED, 1)

    return new_board

# helper function to push stack in cascade action
def push_stack_action(new_board :dict[Coord, CellState], coord: Coord, push_direct: Direction) -> None:
    if coord not in new_board:
        return
    moving_stack = new_board[coord]
    try:
        next_coord_pos = coord + push_direct
    except:
        new_board.pop(coord)
        return
    if next_coord_pos in new_board:
        push_stack_action(new_board, next_coord_pos, push_direct)
    new_board.pop(coord)
    new_board[next_coord_pos] = moving_stack


def g(actions : list[Action]) -> int:
    """
    Calculates total cost so far of path actions.

    Parameters:
        'actions': list of actions taken so far in path.

    Returns:
        integer of total cost of path so far.
    """

    return len(actions)

def distance(red_pos : Coord, blue_pos : Coord) -> int:
    """
    Function for A* search based on position of stacks on board. 
    Checking for move, eat potential.

    Parameters:
        'red_pos': position of red stack on board.
        'blue_pos': position of blue stack on board.

    Returns:
        integer of manhattan distance from blue stack to red stack.
    """

    return abs(red_pos.r - blue_pos.r) + abs(red_pos.c - blue_pos.c)

def test_cascade(red_pos : Coord, blue_pos : Coord, red_height : int) -> int:
    """ 
    Checking for cascade potential.

    Parameters:
        'red_pos': position of red stack on board.
        'blue_pos': position of blue stack on board.
        'red_height': height of red stack on board.
    
    Returns:
        integer of min cost to eliminate blue stack by cascade if possible.
        Otherwise, returns board size.
    """

    # if red stack cannot cascade, return max distance
    if red_height < 2:
        return BOARD_N ** 2
    
    stack_dist_r = blue_pos.r - red_pos.r # positive if red above blue, negative if red below blue
    stack_dist_c = blue_pos.c - red_pos.c # positive if red left of blue, negative if red right of blue
    
    # cost of aligning to same row or col as blue
    align_row = abs(stack_dist_r)
    align_col = abs(stack_dist_c)

    # costs of each direction (d,u,r,l) of cascade to eliminate blue stack
    costs = []
    
    # red above blue, check if cascade down eliminates blue stack
    if stack_dist_r > 0 and red_pos.r + red_height >= BOARD_N - 1:
        costs.append(align_col + 1)

    # red below blue, check if cascade up eliminates blue stack
    if stack_dist_r < 0 and red_pos.r == red_height:
        costs.append(align_col + 1)

    # red left of blue, check if cascade right eliminates blue stack
    if stack_dist_c > 0 and red_pos.c + red_height >= BOARD_N - 1:
        costs.append(align_row + 1)

    # red right of blue, check if cascade left eliminated blue stack
    if stack_dist_c < 0 and red_pos.c == red_height:
        costs.append(align_row + 1)

    if costs:
        return min(costs)
    else:
        return BOARD_N ** 2

def min_to_eliminate_blue(board : dict[Coord, CellState], red_pos : Coord, red_height : int) -> int:
    """
    Checking for move, eat, cascade potential.

    Parameters:
        'board': dictionary representation of board state.
        'red_pos': position of red stack on board.
        'red_height': height of red stack on board.

    Returns:
        integer of total min cost to eliminate each blue stack by move, eat, or cascade if possible.
        Otherwise, returns board size.
    """

    costs = [BOARD_N ** 2]
    for coord, cell in board.items():
        # for each position on board
        if (cell and cell.color == PlayerColor.BLUE):
            # find and update shortest found manhattan distance
            if red_height >= cell.height:
                eat_cost = distance(red_pos, coord)
                costs.append(eat_cost)
            else:
                eat_cost = BOARD_N ** 2
                costs.append(eat_cost)
            
            # test potential for cascade to eliminate blue stack
            cascade_cost = test_cascade(red_pos, coord, red_height)
            costs.append(cascade_cost)

    return min(costs)

def h_board(board : dict[Coord, CellState]) -> int:
    """
    Heuristic function which estimated cost to goal based on position of stacks on board.

    Parameters: 
        'board': a dictionary representing the initial board state, mapping
            coordinates to `CellState` instances (each with a `.color` and
            `.height` attribute).
        'red_pos': position of red stack to be moved.

    Returns:
        integer total of min costs to eliminate each blue stack from each red stack on board.
    """
    
    # for each red, find min cost to eliminate each blue
    mins = []
    for coord, cell in board.items():
        if cell.color == PlayerColor.RED:
            red_height = board.get(coord).height

            mins.append(min_to_eliminate_blue(board, coord, red_height))

    if mins:
        return sum(mins)
    else:
        return BOARD_N ** 2
    
def h_weight(board : dict[Coord, CellState]) -> float:
    """
    Calculates weighting for heuristic function, trusting heuristic more if there are more blue cells.

    Parameters:
        'board': dictionary representing state of the board
    
    Returns:
        weighting such that algorithm is more greedy when there are many blue cells and less greedy when 
        there are fewer than 3 blue cells.
    """
    n_blues = sum(1 for cell in board.values() if cell.color == PlayerColor.BLUE)

    if n_blues <= 0:
        return 0

    # reduce time for complex puzzles
    if n_blues > 3:
        return n_blues / 1.5
    elif n_blues <= 3:
        # more accurate for closer to goal state
        return 1 

def f(board : dict[Coord, CellState], actions : list[Action]) -> int:
    """
    Calculates estimate cost for path, current cost + heuristic cost

    Parameters:
        'board': dictionary representing state of the board
        'actions': list of actions taken so far in path.

    Returns:
        integer of total estimated cost to goal.
    """

    return g(actions) + h_weight(board) * h_board(board)
