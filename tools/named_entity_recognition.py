import tools.utils.api as api

def named_entity_recognition(text):

    system_prompt = """
You are a Named Entity Recognition (NER) agent. Your task is to analyze text and identify all named entities such as people, organizations, locations, dates, and other key elements. Follow these guidelines:

1. Identify and categorize all named entities in the text (People, Organizations, Locations, Dates, Numbers, etc.).
2. Format your output as a structured list with entity categories and their instances.
3. Include context about the entity when it enhances understanding (e.g., "Tim Cook - CEO of Apple").
4. Ensure comprehensive coverage of all entities in the text.
5. Resolve coreferences when possible (e.g., identify that "she" refers to a previously mentioned person).

Your output should be a comprehensive catalog of all the named entities in the text, organized by category.
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
    text = input("Enter the text for entity recognition: ")
    entities = named_entity_recognition(text)
    print(entities)
