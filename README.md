# puzzle-solving-ai
Python weighted A* search algorithm to find near optimal solution for all puzzle scenarios based on a custom board game, 'Cascade'.

## Cascade Board Game Rules
The game uses an 8x8 grid and has variously placed red and blue stacks. Red and Blue players take turns making one of 3 moves with one of their stacks: Move, Eat or Cascade. 
```markdown
- `Move` - The piece moves to an adjacent square in one of four directions: up, left, right, down. If there is another stack of the same color in the target square, the stacks will merge and the total height will be summed.
- `Eat` - If an adjacent square has an opposing color's piece and the stack height is greater than or equal to the stack height of the target enemy piece's stack height, the stack can be eliminated by an 'Eat' action and the stack will be moved where the enemy piece previously was.
- `Cascade` - If the stack height is >= 2, a cascade action is possible any of the up, left, right, down directions. Acts as if the stack is 'falling over' and cells are laid out in direction of Cascade with stack height 1. Any friendly or enemy stacks are pushed by cascade and if pushed off the edge of the board, they are eliminated.
```
```
Cascade example: R3 Stack uses Cascade Right
before:                             after:
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  R3 .  R4 B3 R2 B1             .  .  .  R1 R1 R1 R4 B3
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .              .  .  .  .  .  .  .  .
```
A player wins once all enemy pieces are eliminated. The AI agent plays as Red and Blue pieces are unable to do any actions in this version.

## How It Works
Min-heap is used to store the board state and actions to reach the board state. Every heap pop, the Algorithm checks if the state has been seen before. If not, the algorithm will expand the node and generate a list of possible moves Red can make from the current state. For each of these actions, a new board is generated and pushed into the queue with priority calculated based off current length of path and a heuristic function multiplied by a weighting. The generated board is a goal state if there no blues left on the board. Once goal state is found the list of actions will be returned and printed. If the priority queue is emptied before a goal state is found, it is determined that there is no solution.
The heuristic Function works by summing the minimum costs for each blue stack to be eliminated by either cascading or eating and it is weighted to be more 'greedy' if there are many blue stacks on the board to speed up algorithm in hard cases and weighting allows for more accuracy when it is closer to the goal state as search problem will be less time-consuming. 

## How to Run
Import all files to VS Code or other code editor. Run using terminal in format: "type test_cases/test.csv | python -m search". To parse in CSV file to algorithm. CSV files must have format given:
```
 , , , , , , ,
 B1, , , , , , ,
 R1, , , , , , ,
 , , , , , , ,
 , , , , , , ,
 , , , , , ,R2,
 , , , , , ,  ,
 , , , , , ,B3,
```

## Further Possible Optimisations
The heuristic and weighting could be more fine-tuned to return more optimal solutions and the time to complete puzzles with many blues is significantly still longer than test cases with less blue cells.
