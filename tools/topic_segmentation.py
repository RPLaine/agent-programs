import tools.utils.api as api

def topic_segmentation(text):

    system_prompt = """
You are a text segmentation agent. Your task is to analyze a given text, sentence by sentence, and extract the first contiguous block of sentences that forms a unified and coherent topic. To do this:

1. Evaluate the semantic content and determine topic boundaries based on changes in subject, context, or logical continuity.
2. Begin with the first sentence, and continue including sentences as long as they support the same context or topic.
3. Stop once you detect a significant shift in topic or context.
4. Return only the contiguous block of sentences that you have identified as forming a coherent context.

Make sure that your output contains only this coherent context, without including any sentences that fall outside of it.
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
    text = """
I have always been fascinated by vintage cars. My collection of classic vehicles reflects my admiration for exquisite craftsmanship and timeless design. Every car in my collection tells a story of innovation and passion.

Yesterday, I spent several hours in the garage restoring one of my prized vehicles. I meticulously cleaned each detail and tuned its engine to perfection.

This morning, I shifted my focus to a completely different passion—painting. In my art studio, I mixed vibrant colors and experimented with bold brushstrokes. The creative process fills me with a sense of peace and fulfillment.
"""
    answer = topic_segmentation(text)
    print(answer)