"""
Enhanced Shared Memory System for PCB AI

✔ Multi-agent memory
✔ Chat memory (multi-turn)
✔ RAG context
✔ Token-safe context
✔ Debug + trace
"""

from typing import Any, Dict, List
import copy


# ----------------------------------------
# 🧠 MAIN MEMORY CLASS
# ----------------------------------------
class PCBMemory:

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.history: List[Dict] = []        # agent trace
        self.chat_history: List[Dict] = []   # 💬 NEW
        self.rag_context: List[str] = []     # 📚 NEW


    # ----------------------------------------
    # ➕ ADD / UPDATE DATA
    # ----------------------------------------
    def update(self, key: str, value: Any):

        if value is None:
            return

        self.data[key] = value

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
        self.chat_history = []
        self.rag_context = []


    # ----------------------------------------
    # 💬 CHAT MEMORY (NEW)
    # ----------------------------------------
    def add_chat(self, user: str, ai: str):

        self.chat_history.append({
            "user": user,
            "ai": ai
        })


    def get_chat_context(self, last_n=5):

        context = ""

        for h in self.chat_history[-last_n:]:
            context += f"\nUser: {h['user']}\nAI: {h['ai']}"

        return context


    # ----------------------------------------
    # 📚 RAG CONTEXT (NEW)
    # ----------------------------------------
    def add_rag(self, chunks: List[str]):

        if isinstance(chunks, list):
            self.rag_context.extend(chunks)


    def get_rag_context(self, max_chunks=5):

        return "\n".join(self.rag_context[:max_chunks])


    # ----------------------------------------
    # 🧠 FULL CONTEXT (FOR LLM)
    # ----------------------------------------
    def get_context(self, exclude_keys=None):

        exclude_keys = exclude_keys or []

        context_parts = []

        for key, value in self.data.items():

            if key in exclude_keys:
                continue

            context_parts.append(f"{key.upper()}:\n{value}")

        return "\n\n".join(context_parts)


    # ----------------------------------------
    # 🧠 SMART CONTEXT (NEW)
    # ----------------------------------------
    def get_smart_context(self, max_chars=4000):

        context = self.get_context()

        chat = self.get_chat_context()
        rag = self.get_rag_context()

        full = f"""
        MEMORY:
        {context}

        CHAT:
        {chat}

        KNOWLEDGE:
        {rag}
        """

        return full[:max_chars]


    # ----------------------------------------
    # 🧠 LIMITED CONTEXT
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

        base = self.get_context(exclude_keys=["tools", "final"])

        return f"{base}\n\nCURRENT_AGENT: {agent_name.upper()}"


    # ----------------------------------------
    # 📊 SUMMARY
    # ----------------------------------------
    def summary(self):

        return {
            "keys": list(self.data.keys()),
            "num_items": len(self.data),
            "history_steps": len(self.history),
            "chat_turns": len(self.chat_history),
            "rag_chunks": len(self.rag_context)
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
    # 🧠 HISTORY
    # ----------------------------------------
    def get_history(self):

        return self.history


    # ----------------------------------------
    # 🔍 FILTER
    # ----------------------------------------
    def filter(self, keys: List[str]):

        return {k: self.data.get(k) for k in keys if k in self.data}


    # ----------------------------------------
    # 🧪 DEBUG
    # ----------------------------------------
    def debug(self):

        print("🧠 MEMORY STATE")

        for k, v in self.data.items():
            print(f"{k}: {type(v)}")

        print("\n📜 HISTORY:")
        for step in self.history:
            print(step)

        print("\n💬 CHAT:")
        for c in self.chat_history:
            print(c)

        print("\n📚 RAG:")
        print(len(self.rag_context), "chunks")


    # ----------------------------------------
    # 🔁 SAFE COPY
    # ----------------------------------------
    def copy(self):

        new_mem = PCBMemory()
        new_mem.from_dict(self.data)

        new_mem.chat_history = copy.deepcopy(self.chat_history)
        new_mem.rag_context = copy.deepcopy(self.rag_context)

        return new_mem


    # ----------------------------------------
    # 🧠 REPRESENTATION
    # ----------------------------------------
    def __repr__(self):

        return f"""
        PCBMemory(
            keys={list(self.data.keys())},
            steps={len(self.history)},
            chat={len(self.chat_history)},
            rag={len(self.rag_context)}
        )
        """


# ----------------------------------------
# ⚡ QUICK UTILITY
# ----------------------------------------
def create_memory(initial_data: Dict[str, Any] = None):

    memory = PCBMemory()

    if initial_data:
        memory.merge(initial_data)

    return memory
