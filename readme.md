# Bra Fitting Recommendation System - Technical Assessment

## Introduction

This is a simplified version of a bra fitting recommendation system that helps women find their perfect fit. The system uses RAG (Retrieval Augmented Generation) principles to match user measurements and issues with the most relevant recommendations.

## Setup Instructions

Prerequisites
Python 3.7+
Node.js 14+
npm/yarn
Backend Setup
BASH

# Create and activate virtual environment

`python -m venv venv`

# Windows

`.\venv\Scripts\activate`

# Mac/Linux

`source venv/bin/activate`

# Install dependencies

```
cd backend
pip install -r requirements.txt
```

# Run backend

```
uvicorn app.main:app --reload
Frontend Setup
BASH
```

# In the frontend directory

```
cd frontend
npm install
npm start
```

The application will be running at:

```
Frontend: http://localhost:3000
Backend: http://localhost:8000
```

## Tasks Completed & Improvements

### 1. Backend Issues (Status: Completed)

Location: `backend/app/recommender.py`

**Required improvements addressed:**

- **Implemented better similarity matching:** Combined Jaccard similarity for text description and a graded comparison for extracted measurements (underbust, bust) with configurable weighting.
- **Added proper measurement extraction:** Implemented a function (`extract_measurements`) to parse numbers along with context words (e.g., "underbust", "bust") and handle basic variations.
- **Added specific error handling:** Replaced generic `Exception` catches with specific `ValueError` handling for input issues, improved logging (`logging.exception`), and ensured `load_knowledge_base` raises errors on failure. Integrated with FastAPI error handling for appropriate HTTP status codes.
- **Implemented sister size recommendations:** Added `get_sister_sizes` function and included the results in the API response.
- **Improved handling of no matches:** Removed hardcoded default, added logic to find the closest match even below the threshold (with minimum confidence check), and return `recommendation: null` only if no suitable match exists.
- **Corrected similarity threshold:** Adjusted the initial high threshold to a more reasonable starting point.

### 2. Frontend Issues (Status: Completed)

Location: `frontend/src/`

**Required improvements addressed:**

- **Added loading indicators:** Implemented a spinner and disabled the submit button while waiting for the API response.
- **Enhanced recommendation display:** Updated the message component (`Message.js`) to clearly label and display "Recommended Size", "Reasoning", "Fit Tips", and "Sister Sizes" (when available).
- **Improved error handling:** Added logic to correctly parse error messages from the backend (including FastAPI `HTTPException` details) and display them contextually below the input field.
- **Added Unit Tests:** Implemented unit tests for the `useChatbotMessages` hook and the `ChatInterface` component using Jest and React Testing Library.

## Summary of Changes

- Refactored the backend `recommender.py` to address all specified bugs and implement required improvements, focusing on more robust similarity calculations, measurement extraction, error handling, and adding sister size logic.
- Enhanced the frontend `ChatInterface.js` and `Message.js` components to provide loading states, clearer error feedback, and a more detailed display of recommendations including sister sizes.
- Improved backend API error handling in `main.py` to return appropriate HTTP status codes and messages.
- Added basic unit tests for key frontend logic.

## Reasoning Behind Implementation Choices

- **Backend Similarity:** Chose a combination of Jaccard (for text) and custom numeric comparison to avoid adding external NLP libraries (like sentence-transformers) while still providing more nuance than the original implementation. Weights can be tuned based on perceived importance.
- **Measurement Extraction:** Opted for a rule-based approach looking at keywords near numbers, avoiding the `re` module initially for simplicity, but acknowledging regex would be more robust.
- **Error Handling:** Prioritized specific exceptions (`ValueError`) and clear logging (`logging.exception`) on the backend, mapping errors to standard HTTP status codes (400 for client errors, 500/503 for server errors) for standard API behavior.
- **Frontend State Management:** Utilized a custom hook (`useChatbotMessages`) to encapsulate API logic, state (messages, loading, error), promoting separation of concerns.
- **Frontend Testing:** Used Jest and React Testing Library for standard React testing practices, focusing on testing hook logic and component interactions/rendering based on state.

## Instructions for Testing

1.  **Setup:** Follow the Backend and Frontend setup instructions above.
2.  **Run:** Ensure both backend (`uvicorn app.main:app --reload`) and frontend (`npm start` or `yarn start`) are running.
3.  **Access:** Open `http://localhost:3000` in your browser.
4.  **Test Cases:**
    - **Empty Query:** Click "Get Recommendation" without typing anything. Expect an error message "Query text cannot be empty" below the input.
    - **Query without measurements/issues:** Enter text like "hello". Expect an error message "Please provide at least measurements or describe fit issues".
    - **Valid Queries (Examples from Readme):**
      - `I measure 34 underbust and 38 bust, straps keep falling off` (Expect recommendation ~34D, check sister sizes)
      - `My band rides up and I'm measuring 32 under, 37 over` (Expect recommendation ~32C/D, check sister sizes)
      - `36 underbust, 42 bust, getting quadraboob effect` (Expect recommendation ~36DD, check sister sizes)
    - **Loading State:** Send a valid query and observe the button disable and the spinner appear briefly.
    - **Check Console:** Observe backend logs for detailed similarity scores and processing steps.

## Project Structure

(Keep existing structure)
...

## Notes for Candidates

- Focus on code quality and maintainability
- Document any assumptions you make
- Consider edge cases in your implementation
- Don't hesitate to ask clarifying questions
- Remember the 4-hour time limit

Good luck! We're looking forward to seeing your implementation.
