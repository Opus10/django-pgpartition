RANGE = "RANGE"


class Partition:
    def __init__(self, *, method, key):
        self.method = method
        assert self.method in [RANGE]
        self.key = [key] if not isinstance(key, (list, tuple)) else key

    def deconstruct(self):
        return "pgpartition.Partition", [], {"method": self.method, "key": self.key}
