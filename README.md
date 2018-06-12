# GraphPlan (Automated planning)
Implementation of Graph Planning algorithm in Python.

Program reads the initial state, goal and each action consisting of the pre-condition and effect as the format in [pddl.txt](https://github.com/ragarwa7/GraphPlan/blob/master/README.md) as input and prints the actions and states at each level until it reaches the goal and returns the solution plan as a set of actions.


Input

Intial state, goals and actions in the pddl format.

Output:

1. Prints all of the corresponding mutexes(IS, CN, I, NL, IE) at each level.
2. All layers of states and actions.
3. Solution path
