from threading import Lock, Thread
import random
import time

class Environment:
    def __init__(self, n):
        self.grid_size = n * n
        self.n = n
        self.agents = {}
        self.mutex_grid = []
        self.threads = []
        self.update = False
        self.activeAgent = 0
        self.screen_updated = False
        for _ in range(self.grid_size):
            self.mutex_grid.append(Lock())

    def add_agent(self, agent):
        self.agents[agent.position] = agent
        self.threads.append(Thread(target=agent.run, args=(), daemon=True, name="Agent-%i" % agent.id))

    def get_neighbors(self, pos, check=None):
        if check is None:
            check = self.is_empty

        neighbors = []
        if pos // self.n > 0 and check(pos - self.n):
            neighbors.append(pos - self.n)  # Nord
        if pos % self.n < self.n - 1 and check(pos + 1):  # Est
            neighbors.append(pos + 1)
        if pos // self.n < self.n - 1 and check(pos + self.n):  # Sud
            neighbors.append(pos + self.n)
        if pos % self.n > 0 and check(pos - 1):  # Ouest
            neighbors.append(pos - 1)
        return neighbors

    def get_all_neighbors(self, pos):
        return self.get_neighbors(pos, lambda _: True)

    def is_empty(self, pos):
        for p in list(self.agents.keys()):
            if p == pos:
                return False
        return True

    def next_move(self, agent, pos):
        while not self.screen_updated:
            time.sleep(0.1)
        self.mutex_grid[pos].acquire()
        has_move = False
        try:
            if self.is_empty(pos):
                self.agents.pop(agent.position)
                agent.position = pos
                self.agents[agent.position] = agent
                has_move = True
        finally:
            self.screen_updated = False
            self.mutex_grid[pos].release()
        if has_move:
            self.update = True
            for agent in list(self.agents.values()):
                agent.stuck = False

        return has_move

    def start_agent(self):
        for thread in self.threads:
            thread.start()

    def generate_random_position(self):
        empty_grid = list(filter(self.is_empty, range(self.grid_size)))
        return random.choice(empty_grid)

    def is_finish(self):
        for agent in list(self.agents.values()):
            if not (agent.end or agent.stuck):
                return False
        return True

    def __str__(self):
        str_ = ""
        for i in range(self.n):
            str_ += "#  "
        for i in range(self.grid_size):
            if i % self.n == 0:
                str_ += "\n"
            if self.is_empty(i):
                str_ += "__ "
            else:
                if self.agents[i].id < 10:
                    str_ += " "
                str_ += str(self.agents[i].id) + " "
        str_ += "\n"
        for i in range(self.n):
            str_ += "#  "

        return str_

    def __repr__(self):
        return str(self)
