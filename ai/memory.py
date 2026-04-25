"""
Shared Memory System for Multi-Agent PCB AI

Stores:
- Vision output
- OCR data
- Graph structure
- GNN results
- Agent outputs (power, signal, thermal, layout)
- Tool suggestions

Acts as:
🧠 Central brain for all agents
"""

from typing import Any, Dict
import copy


# ----------------------------------------
# 🧠 MAIN MEMORY CLASS
# ----------------------------------------
class PCBMemory:

    def __init__(self):
        self.data: Dict[str, Any] = {}

    # ----------------------------------------
    # ➕ ADD / UPDATE DATA
    # ----------------------------------------
    def update(self, key: str, value: Any):

        if value is None:
            return

        self.data[key] = value

    # ----------------------------------------
    # 📥 GET VALUE
    # ----------------------------------------
    def get(self, key: str, default=None):

        return self.data.get(key, default)

    # ----------------------------------------
    # 📦 GET FULL MEMORY
    # ----------------------------------------
    def get_all(self) -> Dict[str, Any]:

        return self.data

    # ----------------------------------------
    # 🔄 MERGE DICTIONARY INTO MEMORY
    # ----------------------------------------
    def merge(self, new_data: Dict[str, Any]):

        if not isinstance(new_data, dict):
            return

        for k, v in new_data.items():
            self.data[k] = v

    # ----------------------------------------
    # ❌ REMOVE KEY
    # ----------------------------------------
    def delete(self, key: str):

        if key in self.data:
            del self.data[key]

    # ----------------------------------------
    # 🧹 CLEAR MEMORY
    # ----------------------------------------
    def clear(self):

        self.data = {}

    # ----------------------------------------
    # 🧠 GET CONTEXT (FOR LLM)
    # ----------------------------------------
    def get_context(self) -> str:

        context_str = ""

        for key, value in self.data.items():
            context_str += f"\n--- {key.upper()} ---\n{value}\n"

        return context_str

    # ----------------------------------------
    # 🔍 GET SUMMARY (LIGHTWEIGHT)
    # ----------------------------------------
    def summary(self):

        return {
            "keys": list(self.data.keys()),
            "num_items": len(self.data)
        }

    # ----------------------------------------
    # 📄 SERIALIZE (FOR CACHE / STORAGE)
    # ----------------------------------------
    def to_dict(self):

        return copy.deepcopy(self.data)

    # ----------------------------------------
    # 📥 LOAD FROM DICT
    # ----------------------------------------
    def from_dict(self, data: Dict[str, Any]):

        if isinstance(data, dict):
            self.data = copy.deepcopy(data)

    # ----------------------------------------
    # 🧪 DEBUG PRINT
    # ----------------------------------------
    def debug(self):

        print("🧠 MEMORY STATE")
        for k, v in self.data.items():
            print(f"{k}: {type(v)}")

    # ----------------------------------------
    # 🔁 SAFE COPY
    # ----------------------------------------
    def copy(self):

        new_mem = PCBMemory()
        new_mem.from_dict(self.data)
        return new_mem

    # ----------------------------------------
    # 🧠 REPRESENTATION
    # ----------------------------------------
    def __repr__(self):

        return f"PCBMemory(keys={list(self.data.keys())})"


# ----------------------------------------
# ⚡ QUICK UTILITY
# ----------------------------------------
def create_memory(initial_data: Dict[str, Any] = None):

    memory = PCBMemory()

    if initial_data:
        memory.merge(initial_data)

    return memory
    
