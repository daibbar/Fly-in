*This project has been created as part of the 42 curriculum by mdaibbar*

# Description
Autonomous drones are the future of transportation. They are already used in many industries, such as agriculture, construction, and logistics. They are also used in military operations, such as surveillance and reconnaissance.

The task is to design a system that efficiently routes a fleet of drones from a central base (start) to a target location (end), while navigating this dynamic network under a set of strict constraints and optimization goals.

The given input is a graph representing the network of zones, and a set of constraints we must respect. The graph is represented as a network of connected zones, where connections define possible movement paths between zones.

# Instructions
This project includes a `Makefile` to automate execution and testing. 

To run the project, use the following commands:
* `make install`: Installs any necessary dependencies.
* `make run`: Executes the main simulation script (e.g., `python3 main.py maps/easy/01_linear_path.txt`).
* `make lint`: Runs strict type-checking and styling via `flake8` and `mypy` to ensure type safety.
* `make debug`: Runs the main script in debug mode.
* `make clean`: Removes temporary cache files like `__pycache__` and `.mypy_cache`.

# Resources
* The foundational overview in Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks: https://arxiv.org/pdf/1906.08291
* The video serie of Thomas Nobes about the classical defenition of MAPF: https://tinyurl.com/yc7sscx2
* The standard reference of Cooperative A* By David Silver in 2005: https://tinyurl.com/4s7m3kus
* A* algorithm explanation by Dr Mike Pound: https://tinyurl.com/57z47vrx
* Dijikstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* Graph Data Structure Introduction and Problems: https://www.geeksforgeeks.org/dsa/graph-data-structure/

    ## AI-usage
    AI was used in this project as a tool of search about the domain and the standard references, also he was very helpful in how to implement the algorithm.
    it was also helpful in explaining what is P and NP problem, and the difference between NP-hard and NP-complete.
    you can check this conversation here:
    * https://share.gemini.google/TxCeiwhZrSwB

# Algorithm Choices And Implementation Strategy
I used this section from the subject as a principle to decide what algorithm to choose and how to choose it.

**Brief:** Don't waste time rebuilding existing, well-tested solutions when you're trying to solve actual problems—use what already works, but feel free to build things from scratch if your main goal is practice and deep learning. It boils down to choosing the right tool for your goal:
* For efficiency & results: Rely on existing tools (don't reinvent the wheel).
* For learning & growth: Build it yourself to understand how it works under the hood.

As a result, MAPF is a relatively new domain of search, and many researchers have attributed over the last decades many exceptional algorithms and approaches varying in their complexity and use-cases. Because the problem of MAPF is an NP-Hard problem in optimization and NP-complete in feasibility, there is no one single best approach for every single use case.

From all of those, I chose to use the very foundational one which is Cooperative A* by David Silver (Prioritized Planning). Because of the principle "For learning & growth: Build it yourself to understand how it works under the hood" and the fact that many other advanced algorithms are built on it, I chose it as the best choice for this project. It happens that it validates all the test cases available, including beating the 45-turn reference record on the Challenger map. This implementation makes me very ready for any use-case of MAPF in the future.

# Visual Representation Features
To enhance the user experience and provide clear tracking of the drone fleet, this simulation utilizes dynamic terminal coloring. The parser extracts the optional `color` metadata from the input map and maps it directly to ANSI escape codes. 

When the simulation runs, the terminal output prints the zones and drone paths in their designated colors. This provides immediate visual feedback regarding the state of the network, helping the user easily distinguish between `normal`, `restricted`, `priority`, and `blocked` zones at a glance without needing a heavy graphical user interface.

# Example Input and Expected Output
**Example Input (Map File):**
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
connection: start-roof1
connection: start-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

**Expected Output:**
```text
$ make run MAP=path/to/map.txt
D1-corridorA
D1-tunnelB D2-corridorA
D1-goal D2-tunnelB
D2-goal
4
```

Each line is one simulation turn (space-separated drone movements), and the
final line is the total number of turns taken to deliver every drone.