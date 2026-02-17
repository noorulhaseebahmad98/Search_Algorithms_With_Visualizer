import heapq
from collections import deque
import math

class Node:
    def __init__(self, state, parent=None, action=None, cost=0, depth=0):
        self.state = state  # (row, col)
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)

def get_successors(state, grid_size):
    """
    Generates successors in specific Clockwise order:
    1. Up
    2. Right
    3. Bottom
    4. Bottom-Right (Diagonal)
    5. Left
    6. Top-Left (Diagonal)
    """
    row, col = state
    rows, cols = grid_size
    actions = [
        ("Up", (-1, 0), 1),
        ("Right", (0, 1), 1),
        ("Bottom", (1, 0), 1),
        ("Bottom-Right", (1, 1), 1.5),
        ("Left", (0, -1), 1),
        ("Top-Left", (-1, -1), 1.5)
    ]

    successors = []
    for action, (dr, dc), cost in actions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < rows and 0 <= new_col < cols:
            successors.append(((new_row, new_col), action, cost))
    
    return successors

def reconstruct_path(node):
    path = []
    current = node
    while current.parent:
        path.append(current.action)
        current = current.parent
    return path[::-1] # Reverse path

def bfs(start, goal, grid_size):
    """Breadth-First Search"""
    start_node = Node(start)
    if start == goal:
        return []
    
    frontier = deque([start_node])
    explored = set()
    
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)

        for state, action, cost in get_successors(node.state, grid_size):
            if state not in explored and state not in [n.state for n in frontier]:
                child = Node(state, node, action, node.cost + cost, node.depth + 1)
                if child.state == goal:
                    return reconstruct_path(child)
                frontier.append(child)
    return None

def dfs(start, goal, grid_size):
    """Depth-First Search - Graph Search version to avoid cycles"""
    start_node = Node(start)
    frontier = [start_node]
    explored = set()

    while frontier:
        node = frontier.pop() # LIFO
        
        if node.state == goal:
            return reconstruct_path(node)

        if node.state not in explored:
            explored.add(node.state)
            neighbors = get_successors(node.state, grid_size)
            for state, action, cost in reversed(neighbors):
                if state not in explored:
                     child = Node(state, node, action, node.cost + cost, node.depth + 1)
                     frontier.append(child)
    return None

def ucs(start, goal, grid_size):
    """Uniform-Cost Search"""
    start_node = Node(start)
    frontier = []
    heapq.heappush(frontier, start_node)
    explored = set()
    
    while frontier:
        node = heapq.heappop(frontier)
        
        if node.state == goal:
            return reconstruct_path(node)
            
        if node.state not in explored:
            explored.add(node.state)
            
            for state, action, cost in get_successors(node.state, grid_size):
                if state not in explored:
                    new_cost = node.cost + cost
                    child = Node(state, node, action, new_cost, node.depth + 1)
                    heapq.heappush(frontier, child)
    return None

def dls(start, goal, grid_size, limit):
    """Depth-Limited Search"""
    return recursive_dls(Node(start), goal, grid_size, limit, set())

def recursive_dls(node, goal, grid_size, limit, path_states):
    if node.state == goal:
        return reconstruct_path(node)
    
    if limit <= 0:
        return "cutoff"
    
    cutoff_occurred = False

    path_states.add(node.state)
    
    for state, action, cost in get_successors(node.state, grid_size):
        
        if state not in path_states: 
            child = Node(state, node, action, node.cost + cost, node.depth + 1)
            result = recursive_dls(child, goal, grid_size, limit - 1, path_states)
            
            if result == "cutoff":
                cutoff_occurred = True
            elif result is not None:
                return result
                
    path_states.remove(node.state) 
    
    if cutoff_occurred:
        return "cutoff"
    return None

def iddfs(start, goal, grid_size, max_depth=1000):
    """Iterative Deepening DFS"""
    for depth in range(max_depth):
        result = dls(start, goal, grid_size, depth)
        if result != "cutoff" and result is not None:
            return result

    return None

