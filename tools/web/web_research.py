from tools.web.google_search import google_search, get_content, extract_text_from_html
from tools.summarization import summarization
from tools.information_distiller import distill_text
from tools.number_response import get_number

def get_web_research(
    query, 
    num_results=3,
    custom_focus=None
):
    print(f"[INFO] Performing web research for query: {query}")
    print(f"[INFO] Number of search results to retrieve: {num_results}")
    print(f"[INFO] Custom focus for summarization: {custom_focus}")
    
    actual_num_results = num_results
    try:
        print("Estimating the number of searches required...")
        number_of_searches = num_results
        # number_of_searches = int(get_number("What is the good number of web searches required for an educated answer for this question: " + query + " ?"))
    except Exception as e:
        print(f"[ERROR] Failed to get number of searches: {e}")
        number_of_searches = num_results

    print(f"[INFO] Number of searches recommended: {number_of_searches}")
    
    if number_of_searches > 5:
        print("[WARN] Limiting number of searches to 5")
        actual_num_results = 5
    elif number_of_searches < 1:
        print("[WARN] Limiting number of searches to 1")
        actual_num_results = 1
    else:
        actual_num_results = number_of_searches
        print(f"[INFO] Performing search with {actual_num_results} results...")

    results = google_search(query, num_results=actual_num_results)
    print(f"[DEBUG] Search results: {results}")
    
    all_text = ""
    links = []
    
    focus_for_content = custom_focus if custom_focus else ""
    print(f"[INFO] Focus for content: {focus_for_content}")
    
    for result in results:
        link = result["link"]
        links.append(link)        
        html_content = get_content(link)
        
        if html_content:
            extracted_text = extract_text_from_html(html_content)
            text_content = summarization(extracted_text, focus=focus_for_content)                  
            all_text += f"\n\nContent from {link}:\n{text_content}"
        else:
            print(f"[ERROR] Failed to retrieve content from {link}.")
    
    if all_text:        
        print(f"[INFO] Generating final summary...")
        print(f"[INFO] Focus for content: {focus_for_content}")
        print(f"[INFO] All text content: {all_text}")
        summary = distill_text(all_text, focus_for_content)
        print(f"[INFO] Final summary: {summary}")
        all_text += "\n\n" + summary
        print(f"[INFO] Final summary added to all text.")
        
        return {
            "query": query,
            "links": links, 
            "summary": all_text
        }
    else:
        return {
            "query": query,
            "links": links, 
            "summary": "No content could be extracted from the search results."
        }

if __name__ == "__main__":
    # Test the web research functionality
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Research Tool")
    parser.add_argument("query", type=str, help="The search query to research")
    parser.add_argument("--results", type=int, default=3, help="Number of search results to use (default: 3)")
    parser.add_argument("--focus", type=str, help="Custom focus for summarization")
    
    args = parser.parse_args()
    
    print(f"[INFO] Starting web research for query: {args.query}")
    result = get_web_research(
        query=args.query,
        num_results=args.results,
        custom_focus=args.focus
    )
    
    print("\n" + "="*50)
    print(f"[RESULT] Web Research Summary:")
    print(f"Query: {result['query']}")
    print(f"Links Searched ({len(result['links'])}):")
    for i, link in enumerate(result['links'], 1):
        print(f"  {i}. {link}")
    print("\nSummary:")
    print(result['summary'])
    print("="*50)
