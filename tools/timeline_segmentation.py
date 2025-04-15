import tools.utils.api as api

def timeline_segmentation(text):

    system_prompt = """
You are a timeline segmentation and chronology agent. Your task is to analyze text containing time-based information and organize events into a logical chronological sequence. Follow these guidelines:

1. Identify all events, dates, and temporal references in the text.
2. Arrange these events in chronological order, from earliest to latest.
3. For each event, include the date/time (if specified) and a concise description.
4. Resolve any ambiguous time references based on context.
5. Create a clear, structured timeline that shows how the story has developed over time.

Your output should be a well-organized chronological timeline that helps readers understand the sequence of events described in the original content.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{text}
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)

    return response

if __name__ == "__main__":
    text = input("Enter the text for timeline segmentation: ")
    timeline = timeline_segmentation(text)
    print(timeline)
