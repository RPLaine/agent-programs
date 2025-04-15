import tools.utils.api as api
import tools.information_distiller as distiller

def check_typos(input_text):
    system_prompt = """
You are a typo detection specialist. Your task is to identify and correct any typographical errors or spelling mistakes in the user's input. Follow these guidelines:

1. Identify any spelling errors or typos in the text
2. Suggest corrections for each identified typo
3. If no typos are found, indicate that the text is correct
4. Do not change the meaning or intent of the original text
5. Focus only on spelling and typographical errors, not grammar or style
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Input: {input_text}

Please identify any typos or spelling errors in this text. If you find any, provide the corrected version. If no typos are found, indicate that the text is correct.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)

    response = distiller.extract_key_information(response)["distilled_result"]
    
    return response.strip()

def check_and_correct(input_text):
    typo_check_result = check_typos(input_text)
    
    return {
        "original_text": input_text,
        "typo_check_result": typo_check_result
    }

if __name__ == "__main__":
    user_input = input("Enter text to check for typos: ")
    result = check_and_correct(user_input)
    print(f"Original text: {result['original_text']}")
    print(f"Typo check result: {result['typo_check_result']}")
