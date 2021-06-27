import random
import time
from heapq import heappop
from heapq import heappush
from threading import Thread
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
        closers = PosMan.get_closers(source, target, n, get_neighbors)
        if closers:
            return random.choice(closers)
        else:
            raise NoPathFoundException

    @staticmethod
    def get_farther(source, target, n, get_neighbors):
        farthers = PosMan.get_closers(source, target, n, get_neighbors)
        if farthers:
            return random.choice(farthers)
        else:
            raise NoPathFoundException

    def move(self, source, target):
        pass

    def run(self):
        while not self.position == self.target:
            time.sleep(0.2)
            if not self.stuck:
                try:
                    self.move(self.position, self.target)
                except NoPathFoundException:
                    self.stuck = True
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

    def dijkstra(self, source, target):
        prev = {}
        graph = set()
        distance = {source: 0}
        to_use = [(0, source)]  # Couples (distance[node], node)

        while to_use:
            dist_node, node = heappop(to_use)
            if node in graph:
                continue

            graph.add(node)

            for neighbor in self.env.get_neighbors(node):
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
        path = self.dijkstra(source, target)
        self.env.next_move(self, path[1])


class Message:
    pass


class GiveWayMessage(Message):
    def __init__(self, move_from):
        self.move_from = move_from

    def __str__(self):
        return "{move_from: %i}" % self.move_from

    def __repr__(self):
        return self.__str__()


class ACKMessage(Message):
    pass


class Messenger:
    def __init__(self, id_):
        self.id = id_
        self.handler = {}
        self.received_messages = {}
        self.sended_messages = {}
        self.handler[ACKMessage] = self.ack_handler

    def receive(self, sender, message):
        self.received_messages[sender] = message

    def handle_messages(self):
        if not self.received_messages:
            return

        for sender, message in list(self.received_messages.items()):
            for msg_type in self.handler:
                if isinstance(message, msg_type):
                    self.handler[msg_type](sender)
                    break

    def send(self, receiver, message):
        receiver.receive(self, message)
        self.sended_messages[receiver] = message

    def ack(self, receiver):
        self.send(receiver, ACKMessage())
        self.received_messages.pop(receiver)

    def ack_handler(self, sender):
        self.sended_messages.pop(sender)
        self.received_messages.pop(sender)


class InteractiveDijkstraAgent(DijkstraAgent, Messenger):
    def __init__(self, id_, position, target, env):
        DijkstraAgent.__init__(self, id_, position, target, env)
        Messenger.__init__(self, id_)
        self.handler[GiveWayMessage] = self.give_way_handler

    def receive(self, sender, message):
        super().receive(sender, message)
        # if self.end:
        #     self.end = False
        #     self.env.threads[self.id] = Thread(target=self.run, args=(), daemon=True)
        #     self.env.threads[self.id].start()

    def run(self):
        while not self.position == self.target:
            time.sleep(0.2)
            if not self.stuck:
                try:
                    self.move(self.position, self.target)
                except NoPathFoundException:
                    self.move_or_send_give_way()
            elif self.received_messages:
                self.handle_messages()
        self.end = True

    def give_way_handler(self, sender):
        message = self.received_messages[sender]
        if self.position != message.move_from:
            self.ack(sender)
            return
        print("%i -> %i : %s" % (sender.id, self.id, str(message)))
        self.ack(sender)
        # has_move = self.move_or_send_give_way(sender.target, self.get_farther)
        # if has_move:
        #     self.ack(sender)

    # def move_or_send_give_way(self, target, find):
    #     def check(p):
    #         if self.env.is_empty(p):
    #             return True
    #         else:
    #             agent = self.env.agents[p]
    #             return agent.id not in self.received_messages
    #
    #     def get_neighbors(p):
    #         return self.env.get_neighbors(p, check)
    #
    #     try:
    #         pos = find(self.position, target, self.env.n, get_neighbors)
    #         if self.env.is_empty(pos):
    #             return self.env.next_move(self, pos)
    #         else:
    #             self.stuck = True
    #             if not self.sended_messages:
    #                 receiver = self.env.agents[pos]
    #                 if isinstance(receiver, Messenger) and receiver not in self.received_messages:
    #                     self.send(receiver, GiveWayMessage(pos))
    #                 return False
    #     except NoPathFoundException:
    #         self.stuck = True
    #         return False

    def move_or_send_give_way(self):
        def get_neighbors(p):
            return self.env.get_neighbors(p, lambda _: True)

        closers = PosMan.get_closers(self.position, self.target, self.env.n, get_neighbors)
        empty_closers = []
        fill_closers = []
        for closer in closers:
            if self.env.is_empty(closer):
                empty_closers.append(closer)
            else:
                fill_closers.append(closer)

        while empty_closers:
            closer_i = random.randint(0, len(empty_closers) - 1)
            closer = empty_closers[closer_i]
            has_move = self.env.next_move(self, closer)
            if has_move:
                return True
            empty_closers.pop(closer_i)

        self.stuck = True
        while fill_closers:
            closer_i = random.randint(0, len(fill_closers)-1)
            closer = fill_closers[closer_i]
            try:
                receiver = self.env.agents[closer]
                if isinstance(receiver, Messenger) and receiver not in self.received_messages:
                    self.send(receiver, GiveWayMessage(closer))
                    return False
            except KeyError:
                pass
            fill_closers.pop(closer_i)

    def give_way(self):
        try:
            closer = self.get_closer(self.position, self.target, self.env.n, self.env.get_neighbors)
            return self.env.next_move(self, closer)
        except NoPathFoundException:
            def get_neighbors(p):
                return self.env.get_neighbors(p, lambda _: True)

            closers = PosMan.get_closers(self.position, self.target, self.env.n, get_neighbors)
            while closers:
                closer_i = random.randint(0, len(closers) - 1)
                closer = closers[closer_i]
                try:
                    receiver = self.env.agents[closer]
                    if isinstance(receiver, Messenger) and receiver not in self.received_messages:
                        self.send(receiver, GiveWayMessage(closer))
                        return False
                except KeyError:
                    pass
                closers.pop(closer_i)
