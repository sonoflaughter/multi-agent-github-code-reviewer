class VectorStoreMock:
    def __init__(self):
        self.store = {}

    def upsert(self, key: str, vector: list, metadata: dict):
        self.store[key] = {"vector": vector, "meta": metadata}

    def query(self, query_vector: list, top_k: int = 3):
        # naive: return first top_k items
        items = list(self.store.items())[:top_k]
        return [{"id": k, "meta": v["meta"]} for k, v in items]
