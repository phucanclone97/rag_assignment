import json
from typing import Dict, List
import logging
class BraFittingRAG:
    def __init__(self):
        self.load_knowledge_base()
        # Bug: Incorrect similarity threshold
        self.similarity_threshold = 0.2

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
        measurements = {}
        # Pre-process text slightly: remove common noise like 'inch', '-', ','
        processed_text = text.replace('inch', '').replace('-', ' ').replace(',', ' ')
        words = processed_text.split()
        
        nums_found = []
        for i, word in enumerate(words):
            # Try cleaning the word further before checking if it's a digit
            cleaned_word = ''.join(filter(str.isdigit, word))
            if cleaned_word.isdigit():
                num = int(cleaned_word)
                nums_found.append({'value': num, 'index': i})
                
                context_range = 3
                start_idx = max(0, i - context_range)
                end_idx = min(len(words), i + context_range + 1)
                context_words = ' '.join(words[start_idx:end_idx]).lower()
                
                if any(term in context_words for term in ['underbust', 'under bust', 'band']):
                    measurements['underbust'] = num
                elif any(term in context_words for term in ['overbust', 'over bust', 'bust', 'cup']):
                    measurements['overbust'] = num

        # Fallback: If two numbers found and not assigned, assume smaller is underbust
        if len(nums_found) == 2 and ('underbust' not in measurements or 'overbust' not in measurements):
             sorted_nums = sorted(nums_found, key=lambda x: x['value'])
             if 'underbust' not in measurements:
                 measurements['underbust'] = sorted_nums[0]['value']
             if 'overbust' not in measurements:
                 measurements['overbust'] = sorted_nums[1]['value']
        
        # Ensure consistency if only one assigned
        elif len(nums_found) >= 1 and len(measurements) == 1:
            assigned_key = next(iter(measurements))
            assigned_val = measurements[assigned_key]
            unassigned_nums = [n['value'] for n in nums_found if n['value'] != assigned_val]
            if len(unassigned_nums) == 1:
                unassigned_val = unassigned_nums[0]
                if assigned_key == 'underbust' and 'overbust' not in measurements:
                    measurements['overbust'] = unassigned_val
                elif assigned_key == 'overbust' and 'underbust' not in measurements:
                     measurements['underbust'] = unassigned_val

        return measurements

    def calculate_fit_similarity(self, query: str, context: Dict) -> float:
        """Calculate similarity based primarily on measurement matching."""
        # Extract measurements from query and context
        query_measurements = self.extract_measurements(query.lower())
        context_desc = context['description'].lower()
        context_measurements = self.extract_measurements(context_desc)
        
        # Debug print to see what's being extracted
        print(f"Query: {query}")
        print(f"Extracted measurements: {query_measurements}")
        print(f"Context measurements: {context_measurements}")
        
        # If no measurements in either query or context, return low similarity
        if not query_measurements or not context_measurements:
            return 0.1
        
        # Calculate measurement similarity
        similarity = 0.0
        measurement_count = 0
        
        # Check underbust match
        if 'underbust' in query_measurements and 'underbust' in context_measurements:
            underbust_diff = abs(query_measurements['underbust'] - context_measurements['underbust'])
            if underbust_diff == 0:
                similarity += 1.0
            elif underbust_diff <= 1:
                similarity += 0.8
            elif underbust_diff <= 2:
                similarity += 0.5
            else:
                similarity += 0.0
            measurement_count += 1
        
        # Check overbust/bust match
        if 'overbust' in query_measurements and 'overbust' in context_measurements:
            overbust_diff = abs(query_measurements['overbust'] - context_measurements['overbust'])
            if overbust_diff == 0:
                similarity += 1.0
            elif overbust_diff <= 1:
                similarity += 0.8
            elif overbust_diff <= 2:
                similarity += 0.5
            else:
                similarity += 0.0
            measurement_count += 1
        
        # Add similarity for issue matching
        query_issues = self.identify_fit_issues(query)
        context_issues = context.get('common_issues', [])
        
        issue_similarity = 0.0
        if query_issues and context_issues:
            matching_issues = set(query_issues).intersection(set(context_issues))
            if matching_issues:
                issue_similarity = len(matching_issues) / max(len(query_issues), len(context_issues))
        
        # Final similarity is average of measurement similarity + boost for matching issues
        final_similarity = 0.0
        if measurement_count > 0:
            measurement_similarity = similarity / measurement_count
            final_similarity = 0.7 * measurement_similarity + 0.3 * issue_similarity
            
            # Boost exact matches significantly
            if measurement_count == 2 and similarity == 2.0:  # Both measurements match exactly
                final_similarity = max(final_similarity, 0.9)  # Ensure very high similarity
        
        print(f"Final similarity: {final_similarity}")
        return final_similarity

    def identify_fit_issues(self, query: str) -> List[str]:
        issues = set() 
        query_lower = query.lower()
        common_problems = { # Keeping the expanded list from previous suggestions
            # Band issues
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
            "quadraboob effect": "quadraboob", # More specific
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
        # Use simple substring check
        for keyword, issue in common_problems.items():
            if keyword in query_lower:
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
            logging.info(f"Received query: {query}") # Log query
            if not query.strip():
                raise ValueError("Query cannot be empty")

            query_measurements = self.extract_measurements(query)
            identified_issues = self.identify_fit_issues(query)
            logging.info(f"Extracted measurements: {query_measurements}")
            logging.info(f"Identified issues: {identified_issues}")

            if not query_measurements and not identified_issues:
                raise ValueError("Please provide at least measurements or describe fit issues")

            if not query_measurements:
                logging.warning("Query lacks measurements, recommendation may be less accurate")

            all_scored_items = []
            logging.info(f"Comparing against {len(self.knowledge_base)} KB items.")
            for i, context in enumerate(self.knowledge_base):
                similarity = self.calculate_fit_similarity(query, context) # Assuming calculate_fit_similarity is defined
                # DEBUG PRINT:
                logging.debug(f"Item {i} ({context.get('recommendation')}), Similarity: {similarity:.4f}")
                all_scored_items.append({
                    'context': context,
                    'similarity': similarity
                })

            relevant_fits = [
                item for item in all_scored_items if item['similarity'] > self.similarity_threshold
            ]
            logging.info(f"Found {len(relevant_fits)} relevant fits above threshold {self.similarity_threshold}")

            if relevant_fits:
                best_match = max(relevant_fits, key=lambda x: x['similarity'])
                logging.info(f"Best relevant match: {best_match['context'].get('recommendation')} (Similarity: {best_match['similarity']:.4f})")
                sister_sizes = self.get_sister_sizes(best_match['context']['recommendation']) # Assuming get_sister_sizes is defined
                return {
                    "recommendation": best_match['context']['recommendation'],
                    "confidence": best_match['similarity'],
                    "reasoning": best_match['context']['reasoning'],
                    "fit_tips": best_match['context']['fit_tips'],
                    "identified_issues": identified_issues,
                    "sister_sizes": sister_sizes
                }
            elif all_scored_items:
                closest_match_overall = max(all_scored_items, key=lambda x: x['similarity'])
                logging.info(f"No relevant fits. Closest overall match: {closest_match_overall['context'].get('recommendation')} (Similarity: {closest_match_overall['similarity']:.4f})")
                
                # Check against the low threshold
                if closest_match_overall['similarity'] > 0.1: 
                    sister_sizes = self.get_sister_sizes(closest_match_overall['context']['recommendation'])
                    logging.info("Returning low confidence match.")
                    return {
                        "recommendation": closest_match_overall['context']['recommendation'],
                        "confidence": closest_match_overall['similarity'],
                        "reasoning": "Low confidence match. " + closest_match_overall['context']['reasoning'],
                        "fit_tips": closest_match_overall['context']['fit_tips'],
                        "identified_issues": identified_issues,
                        "sister_sizes": sister_sizes
                    }
                else:
                    logging.info("Closest overall match similarity too low.")
            
            logging.warning("No suitable match found.")
            return {
                "recommendation": None,
                "confidence": 0.0,
                "reasoning": "Unable to find a suitable match based on your information. Please ensure measurements are accurate.",
                "fit_tips": "Please consult our measurement guide or provide more details about your fit issues.",
                "identified_issues": identified_issues,
                "sister_sizes": []
            }

        except ValueError as ve:
            logging.warning(f"Validation error in get_recommendation: {ve}")
            return {"error": str(ve)}
        except Exception as e:
            logging.exception(f"Unexpected error in get_recommendation: {e}") # Use logging.exception here
            return {"error": "An unexpected error occurred while processing your request"}
