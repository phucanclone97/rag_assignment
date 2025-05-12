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
        issues = set()  # Use a set to avoid duplicates
        query_lower = query.lower()

        # Expanded problem dictionary with more keywords and phrases
        common_problems = {
            #Band issues
            "riding up": "band_riding_up",
            "rides up": "band_riding_up",
            "band too loose": "band_riding_up",
            "loose band": "band_riding_up",

            # Strap issues
            "falling": "straps_falling",
            "falls off": "straps_falling",
            "slip": "straps_falling",
            "slips": "straps_falling",
            "slipping": "straps_falling",
            "strap fall": "straps_falling",
            
            "digging": "straps_digging",
            "dig": "straps_digging",
            "cuts in": "straps_digging",
            "painful straps": "straps_digging",
            "strap pain": "straps_digging",
            
            # Cup issues
            "wrinkle": "cup_wrinkling",
            "wrinkling": "cup_wrinkling",
            "wrinkled": "cup_wrinkling",
            "baggy": "cup_wrinkling",
            "gap": "cup_gapping",
            "gapping": "cup_gapping",
            "gaps": "cup_gapping",
            
            "overflow": "quadraboob",
            "spill": "quadraboob",
            "spilling": "quadraboob",
            "bulging": "quadraboob",
            "quad boob": "quadraboob",
            "double breast": "quadraboob",
            
            # Wire issues
            "poke": "wire_poking",
            "poking": "wire_poking",
            "stabbing": "wire_poking",
            "underwire pain": "wire_poking",
            
            # Gore issues
            "doesn't lay flat": "gore_floating",
            "doesn't lie flat": "gore_floating",
            "not flat": "gore_floating",
            "gore floats": "gore_floating",
            "gore doesn't touch": "gore_floating",
            "center gore": "gore_floating"
        }
        
        for keyword, issue in common_problems.items():
            if " " in keyword and keyword in query_lower:
                issues.add(issue) #using add instead of append to avoid duplicates
        
        words = query_lower.split()
        for word in words:
            for keyword, issue in common_problems.items():
                if " " not in keyword and word == keyword:
                    issues.add(issue)

        return list(issues)

    def get_sister_sizes(self, bra_size: str) -> List[str]:
        """Calculate sister sizes (same cup volume with different band sizes)."""
        # Parse the bra size into band and cup
        if not bra_size or not isinstance(bra_size, str):
            return []
        
        # Try to parse sizes like "34D", "36DD", etc.
        i = 0
        while i < len(bra_size) and bra_size[i].isdigit():
            i += 1
        
        if i == 0 or i == len(bra_size):
            return []  # Invalid format
        
        try:
            band = int(bra_size[:i])
            cup = bra_size[i:]
            
            # Cup progression (simplified)
            cup_progression = ['A', 'B', 'C', 'D', 'DD', 'DDD', 'E', 'F', 'FF', 'G']
            
            # Find the cup's position
            if cup not in cup_progression:
                return []  # Unknown cup
            
            cup_index = cup_progression.index(cup)
            
            # Calculate sister sizes
            sister_sizes = []
            
            # One band size smaller, one cup size larger
            if band > 30 and cup_index + 1 < len(cup_progression):
                smaller_band = band - 2
                larger_cup = cup_progression[cup_index + 1]
                sister_sizes.append(f"{smaller_band}{larger_cup}")
            
            # One band size larger, one cup size smaller
            if band < 44 and cup_index > 0:
                larger_band = band + 2
                smaller_cup = cup_progression[cup_index - 1]
                sister_sizes.append(f"{larger_band}{smaller_cup}")
            
            return sister_sizes
            
        except (ValueError, IndexError):
            return []  # Handle any parsing errors

    def get_recommendation(self, query: str) -> Dict:
        try:
            # Bug: No input validation
            if not query.strip():
                raise ValueError("Query cannot be empty")

            # Identify fit issues
            query_measurements = self.extract_measurements(query)
            identified_issues = self.identify_fit_issues(query)
            
            if not query_measurements and not identified_issues:
                raise ValueError("Please provide at least measurements or describe fit issues")

            if not query_measurements:
                logging.warning("Query lacks measurements, recommendation may be less accurate")
            # Try to find best overall match regardless of threshold
            all_matches = []
            for context in self.knowledge_base:
                similarity = self.calculate_fit_similarity(query, context)
                if similarity > self.similarity_threshold:
                    all_matches.append({
                        'context': context,
                        'similarity': similarity
                    })

            # Bug: No handling of no matches
            if all_matches:
                closest_match = max(all_matches, key=lambda x: x['similarity'])
                # Only use if it has at least some minimal similarity
                if closest_match['similarity'] > 0.1:  # Very low threshold for "at least something matches"
                    sister_sizes = self.get_sister_sizes(closest_match['context']['recommendation'])
                    return {
                        "recommendation": closest_match['context']['recommendation'],
                        "confidence": closest_match['similarity'],
                        "reasoning": "Low confidence match. " + closest_match['context']['reasoning'],
                        "fit_tips": closest_match['context']['fit_tips'],
                        "identified_issues": identified_issues,
                        "sister_sizes": sister_sizes
                    }
            if not all_matches:
                return {
                    "recommendation": None,  # Bug: Hardcoded default
                    "confidence": 0.0,
                    "reasoning": "Unable to find exact match. Please measure again.",
                    "fit_tips": "Please provide more detailed measurements (underbust and bust) and any fit issues you're experiencing.",
                    "identified_issues": identified_issues,
                    "sister_sizes": []
                }
            best_match = max(all_matches, key=lambda x: x['similarity'])
            sister_sizes = self.get_sister_sizes(best_match['context']['recommendation'])
            return {
                "recommendation": best_match['context']['recommendation'],
                "confidence": best_match['similarity'],
                "reasoning": best_match['context']['reasoning'],
                "fit_tips": best_match['context']['fit_tips'],
                "identified_issues": identified_issues,
                "sister_sizes": sister_sizes  # Add the sister sizes
            }

        except ValueError as ve:
        # Handle validation errors properly
            logging.warning(f"Validation error: {ve}")
            return {"error": str(ve)}
        except Exception as e:
            # Log unexpected errors with full traceback
            logging.exception(f"Unexpected error in get_recommendation: {e}")
            return {"error": "An unexpected error occurred while processing your request"}
