import random
import time
from heapq import heappop
from heapq import heappush
from utils import PositionManager as PosMan


class NoPathFoundException(Exception):
    pass


class Agent:
    def __init__(self, id_, position, target, env):
        self.id = id_
        self.position = position
        self.target = target
        self.env = env
        self.end = False
        self.stuck = False

    @staticmethod
    def get_closer(source, target, n, get_neighbors):
        closers = PosMan.get_closers_neighbors(source, target, n, get_neighbors)
        if closers:
            return random.choice(closers)
        else:
            raise NoPathFoundException

    @staticmethod
    def get_farther(source, target, n, get_neighbors):
        farthers = PosMan.get_closers_neighbors(source, target, n, get_neighbors)
        if farthers:
            return random.choice(farthers)
        else:
            raise NoPathFoundException

    def move(self, source, target):
        pass

    def run(self):
        while not self.end:
            time.sleep(0.2)
            if not self.stuck:
                try:
                    self.move(self.position, self.target)
                except NoPathFoundException:
                    self.stuck = True
            if self.position == self.target:
                self.end = True

    def __str__(self):
        return str(self.id)


class SimpleAgent(Agent):
    def __init__(self, id_, position, target, env):
        super().__init__(id_, position, target, env)

    def move(self, source, target):
        closer = self.get_closer(self.position, self.target, self.env.n, self.env.get_neighbors)
        self.env.next_move(self, closer)


class DijkstraAgent(Agent):
    def __init__(self, id_, position, target, env):
        super().__init__(id_, position, target, env)

    @staticmethod
    def dijkstra(source, target, get_neighbors):
        prev = {}
        graph = set()
        distance = {source: 0}
        to_use = [(0, source)]  # Couples (distance[node], node)

        while to_use:
            dist_node, node = heappop(to_use)
            if node in graph:
                continue

            graph.add(node)

            for neighbor in get_neighbors(node):
                if neighbor in graph:
                    continue
                dist_neighbor = dist_node + 1
                if neighbor not in distance or distance[neighbor] > dist_neighbor:
                    distance[neighbor] = dist_neighbor
                    heappush(to_use, (dist_neighbor, neighbor))
                    prev[neighbor] = node

        path = [target]
        node = target
        while node != source:
            if node in prev:
                node = prev[node]
            else:
                raise NoPathFoundException
            path.insert(0, node)

        return path

    def move(self, source, target):
        path = self.dijkstra(source, target, self.env.get_neighbors)
        self.env.next_move(self, path[1])


class Message:
    def __init__(self, priority):
        self.priority = priority


class ACKMessage(Message):
    pass


class GiveWayMessage(Message):
    def __init__(self, chain, priority):
        super().__init__(priority)
        self.chain = chain

    def __str__(self):
        return "{chain: %a with priority: %i}" % (self.chain, self.priority)

    def __repr__(self):
        return self.__str__()


class LetsTurnMessage(Message):
    pass


class Messenger:
    def __init__(self, id_):
        self.id = id_
        self.handler = {}
        self.received_messages = {}
        self.handler[ACKMessage] = self.ack_handler

    def receive(self, sender, message):
        if sender in self.received_messages:
            old_message = self.received_messages[sender]
            if old_message.priority > message.priority:
                self.received_messages[sender] = message
        else:
            self.received_messages[sender] = message

    def handle_messages(self):
        if not self.received_messages:
            return

        for sender, message in list(self.received_messages.items()):
            for msg_type in self.handler:
                if isinstance(message, msg_type):
                    self.handler[msg_type](sender)

    def send(self, receiver, message):
        receiver.receive(self, message)

    def ack(self, receiver):
        self.send(receiver, ACKMessage(self.id))
        self.received_messages.pop(receiver)

    def ack_handler(self, sender):
        self.received_messages.pop(sender)


class Actuator:
    def __init__(self, agent):
        self.agent = agent
        self.can_end = False

    def do(self, source, target):
        pass


class DirectWayActuator(Actuator):
    def __init__(self, agent):
        super().__init__(agent)
        self.can_end = False

    def do(self, source, target):
        if source == target:
            self.can_end = True
            return True
        return self.agent.move_or_send_give_way(source, target, self.agent.id)


class N2Actuator(Actuator):
    def __init__(self, agent, target_bis):
        super().__init__(agent)
        self.target_bis = target_bis

    def do(self, source, target):
        if source == self.target_bis:
            self.can_end = True
            return True
        return self.agent.move_or_send_give_way(source, self.target_bis, self.agent.id)


class N1Actuator(N2Actuator):
    def __init__(self, agent, target_bis, master_id):
        super().__init__(agent, target_bis)
        self.master_id = master_id

    def do(self, source, target):
        if source == target:
            self.can_end = True
            return True
        if source == self.target_bis:
            return self.agent.move_or_send_lets_turn(target)
        return self.agent.move_or_send_give_way(source, self.target_bis, self.master_id)


