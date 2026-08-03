import prq


graph = {
    'A' : {'B': 4, 'C': 5},
    'B': {'C': 5, 'A': 4, 'D': 9, 'E': 7},
    'C': {'A': 5, 'B': 11, 'E': 3},
    'D':{},
    'E':{},
    'F':{}
}

class Djikstra:
    pass