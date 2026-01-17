# ======================================================
# graph/content_graph.py
# ======================================================
class Concept:
    def __init__(self, cid: str, min_elo: float = 0.0):
        self.id = cid
        self.min_elo = min_elo
        self.prerequisites = set()


class ContentGraph:
    def __init__(self):
        self.concepts = {}

    def add_concept(self, concept: Concept):
        self.concepts[concept.id] = concept

    def add_prerequisite(self, concept_id: str, prereq_id: str):
        self.concepts[concept_id].prerequisites.add(prereq_id)

    def available_concepts(self, global_elo: float):
        available = []
        for c in self.concepts.values():
            if global_elo >= c.min_elo:
                available.append(c)
        return available

