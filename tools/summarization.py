import tools.utils.api as api
from tools.true_or_false import true_or_false

async def summarization(text, focus="", recursion_level=0):
    MAX_CHARS = 5000
    MAX_RECURSION = 3
    
    print(f"📝 Summarizing text ({len(text)} characters){' with focus on ' + focus if focus else ''}")
    print(f"  ├─ Recursion level: {recursion_level}/{MAX_RECURSION}")
    
    if recursion_level >= MAX_RECURSION:
        print(f"  ├─ ⚠️ Maximum recursion level reached ({MAX_RECURSION}). Forcing direct summarization.")
        truncated_text = text[:MAX_CHARS]
        print(f"  ├─ Text truncated from {len(text)} to {len(truncated_text)} characters.")
        text = truncated_text
    elif len(text) > MAX_CHARS:
        print(f"  ├─ Text exceeds maximum length ({len(text)}/{MAX_CHARS} characters)")
        print(f"  ├─ Breaking text into smaller parts...")
        return await handle_long_text(text, focus, MAX_CHARS, recursion_level)
    
    if focus:
        print(f"  ├─ Checking relevance to focus: \"{focus}\"")
        if true_or_false(f"Focus: {focus} . Is the focus valid for this text: {text} ?"):
            print(f"  ├─ ✅ Text is relevant to the focus")
        else:
            print(f"  ├─ ⚠️ Text is not relevant to the focus. Skipping summarization.")
            return ""
    
    print(f"  ├─ Generating summary...")
    system_prompt = f"""
You are a text summarization agent. Your task is to distill lengthy articles or transcripts into concise, informative summaries with a specific focus. Follow these guidelines:

1. Focus specifically on information related to: "{focus}"
2. Identify and capture the main points, key arguments, and essential details of the content related to this focus.
3. Maintain factual accuracy while condensing the information.
4. Preserve the original tone and perspective of the content.
5. Organize the summary in a logical flow that mirrors the structure of the original text.
6. Ensure the summary stands on its own as a coherent piece.
7. Prioritize content that directly addresses the focus area.

Your output should be a concise summary that allows readers to quickly grasp the essential details related to the focus area without needing to read the entire text.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Please summarize the following text with a specific focus on information related to: "{focus}"

{text}

Respond with only one message.
<|im-end|>
<|im-assistant|>
"""
 
    data = {"prompt": prompt, "max_length": 5000}
    response = await api.request(data)
    print(f"  └─ Summary generated: {len(response)} characters")
    return response

async def handle_long_text(text, focus, max_chars, recursion_level):
    parts = split_text(text, max_chars)
    print(f"  ├─ Text split into {len(parts)} parts")
    
    # Limit to 5 parts if there are more than 5
    if len(parts) > 5:
        print(f"  ├─ ⚠️ Limiting from {len(parts)} to 5 parts due to part limit...")
        # Take only the first 5 parts and ignore the rest
        parts = parts[:5]
    
    part_summaries = []
    for i, part in enumerate(parts):
        print(f"  ├─ Processing part {i+1}/{len(parts)} ({len(part)} characters)...")
        part_summary = await summarization(part, focus, recursion_level + 1)
        if part_summary:
            part_summaries.append(part_summary)
            print(f"  │   └─ Part {i+1} summary: {len(part_summary)} characters")
    
    if not part_summaries:
        print(f"  └─ ⚠️ No relevant content found in any part")
        return ""
    
    combined_summary = "\n\n".join(part_summaries)
    print(f"  ├─ Combined {len(part_summaries)} part summaries: {len(combined_summary)} characters")
    
    # Check if further summarization is needed and if we haven't hit recursion limit
    if len(parts) > 1 and recursion_level < 3:
        print(f"  ├─ Creating final consolidated summary...")
        return await summarization(combined_summary, focus, recursion_level + 1)
    
    return combined_summary

