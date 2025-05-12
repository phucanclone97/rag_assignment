import json
from typing import Dict, List
import logging
class BraFittingRAG:
    def __init__(self):
        self.load_knowledge_base()
        # Bug: Incorrect similarity threshold
        self.similarity_threshold = 0.3

    def load_knowledge_base(self):
        try:
            with open('app/data/bra_fitting_data.json', 'r') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"Knowledge base file not found at 'app/data/bra_fitting_data.json'. Error: {e}", exc_info=True)
            raise ValueError(f"Knowledge base file not found: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in knowledge base file: {e}", exc_info=True)
            raise ValueError(f"Invalid JSON in knowledge base file: {e}")

    def extract_measurements(self, text: str) -> Dict[str, int]:
        """Extract measurements from text with context awareness."""
        measurements = {}
        words = text.split()
        
        # Look for numeric values and their context
        for i, word in enumerate(words):
            if word.isdigit():
                num = int(word)
            # Check surrounding context (up to 3 words before/after)
                context_range = 3
                start_idx = max(0, i - context_range)
                end_idx = min(len(words), i + context_range + 1)
                context_words = ' '.join(words[start_idx:end_idx]).lower()
                
                # Check for measurement type indicators
                if any(term in context_words for term in ['underbust', 'under bust', 'band']):
                    measurements['underbust'] = num
                elif any(term in context_words for term in ['overbust', 'over bust', 'bust', 'cup']):
                    measurements['overbust'] = num
                
                # Handle units (convert if necessary)
                # This is a simplistic approach; more robust parsing might need regex
                if i + 1 < len(words) and words[i + 1].lower() in ['cm', 'centimeter', 'centimeters']:
                    # Convert cm to inches (rough approximation)
                    if 'underbust' in measurements and measurements['underbust'] == num:
                        measurements['underbust'] = int(num / 2.54)
                    elif 'overbust' in measurements and measurements['overbust'] == num:
                        measurements['overbust'] = int(num / 2.54)
    
        return measurements

    def calculate_fit_similarity(self, query: str, context: Dict) -> float:
        # Bug: Oversimplified similarity calculation
        query_lower = query.lower()
        description_lower = context['description'].lower()
        
        query_words = set(query_lower.split())
        description_words = set(description_lower.split())
        
        text_similarity = 0.0
        # Calculate Jaccard similarity
        if not query_words or not description_words:
            text_similarity = 0.0
        else:
            intersection = query_words.intersection(description_words)
            union = query_words.union(description_words)
            text_similarity = len(intersection) / len(union) if union else 0.0

        query_measurements = self.extract_measurements(query_lower)
        context_measurements = self.extract_measurements(description_lower)
        # Bug: Poor similarity logic
        numeric_similarity = 0.0
        if query_measurements and context_measurements:
        # Check underbust similarity
            if 'underbust' in query_measurements and 'underbust' in context_measurements:
                underbust_diff = abs(query_measurements['underbust'] - context_measurements['underbust'])
                # Scale: 0 difference = 1.0, 2+ inches difference = 0.0
                underbust_score = max(0.0, 1.0 - (underbust_diff / 2.0))
                numeric_similarity += underbust_score
                
            # Check overbust/bust similarity
            if 'overbust' in query_measurements and 'overbust' in context_measurements:
                overbust_diff = abs(query_measurements['overbust'] - context_measurements['overbust'])
                # Scale: 0 difference = 1.0, 3+ inches difference = 0.0
                overbust_score = max(0.0, 1.0 - (overbust_diff / 3.0))
                numeric_similarity += overbust_score
                
            # Average the scores if we have both measurements
            measurement_count = ('underbust' in query_measurements and 'underbust' in context_measurements) + \
                            ('overbust' in query_measurements and 'overbust' in context_measurements)
            numeric_similarity = numeric_similarity / measurement_count if measurement_count > 0 else 0.0

        text_weight = 0.4
        numeric_weight = 0.6
        
        if not query_measurements or not context_measurements:
            text_weight = 0.8
            numeric_weight = 0.2
        
        total_similarity = (text_weight * text_similarity) + (numeric_weight * numeric_similarity)
        return total_similarity

    def identify_fit_issues(self, query: str) -> List[str]:
        # Bug: Missing comprehensive issue detection
        issues = []
        common_problems = {
            "riding up": "band_riding_up",
            "falling": "straps_falling",
            "digging": "straps_digging",
            "wrinkle": "cup_wrinkling",
            "overflow": "quadraboob"
        }
        
        for keyword, issue in common_problems.items():
            if keyword in query.lower():
                issues.append(issue)
        
        return issues

    def get_recommendation(self, query: str) -> Dict:
        try:
            # Bug: No input validation
            if not query.strip():
                raise ValueError("Empty query")

            # Identify fit issues
            identified_issues = self.identify_fit_issues(query)
            
            # Find relevant contexts
            relevant_fits = []
            for context in self.knowledge_base:
                similarity = self.calculate_fit_similarity(query, context)
                if similarity > self.similarity_threshold:
                    relevant_fits.append({
                        'context': context,
                        'similarity': similarity
                    })

            # Bug: No handling of no matches
            if not relevant_fits:
                return {
                    "recommendation": "34B",  # Bug: Hardcoded default
                    "confidence": 0.3,
                    "reasoning": "Unable to find exact match. Please measure again.",
                    "fit_tips": "Please consult our measurement guide."
                }

            # Bug: Oversimplified recommendation selection
            best_match = max(relevant_fits, key=lambda x: x['similarity'])
            
            return {
                "recommendation": best_match['context']['recommendation'],
                "confidence": best_match['similarity'],
                "reasoning": best_match['context']['reasoning'],
                "fit_tips": best_match['context']['fit_tips'],
                "identified_issues": identified_issues
            }

        except Exception as e:
            # Bug: Generic error handling
            return {"error": str(e)}
