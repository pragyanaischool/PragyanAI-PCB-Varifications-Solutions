# ai/memory.py

"""
Shared Memory System for Multi-Agent PCB AI

Acts as:
🧠 Central brain for all agents
"""

from typing import Any, Dict, List
import copy


# ----------------------------------------
# 🧠 MAIN MEMORY CLASS
# ----------------------------------------
class PCBMemory:

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.history: List[Dict] = []   # 🧠 reasoning trace


    # ----------------------------------------
    # ➕ ADD / UPDATE DATA
    # ----------------------------------------
    def update(self, key: str, value: Any):

        if value is None:
            return

        self.data[key] = value

        # 🔥 Track history (critical for debugging AI)
        self.history.append({
            "step": len(self.history),
            "key": key,
            "type": type(value).__name__
        })


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
    # 🔄 SAFE MERGE
    # ----------------------------------------
    def merge(self, new_data: Dict[str, Any], overwrite=True):

        if not isinstance(new_data, dict):
            return

        for k, v in new_data.items():

            if not overwrite and k in self.data:
                continue

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
        self.history = []


    # ----------------------------------------
    # 🧠 FULL CONTEXT (FOR LLM)
    # ----------------------------------------
    def get_context(self, exclude_keys=None) -> str:

        exclude_keys = exclude_keys or []

        context_parts = []

        for key, value in self.data.items():

            if key in exclude_keys:
                continue

            context_parts.append(f"{key.upper()}:\n{value}")

        return "\n\n".join(context_parts)


    # ----------------------------------------
    # 🧠 LIMITED CONTEXT (TOKEN SAFE)
    # ----------------------------------------
    def get_limited_context(self, max_chars=4000):

        context = self.get_context()

        if len(context) > max_chars:
            return context[:max_chars]

        return context


    # ----------------------------------------
    # 🎯 AGENT-SPECIFIC CONTEXT
    # ----------------------------------------
    def get_agent_context(self, agent_name: str):

        """
        Give each agent relevant context only
        """

        base = self.get_context(exclude_keys=["tools", "final"])

        agent_specific = f"\n\nCURRENT_AGENT: {agent_name.upper()}"

        return base + agent_specific


    # ----------------------------------------
    # 📊 SUMMARY
    # ----------------------------------------
    def summary(self):

        return {
            "keys": list(self.data.keys()),
            "num_items": len(self.data),
            "history_steps": len(self.history)
        }


    # ----------------------------------------
    # 📄 SERIALIZE
    # ----------------------------------------
    def to_dict(self):

        return copy.deepcopy(self.data)


    # ----------------------------------------
    # 📥 LOAD
    # ----------------------------------------
    def from_dict(self, data: Dict[str, Any]):

        if isinstance(data, dict):
            self.data = copy.deepcopy(data)


    # ----------------------------------------
    # 🧠 HISTORY (VERY IMPORTANT)
    # ----------------------------------------
    def get_history(self):

        return self.history


    # ----------------------------------------
    # 🔍 FILTER KEYS
    # ----------------------------------------
    def filter(self, keys: List[str]):

        return {k: self.data.get(k) for k in keys if k in self.data}


    # ----------------------------------------
    # 🧪 DEBUG PRINT
    # ----------------------------------------
    def debug(self):

        print("🧠 MEMORY STATE")

        for k, v in self.data.items():
            print(f"{k}: {type(v)}")

        print("\n📜 HISTORY:")
        for step in self.history:
            print(step)


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

        return f"PCBMemory(keys={list(self.data.keys())}, steps={len(self.history)})"


# ----------------------------------------
# ⚡ QUICK UTILITY
# ----------------------------------------
def create_memory(initial_data: Dict[str, Any] = None):

    memory = PCBMemory()

    if initial_data:
        memory.merge(initial_data)

    return memory
    
