import tools.utils.api as api
from tools.text_processor import process_text
from tools.true_or_false import true_or_false

def count_tokens(text):
    system_prompt = """
You are a token counting specialist. Your task is to count the number of tokens in the provided text.
Follow these guidelines:
1. Count the number of tokens in the given text according to standard tokenization rules
2. Respond with only a number - the token count
3. Do not include any explanations, qualifications, or additional context
4. The output should be exactly one number
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

    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)

    max_tries = 3
    tries = 0

    final_output = ""
    is_number_verification = "False"

    while tries < max_tries:
        processed_result = process_text(response, extraction_goal="Extract only the number representing token count", use_typo_check=True)
        final_output = processed_result["final_output"]
    
        is_number_verification = true_or_false(f"Is '{final_output}' a number without any additional text?")
        is_believable = true_or_false(f"Is '{final_output}' a believable token count of this text: '{text}'?")

        if is_believable == "True" and is_number_verification == "True":
            break
        else:
            tries += 1
    
    if is_number_verification == "True":
        try:
            return int(final_output)
        except ValueError:
            try:
                return float(final_output)
            except ValueError:
                return None
    else:
        import re
        number_match = re.search(r'\d+', final_output)
        if number_match:
            return int(number_match.group())
        return None

if __name__ == "__main__":
    input_text = input("Enter text to count tokens: ")
    token_count = count_tokens(input_text)
    print(f"Token count: {token_count}")