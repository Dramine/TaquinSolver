class PositionManager:
    @staticmethod
    def pos_2D(pos, n):
        return pos % n, pos // n

    @staticmethod
    def get_distance(pos_a, pos_b, n):
        pos_a = PositionManager.pos_2D(pos_a, n)
        pos_b = PositionManager.pos_2D(pos_b, n)
        return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

    @staticmethod
    def get_closers(source, target, n, get_neighbors):
        neighbors = get_neighbors(source)
        closers = []
        for neighbor in neighbors:
            if PositionManager.get_distance(neighbor, target, n) < PositionManager.get_distance(source, target, n):
                closers.append(neighbor)
        return closers

    @staticmethod
    def get_farthers(source, target, n, get_neighbors):
        neighbors = get_neighbors(source)
        farthers = []
        for neighbor in neighbors:
            if PositionManager.get_distance(neighbor, target, n) > PositionManager.get_distance(source, target, n):
                farthers.append(neighbor)
        return farthers