def bidirectional_search(start, goal, grid_size):
    """Bidirectional Search using BFS"""
    if start == goal:
        return []
    
    f_frontier = deque([Node(start)])
    f_explored = {start: Node(start)}
    
    b_frontier = deque([Node(goal)])
    b_explored = {goal: Node(goal)}
    
    while f_frontier and b_frontier:
        if f_frontier:
            node = f_frontier.popleft()
            for state, action, cost in get_successors(node.state, grid_size):
                if state not in f_explored:
                    child = Node(state, node, action, node.cost + cost)
                    f_explored[state] = child
                    f_frontier.append(child)
                    if state in b_explored:
                        return merge_paths(child, b_explored[state])
        
        if b_frontier:
            node = b_frontier.popleft()
            for state, action, cost in get_successors(node.state, grid_size):
                if state not in b_explored:
                    
                    child = Node(state, node, action, node.cost + cost) 
                    b_explored[state] = child
                    b_frontier.append(child)
                    if state in f_explored:
                        return merge_paths(f_explored[state], child)
                        
    return None

def merge_paths(f_node, b_node):
    path_forward = reconstruct_path(f_node)
    
    path_backward = []
    curr = b_node
    while curr.parent:
        action =  get_inverse_action(curr.action)
        path_backward.append(action)
        curr = curr.parent
        
    return path_forward + path_backward

def get_inverse_action(action):
    inverses = {
        "Up": "Bottom",
        "Bottom": "Up",
        "Left": "Right",
        "Right": "Left",
        "Top-Left": "Bottom-Right",
        "Bottom-Right": "Top-Left"
    }
    return inverses.get(action, action)


def bfs_step(start, goal, grid_size):
    start_node = Node(start)
    if start == goal:
        yield {'type': 'path', 'path': [], 'explored': set(), 'frontier': []}
        return
    
    frontier = deque([start_node])
    explored = set()
    explored.add(start)
    
    yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': start_node.state}
    
    while frontier:
        node = frontier.popleft()
        yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': node.state}
        
        for state, action, cost in get_successors(node.state, grid_size):
            if state not in explored and state not in [n.state for n in frontier]:
                child = Node(state, node, action, node.cost + cost, node.depth + 1)
                #goal ko check karo generating ka doran!
                if child.state == goal:
                    yield {'type': 'path', 'path': reconstruct_path(child), 'explored': list(explored), 'frontier': [n.state for n in frontier]}
                    return
                
                frontier.append(child)
                explored.add(state) 
    frontier = deque([start_node])
    explored = set()
    
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)
        
        yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': node.state}

        for state, action, cost in get_successors(node.state, grid_size):
            in_frontier = any(n.state == state for n in frontier)
            if state not in explored and not in_frontier:
                child = Node(state, node, action, node.cost + cost, node.depth + 1)
                if child.state == goal:
                    yield {'type': 'path', 'path': reconstruct_path(child), 'explored': list(explored), 'frontier': [n.state for n in frontier]}
                    return
                frontier.append(child)
    yield {'type': 'path', 'path': None, 'explored': list(explored), 'frontier': []}

def dfs_step(start, goal, grid_size):
    start_node = Node(start)
    frontier = [start_node]
    explored = set()

    yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': None}

    while frontier:
        node = frontier.pop()
        
        if node.state == goal:
            yield {'type': 'path', 'path': reconstruct_path(node), 'explored': list(explored), 'frontier': [n.state for n in frontier]}
            return

        if node.state not in explored:
            explored.add(node.state)
            yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': node.state}
            
            neighbors = get_successors(node.state, grid_size)
            for state, action, cost in reversed(neighbors):
                if state not in explored:
                     child = Node(state, node, action, node.cost + cost, node.depth + 1)
                     frontier.append(child)
    yield {'type': 'path', 'path': None, 'explored': list(explored), 'frontier': []}

