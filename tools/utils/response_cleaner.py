def clean_response(response_text):
    tags = ["<|im-system|>", "<|im-user|>", "<|im-assistant|>", "<|im-end|>", "<|im-response|>"]
    cleaned_text = response_text

    if "<|im-assistant|>" in cleaned_text:
        cleaned_text = cleaned_text.split("<|im-assistant|>", 1)[1]

    if "<|im-end|>" in cleaned_text:
        cleaned_text = cleaned_text.split("<|im-end|>", 1)[0]
    
    for tag in tags:
        parts = cleaned_text.split(tag)
        cleaned_text = "".join(parts)
    
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

if __name__ == "__main__":
    input_text = input("Enter response text to clean: ")
    result = clean_response(input_text)
    
    print(f"\nCleaned text: {result}")