class InteractiveAgent(DijkstraAgent, Messenger):
    def __init__(self, id_, position, target, env):
        DijkstraAgent.__init__(self, id_, position, target, env)
        Messenger.__init__(self, id_)
        self.handler[GiveWayMessage] = self.give_way_handler
        self.handler[LetsTurnMessage] = self.lets_turn_handler
        self.waiting = False
        self.next = 1
        self.actuator = self.create_actuator()

    def create_actuator(self):
        n = self.env.n
        target_2d = PosMan.pos_2D(self.id, n)
        if (target_2d[0] < n - 2 and target_2d[1] < n - 2) or (target_2d[0] == n-1 and target_2d[1] == n - 2):
            return DirectWayActuator(self)
        elif target_2d[0] >= n - 2 > target_2d[1]:
            if target_2d[0] == n - 2:
                target_bis = PosMan.pos_1D(n - 1, (self.id // n), n)
                return N2Actuator(self, target_bis)
            elif target_2d[0] == n - 1:
                target_bis = PosMan.pos_1D(n - 1, (self.id // n) + 1, n)
                return N1Actuator(self, target_bis, self.id - 1)
        elif target_2d[1] >= n - 2:
            if target_2d[1] == n - 2:
                self.next = n
                target_bis = PosMan.pos_1D((self.id % n), n - 1, n)
                return N2Actuator(self, target_bis)
            elif target_2d[1] == n - 1:
                self.next = -n + 1
                target_bis = PosMan.pos_1D((self.id % n) + 1, n - 1, n)
                return N1Actuator(self, target_bis, self.id - n)

    def receive(self, sender, message):
        super().receive(sender, message)

    def send(self, receiver, message):
        if isinstance(message, GiveWayMessage):
            self.waiting = True
        super().send(receiver, message)

    def move(self, source, target):
        did = self.actuator.do(source, target)
        if not did:
            raise NoPathFoundException

    def run(self):
        while True:
            if self.received_messages:
                self.handle_messages()
            elif (not (self.stuck or self.waiting or self.end)) and self.env.activeAgent == self.id:
                try:
                    self.move(self.position, self.target)
                except NoPathFoundException:
                    self.stuck = True
            if self.actuator.can_end:
                if self.position == self.target:
                    self.end = True
                    self.stuck = False
                if self.env.activeAgent == self.id and not self.waiting:
                    self.env.activeAgent += self.next

    def ack_handler(self, sender):
        super().ack_handler(sender)
        self.waiting = False
        self.stuck = False

    def give_way_handler(self, sender):
        if self.waiting:
            return

        message = self.received_messages[sender]
        if self.position != message.chain[0] or len(message.chain) < 2:
            self.ack(sender)
            return

        pos = message.chain[1]
        if self.env.is_empty(pos):
            self.env.next_move(self, pos)
            self.ack(sender)
        else:
            try:
                receiver = self.env.agents[pos]
                path = message.chain[1:]
                self.send(receiver, GiveWayMessage(path, message.priority))
            except KeyError:
                pass

    def lets_turn_handler(self, sender):
        if self.waiting:
            return

        def empty_handler(pos):
            return self.env.next_move(self, pos)

        def fill_handler(pos):
            try:
                receiver = self.env.agents[pos]
                if isinstance(receiver, Messenger) and receiver not in self.received_messages \
                        and receiver.id > self.id:
                    return self.send_give_way(receiver, self.id)
            except KeyError:
                pass
            return False

        closers = PosMan.get_closers_neighbors(self.position, self.target, self.env.n, self.env.get_all_neighbors)
        old_pos = self.position
        self.do_for_empty_or_then_fill(closers, empty_handler, fill_handler)
        if old_pos != self.position:
            self.ack(sender)

    def send_give_way(self, receiver, priority):
        def is_servant(pos):
            if pos in self.env.agents:
                agent = self.env.agents[pos]
                return isinstance(agent, Messenger) and agent not in self.received_messages \
                       and agent.id > priority and agent.id != self.id
            else:
                return True

        def get_neighbors(pos):
            return self.env.get_neighbors(pos, is_servant)

        closers_empty = PosMan.get_closers_empty(receiver.position, self.env.n, self.env.is_empty)
        closer_empty = random.choice(closers_empty)
        try:
            path = self.dijkstra(receiver.position, closer_empty, get_neighbors)
            self.send(receiver, GiveWayMessage(path, priority))
            return True
        except NoPathFoundException:
            return False

    def move_or_send_lets_turn(self, target):
        if self.env.is_empty(target):
            self.env.next_move(self, target)
            return True

        try:
            receiver = self.env.agents[self.target]
            if isinstance(receiver, Messenger) and receiver not in self.received_messages:
                self.send(receiver, LetsTurnMessage(self.id))
                return True
        except KeyError:
            pass
        return False

    def do_for_empty_or_then_fill(self, positions, empty_handler, fill_handler):
        empty_positions = []
        fill_positions = []
        for pos in positions:
            if self.env.is_empty(pos):
                empty_positions.append(pos)
            else:
                fill_positions.append(pos)

        while empty_positions:
            i = random.randint(0, len(empty_positions) - 1)
            pos = empty_positions[i]
            if empty_handler(pos):
                return True
            empty_positions.pop(i)

        while fill_positions:
            i = random.randint(0, len(fill_positions) - 1)
            pos = fill_positions[i]
            if fill_handler(pos):
                return True
            fill_positions.pop(i)
        return False

    def move_or_send_give_way(self, source, target, priority):
        def empty_handler(pos):
            return self.env.next_move(self, pos)

        def fill_handler(pos):
            try:
                receiver = self.env.agents[pos]
                if isinstance(receiver, Messenger) and receiver not in self.received_messages \
                        and receiver.id > priority and receiver.id != self.id:
                    return self.send_give_way(receiver, priority)
            except KeyError:
                pass
            return False

        closers = PosMan.get_closers_neighbors(source, target, self.env.n, self.env.get_all_neighbors)
        return self.do_for_empty_or_then_fill(closers, empty_handler, fill_handler)