def split_text(text, max_chars):
    if len(text) <= max_chars:
        return [text]
        
    paragraphs = text.split("\n\n")
    
    parts = []
    current_part = ""
    current_length = 0
    target_length = max_chars * 0.9
    
    for paragraph in paragraphs:
        paragraph_length = len(paragraph)
        if current_length + paragraph_length + 2 > max_chars and current_part:
            if current_length < target_length and paragraph_length > max_chars * 0.5:
                sentences = split_into_sentences(paragraph)
                for sentence in sentences:
                    sentence_length = len(sentence)
                    if current_length + sentence_length + 1 <= max_chars:
                        if current_part:
                            current_part += " " + sentence
                            current_length += sentence_length + 1
                        else:
                            current_part = sentence
                            current_length = sentence_length
                    else:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = sentence
                            current_length = sentence_length
                        elif sentence_length > max_chars:
                            chunks = [sentence[i:i+max_chars] for i in range(0, len(sentence), max_chars)]
                            parts.extend(chunks[:-1])
                            current_part = chunks[-1]
                            current_length = len(current_part)
                        else:
                            current_part = sentence
                            current_length = sentence_length
            else:
                parts.append(current_part.strip())
                current_part = paragraph
                current_length = paragraph_length
        else:
            if current_part:
                current_part += "\n\n" + paragraph
                current_length += paragraph_length + 2
            else:
                current_part = paragraph
                current_length = paragraph_length
                
    if current_part:
        parts.append(current_part.strip())
    
    final_parts = []
    for part in parts:
        if len(part) <= max_chars:
            final_parts.append(part)
        else:
            sentences = split_into_sentences(part)
            sentence_parts = []
            current_part = ""
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                if current_length + sentence_length + 1 > max_chars and current_part:
                    sentence_parts.append(current_part.strip())
                    current_part = sentence
                    current_length = sentence_length
                else:
                    if current_part:
                        current_part += " " + sentence
                        current_length += sentence_length + 1
                    else:
                        current_part = sentence
                        current_length = sentence_length
            
            if current_part:
                sentence_parts.append(current_part.strip())
                
            final_parts.extend(sentence_parts)
    
    optimized_parts = []
    i = 0
    while i < len(final_parts):
        current = final_parts[i]
        current_length = len(current)
        
        if current_length < target_length and i < len(final_parts) - 1:
            next_part = final_parts[i + 1]
            next_length = len(next_part)
            
            if current_length + next_length + 2 <= max_chars:
                combined = current + "\n\n" + next_part
                optimized_parts.append(combined)
                i += 2
            else:
                optimized_parts.append(current)
                i += 1
        else:
            optimized_parts.append(current)
            i += 1
    
    return optimized_parts

def split_into_sentences(text):
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char in ['.', '!', '?'] and len(current) > 1:
            next_char_pos = len(current)
            while next_char_pos < len(text) and text[next_char_pos].isspace():
                next_char_pos += 1
            
            if next_char_pos >= len(text) or text[next_char_pos].isupper():
                sentences.append(current.strip())
                current = ""
    
    if current:
        sentences.append(current.strip())
    
    return sentences

if __name__ == "__main__":
    import asyncio
    
    text = """
To develop a machine learning model that can generate a summary for a given text, a deep learning approach using transformer-based architectures, such as BERT or T5, can be effective. The first step is data collection, where a large dataset of documents and their corresponding summaries is required. Preprocessing the data involves cleaning the text, tokenizing, and dividing the dataset into training, validation, and testing sets.
After preprocessing, the next step is training the model using the training dataset. This can be done using a framework like TensorFlow or PyTorch. The model is trained to predict the summary given the full text. During training, the model learns to understand the structure and content of the text to generate accurate summaries.
Evaluation is a crucial step in the process. The model's performance is evaluated using metrics such as ROUGE (Recall-Oriented Understudy for Gisting Evaluation) and BLEU (Bilingual Evaluation Understudy). These metrics measure the overlap between the generated summaries and the reference summaries to assess the model's performance.
Fine-tuning and optimization are the final steps in developing the model. The model can be fine-tuned using the validation set to improve its performance. Techniques like learning rate scheduling, weight decay, and dropout can be used to prevent overfitting and improve the model's generalization ability.
Once the model is trained and optimized, it can be used to generate summaries for new texts. The generated summaries can then be evaluated for coherence, relevance, and fluency to ensure they meet the desired standards.
"""
    summary = asyncio.run(summarization(text))
    print(summary)