def ucs_step(start, goal, grid_size):
    start_node = Node(start)
    frontier = []
    heapq.heappush(frontier, start_node)
    explored = set()
    
    yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': None}
    
    while frontier:
        node = heapq.heappop(frontier)
        
        if node.state == goal:
            yield {'type': 'path', 'path': reconstruct_path(node), 'explored': list(explored), 'frontier': [n.state for n in frontier]}
            return
            
        if node.state not in explored:
            explored.add(node.state)
            yield {'type': 'step', 'frontier': [n.state for n in frontier], 'explored': list(explored), 'current': node.state}
            
            for state, action, cost in get_successors(node.state, grid_size):
                if state not in explored:
                    new_cost = node.cost + cost
                    child = Node(state, node, action, new_cost, node.depth + 1)
                    heapq.heappush(frontier, child)
    yield {'type': 'path', 'path': None, 'explored': list(explored), 'frontier': []}

def dls_step(start, goal, grid_size, limit):
    start_node = Node(start)
    path_states = set()
    stack = [(start_node, [start_node.state])]
    
    yield from recursive_dls_step(Node(start), goal, grid_size, limit, set())

def recursive_dls_step(node, goal, grid_size, limit, path_states):
    yield {'type': 'step', 'frontier': [], 'explored': list(path_states), 'current': node.state}
    
    if node.state == goal:
        yield {'type': 'path', 'path': reconstruct_path(node)}
        return True # Signal found
    
    if limit <= 0:
        return False
    
    path_states.add(node.state)
    
    cutoff_occurred = False
    
    neighbors = get_successors(node.state, grid_size)

    for state, action, cost in neighbors:
        if state not in path_states:
            child = Node(state, node, action, node.cost + cost, node.depth + 1)
            gen = recursive_dls_step(child, goal, grid_size, limit - 1, path_states)
            for event in gen:
                yield event
                if event['type'] == 'path':
                    return True
            
    path_states.remove(node.state)
    return False

def iddfs_step(start, goal, grid_size, max_depth=1000):
    for depth in range(max_depth):
        yield {'type': 'log', 'message': f'Starting Depth {depth}'}
        found = False
        gen = dls_step(start, goal, grid_size, depth)
        for event in gen:
            yield event
            if event['type'] == 'path':
                return
    yield {'type': 'path', 'path': None}

def bidirectional_search_step(start, goal, grid_size):
    if start == goal:
        yield {'type': 'path', 'path': []}
        return

    f_frontier = deque([Node(start)])
    f_explored = {start: Node(start)}
    
    b_frontier = deque([Node(goal)])
    b_explored = {goal: Node(goal)}
    
    while f_frontier and b_frontier:
        # Forward
        if f_frontier:
            node = f_frontier.popleft()
            yield {'type': 'step', 'frontier': [n.state for n in f_frontier] + [n.state for n in b_frontier], 
                   'explored': list(f_explored.keys()) + list(b_explored.keys()), 'current': node.state}
            
            for state, action, cost in get_successors(node.state, grid_size):
                if state not in f_explored:
                    child = Node(state, node, action, node.cost + cost)
                    f_explored[state] = child
                    f_frontier.append(child)
                    if state in b_explored:
                        path = merge_paths(child, b_explored[state])
                        yield {'type': 'path', 'path': path}
                        return

        if b_frontier:
            node = b_frontier.popleft()
            yield {'type': 'step', 'frontier': [n.state for n in f_frontier] + [n.state for n in b_frontier], 
                   'explored': list(f_explored.keys()) + list(b_explored.keys()), 'current': node.state}

            for state, action, cost in get_successors(node.state, grid_size):
                if state not in b_explored:
                    child = Node(state, node, action, node.cost + cost)
                    b_explored[state] = child
                    b_frontier.append(child)
                    if state in f_explored:
                        path = merge_paths(f_explored[state], child)
                        yield {'type': 'path', 'path': path}
                        return
    yield {'type': 'path', 'path': None}
