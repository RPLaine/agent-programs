import tools.utils.api as api
from tools.web.google_search import google_search
from tools.information_distiller import extract_key_information

def extract_query_keywords(query):
    print(f"[KEYWORD EXTRACTION] Processing query: '{query}'")
    system_prompt = """
You are a keyword extraction specialist. Your task is to identify the most important keywords from a search query. Follow these guidelines:

1. Identify nouns, verbs, and specific terms that carry the core meaning of the query
2. Remove filler words, articles, and prepositions
3. Prioritize domain-specific and technical terms
4. List keywords in order of importance
5. Do not rephrase or optimize the query, only extract existing keywords
6. Include proper nouns and named entities as individual keywords
7. Return only a comma-separated list of keywords with no additional text
"""    
    try:
        print("[KEYWORD EXTRACTION] Fetching search results...")
        search_results = google_search(query, num_results=3)
        print(f"[KEYWORD EXTRACTION] Successfully retrieved {len(search_results)} search results")
    except Exception as e:
        print(f"[KEYWORD EXTRACTION] Error during search: {e}")
        search_results = []
    
    search_context = ""
    if search_results:
        links = [result["link"] for result in search_results]
        search_context = f"Search results found: {', '.join(links)}"
        print(f"[KEYWORD EXTRACTION] Search contexts: {links}")
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Original search query: {query}

{search_context}

Please extract only the most important keywords from this query without optimizing or rephrasing it.
Return only a comma-separated list of keywords.
<|im-end|>
<|im-assistant|>
"""    
    print("[KEYWORD EXTRACTION] Sending API request for keyword extraction...")
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)
    
    print("[KEYWORD EXTRACTION] Processing API response...")
    keywords_response = extract_key_information(response, extraction_goal="Extract only the comma-separated keywords")["distilled_result"]
    
    keywords = [keyword.strip() for keyword in keywords_response.split(",") if keyword.strip()]
    print(f"[KEYWORD EXTRACTION] Extracted {len(keywords)} keywords: {', '.join(keywords)}")
    
    return {
        "original_query": query,
        "keywords": keywords
    }

def get_keyword_importance(query):
    print(f"[IMPORTANCE ANALYSIS] Starting keyword importance analysis for: '{query}'")
    keywords_result = extract_query_keywords(query)
    keywords = keywords_result["keywords"]
    if not keywords:
        print("[IMPORTANCE ANALYSIS] No keywords found, returning empty result")
        return {
            "original_query": query,
            "keywords": [],
            "importance_ratings": {}
        }
    
    system_prompt = """
You are a keyword importance analysis specialist. Your task is to rate the importance of keywords for a search query on a scale of 1-10. Follow these guidelines:

1. Consider each keyword's specificity and relevance to the search topic
2. Rate general terms lower and specific terms higher
3. Consider the uniqueness of terms in driving search relevance
4. Give higher scores to terms that disambiguate the query's intent
5. Provide only numerical ratings for each keyword with no explanations
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Original search query: {query}
Keywords: {', '.join(keywords)}

Please rate each keyword on a scale of 1-10 based on its importance to this search query.
Format your response as a simple list with each line containing "keyword: rating", for example:
machine: 8
learning: 7
<|im-end|>
<|im-assistant|>
"""    
    print("[IMPORTANCE ANALYSIS] Sending API request for importance ratings...")
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)
    
    print("[IMPORTANCE ANALYSIS] Processing importance ratings...")
    ratings = {}
    extracted_ratings = extract_key_information(response, extraction_goal="Extract only the keyword ratings in the format 'keyword: rating'")["distilled_result"]
    for line in extracted_ratings.split("\n"):
        line = line.strip()
        if ":" in line:
            parts = line.split(":", 1)
            keyword = parts[0].strip()
            try:
                rating = int(parts[1].strip())
                ratings[keyword] = rating
                print(f"[IMPORTANCE ANALYSIS] Keyword '{keyword}' rated {rating}/10")
            except ValueError:
                print(f"[IMPORTANCE ANALYSIS] Invalid rating format for keyword '{keyword}'")
                pass
    
    return {
        "original_query": query,
        "keywords": keywords,
        "importance_ratings": ratings
    }

if __name__ == "__main__":
    user_query = input("Enter a search query to extract keywords: ")
    result = get_keyword_importance(user_query)
    
    print(f"\nOriginal query: {result['original_query']}")
    print(f"Extracted keywords: {', '.join(result['keywords'])}")
    
    print("\nKeyword importance ratings:")
    for keyword, rating in result['importance_ratings'].items():
        print(f"  {keyword}: {rating}/10")
