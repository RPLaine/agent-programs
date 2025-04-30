from tools.web.google_search import google_search, get_content, extract_text_from_html
from tools.summarization import summarization
from tools.information_distiller import distill_text

async def get_web_research(
    query, 
    num_results=3,
    custom_focus=None
):
    print(f"🔍 Performing web research for query: '{query}'")
    print(f"  ├─ Number of search results requested: {num_results}")
    if custom_focus:
        print(f"  ├─ Custom focus for summarization: '{custom_focus}'")
    
    actual_num_results = num_results
    try:
        print(f"  ├─ Estimating required number of searches...")
        number_of_searches = num_results
        # number_of_searches = int(get_number("What is the good number of web searches required for an educated answer for this question: " + query + " ?"))
    except Exception as e:
        print(f"  ├─ ⚠️ Failed to get number of searches: {e}")
        number_of_searches = num_results

    print(f"  ├─ Recommended number of searches: {number_of_searches}")
    
    if number_of_searches > 5:
        print(f"  ├─ ⚠️ Limiting number of searches to maximum of 5")
        actual_num_results = 5
    elif number_of_searches < 1:
        print(f"  ├─ ⚠️ Setting minimum number of searches to 1")
        actual_num_results = 1
    else:
        actual_num_results = number_of_searches
    
    print(f"  ├─ Executing search with {actual_num_results} results...")
    results = google_search(query, num_results=actual_num_results)
    print(f"  ├─ Search completed with {len(results)} results")
    
    all_text = ""
    links = []
    
    focus_for_content = custom_focus if custom_focus else ""
    
    for i, result in enumerate(results):
        link = result["link"]
        links.append(link)
        print(f"  ├─ [{i+1}/{len(results)}] Retrieving content from: {link[:50]}..." if len(link) > 50 else f"  ├─ [{i+1}/{len(results)}] Retrieving content from: {link}")
        
        html_content = get_content(link)
        
        if html_content:
            extracted_text = extract_text_from_html(html_content)
            print(f"  │   ├─ Extracted {len(extracted_text)} characters")
            print(f"  │   ├─ Summarizing content...")
            text_content = await summarization(extracted_text, focus=focus_for_content)
            print(f"  │   └─ Summary created: {len(text_content)} characters")
            all_text += f"\n\nContent from {link}:\n{text_content}"
        else:
            print(f"  │   └─ ❌ Failed to retrieve content")
    
    if all_text:
        print(f"  ├─ Generating final summary from {len(all_text)} characters...")
        summary = await distill_text(all_text, focus_for_content)
        print(f"  ├─ Final summary created: {len(summary)} characters")
        all_text += f"\n\n{summary}"
        
        return {
            "query": query,
            "links": links, 
            "summary": all_text
        }
    else:
        print(f"  └─ ⚠️ No content could be extracted from search results")
        return {
            "query": query,
            "links": links, 
            "summary": "No content could be extracted from the search results."
        }
    
    print(f"  └─ Web research completed")

if __name__ == "__main__":
    # Test the web research functionality
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Web Research Tool")
    parser.add_argument("query", type=str, help="The search query to research")
    parser.add_argument("--results", type=int, default=3, help="Number of search results to use (default: 3)")
    parser.add_argument("--focus", type=str, help="Custom focus for summarization")
    
    args = parser.parse_args()
    
    print(f"[INFO] Starting web research for query: {args.query}")
    result = asyncio.run(get_web_research(
        query=args.query,
        num_results=args.results,
        custom_focus=args.focus
    ))
    
    print("\n" + "="*50)
    print(f"[RESULT] Web Research Summary:")
    print(f"Query: {result['query']}")
    print(f"Links Searched ({len(result['links'])}):")
    for i, link in enumerate(result['links'], 1):
        print(f"  {i}. {link}")
    print("\nSummary:")
    print(result['summary'])
    print("="*50)
