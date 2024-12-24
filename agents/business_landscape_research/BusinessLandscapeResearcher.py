from .graph import get_market_research_graph

class BusinessLandscapeResearcher:
    def __init__(self):
        self.graph = get_market_research_graph()

    def ainvoke(self, **kwargs):
        return self.graph.ainvoke(kwargs)