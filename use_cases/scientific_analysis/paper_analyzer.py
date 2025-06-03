from ...utils.data_processors import TextProcessor
from ...utils.citation_handler import CitationHandler

class PaperAnalyzer:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.citation_handler = CitationHandler()

    def extract_methods(self, text):
        # ...existing code or logic for extracting methods...
        pass

    def extract_citations(self, text):
        return self.citation_handler.extract_citations(text)
