import tools.utils.api as api
from tools.web.google_search import google_search, get_content, extract_text_from_html
from tools.summarization import summarization

def topic_classification(text):
    system_prompt = """
You are a topic classification and trend analysis agent. Your task is to analyze content and categorize it into appropriate topics while also identifying relevant trends. Follow these guidelines:

1. Classify the content into primary and secondary topic categories
2. Identify key trending topics, themes, or narratives present in the content.
3. Note any emerging patterns or shifts in topic emphasis compared to standard coverage.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Topic summary:
{text}

Create only one message of the topic classification.
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)

    return response

def topic_classification_with_websearch(query, num_results=3):
    print(f"[INFO] 🔍 Searching for: {query}")
    results = google_search(query, num_results=num_results)
    print(f"[INFO] 📊 Found {len(results)} search results")
    
    all_text = ""
    processed_links = []
    
    for result in results:
        link = result["link"]
        processed_links.append(link)
        print(f"[INFO] 🌐 Processing link: {link}")
        
        html_content = get_content(link)
        if html_content:
            extracted_text = extract_text_from_html(html_content)
            summarized_text = summarization(extracted_text, focus=query)
            
            if summarized_text:
                print(f"[INFO] ✅ Successfully extracted and summarized content from {link}")
                all_text += f"\n\nContent from {link}:\n{summarized_text}"
            else:
                print(f"[INFO] ⚠️ Content from {link} was not relevant to the query.")
        else:
            print(f"[WARNING] ❌ Failed to retrieve content from {link}")
            
    if not all_text:
        print("[WARNING] ❗ No relevant content found in search results")
        return {
            "original_query": query,
            "links": processed_links,
            "topic_classification": "No relevant content found for classification."
        }
    
    print("[INFO] 📝 Creating final summary of all content...")
    final_summary = summarization(all_text, focus=query)
    
    print("[INFO] 🔍 Performing topic classification...")
    topic_analysis = topic_classification(final_summary)
    
    return {
        "original_query": query,
        "links": processed_links,
        "topic_classification": topic_analysis
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Topic Classification Tool")
    parser.add_argument("--query", type=str, help="A search query to find content for topic classification")
    parser.add_argument("--results", type=int, default=3, help="Number of search results to use (default: 3)")
    parser.add_argument("--direct", action="store_true", help="Enter text directly instead of web search")
    
    args = parser.parse_args()
    
    if args.direct:
        text = input("Enter the text for topic classification: ")
        analysis = topic_classification(text)
        print("\nTopic Classification:")
        print(analysis)
    else:
        if not args.query:
            args.query = input("Enter a search query for topic classification: ")
        
        print(f"[INFO] Starting topic classification with web search for: {args.query}")
        result = topic_classification_with_websearch(
            query=args.query,
            num_results=args.results
        )
        
        print("\n" + "="*50)
        print(f"[RESULT] Topic Classification for: {result['original_query']}")
        print(f"Links Searched ({len(result['links'])}):")
        for i, link in enumerate(result['links'], 1):
            print(f"  {i}. {link}")
        print("\nTopic Classification:")
        print(result['topic_classification'])
        print("="*50)
