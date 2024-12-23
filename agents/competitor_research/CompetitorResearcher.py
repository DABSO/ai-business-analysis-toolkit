from .graph import get_competition_research_graph
from tools.browser_manager import BrowserManager

class CompetitionResearcher:
    def __init__(self):
        self.graph = get_competition_research_graph()
    
    async def cleanup(self):
        await BrowserManager.close_browser()
    
    async def ainvoke(self, **kwargs):
        try:
            result = await self.graph.ainvoke(kwargs)
            return result
        finally:
            await self.cleanup()


