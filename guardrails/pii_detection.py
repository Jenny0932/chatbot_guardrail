from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from typing import List

class PIIDetector:
    def __init__(self):
        """
        Initialize the PII Detector with Presidio Analyzer and Anonymizer engines.
        """
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def detect_pii(self, text: str, entities: List[str] = None, language: str = 'en') -> List[str]:
        """
        Detect specific PII entities in the input text.

        :param text: The text to analyze.
        :param entities: A list of entity types to detect (e.g., ["PERSON", "PHONE_NUMBER"]).
                         If None, all entities will be detected.
        :param language: The language of the text (default is 'en').
        :return: A list of detected PII entity types.
        """
        analysis_results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=entities
        )
        return [result.entity_type for result in analysis_results]

    def analyze_text(self, text, language='en'):
        """
        Analyze the input text for PII entities.

        :param text: The text to analyze.
        :param language: The language of the text (default is 'en').
        :return: A list of detected PII entities.
        """
        return self.analyzer.analyze(text=text, language=language)

    def anonymize_text(self, text, analysis_results):
        """
        Anonymize the detected PII entities in the text.

        :param text: The original text.
        :param analysis_results: The results from the analyze_text method.
        :return: The anonymized text.
        """
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analysis_results
        )
        return anonymized_result.text

# Example usage
if __name__ == "__main__":
    detector = PIIDetector()
    
    text = "Can you tell me what orders I've placed in the last 3 months? My name is Hank Tate and my phone number is 555-123-4567."
    
    # Detect specific PII entities
    detected_pii = detector.detect_pii(text, entities=["PERSON", "PHONE_NUMBER"])
    print("Detected PII Entities:", detected_pii)
    
    # Analyze the text for PII
    analysis_results = detector.analyze_text(text)
    print("Analysis Results:", analysis_results)
    
    # Anonymize the text
    anonymized_text = detector.anonymize_text(text, analysis_results)
    print("Anonymized Text:", anonymized_text)