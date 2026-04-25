"""
Shared Memory for Multi-Agent System
"""

class PCBMemory:

    def __init__(self):
        self.data = {}

    def update(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def get_all(self):
        return self.data

    def __repr__(self):
        return str(self.data)
