class PositionManager:
    @staticmethod
    def pos_2D(pos, n):
        return pos % n, pos // n

    @staticmethod
    def pos_1D(pos_x, pos_y, n):
        return pos_y * n + pos_x

    @staticmethod
    def get_distance(pos_a, pos_b, n):
        pos_a = PositionManager.pos_2D(pos_a, n)
        pos_b = PositionManager.pos_2D(pos_b, n)
        return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

    @staticmethod
    def get_closers_neighbors(source, target, n, get_neighbors):
        neighbors = get_neighbors(source)
        closers = []
        for neighbor in neighbors:
            if PositionManager.get_distance(neighbor, target, n) < PositionManager.get_distance(source, target, n):
                closers.append(neighbor)
        return closers

    @staticmethod
    def get_closers_among(source, target, n, neighbors):
        closers = []
        dist_min = 1
        for neighbor in neighbors:
            dist = PositionManager.get_distance(neighbor, target, n) - PositionManager.get_distance(source, target, n)
            if dist < dist_min:
                dist_min = dist
                closers = [neighbor]
            elif dist == dist_min:
                closers.append(neighbor)
        return closers

    @staticmethod
    def get_closers_empty(source, n, is_empty):
        closers = []
        dist_min = n * n

        for pos in range(n * n):
            if is_empty(pos):
                dist = PositionManager.get_distance(source, pos, n)
                if dist < dist_min:
                    dist_min = dist
                    closers = [pos]
                elif dist == dist_min:
                    closers.append(pos)
        return closers
