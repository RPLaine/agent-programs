from tools.information_distiller import extract_key_information
from tools.typo_checker import check_typos

def process_text(input_text, extraction_goal=None, use_distiller=True, use_typo_check=True):
    result = {
        "original_text": input_text,
    }
    
    processed_text = input_text
    
    if use_distiller:
        distilled_info = extract_key_information(input_text, extraction_goal=extraction_goal)
        processed_text = distilled_info["distilled_result"]
        result["extraction_goal"] = distilled_info["extraction_goal"]
        result["distilled_result"] = processed_text
    
    if use_typo_check:
        typo_check_result = check_typos(processed_text)
        result["typo_check_result"] = typo_check_result
        
        if "text is correct" not in typo_check_result.lower():
            lines = typo_check_result.split('\n')
            for i, line in enumerate(lines):
                if any(marker in line.lower() for marker in ["corrected version:", "correction:", "corrected text:"]):
                    if i + 1 < len(lines):
                        processed_text = lines[i + 1].strip()
                        break
    
    result["final_output"] = processed_text
    
    return result

if __name__ == "__main__":
    use_custom_goal = input("Use custom extraction goal? (y/n): ").lower() == 'y'
    extraction_goal = None
    
    if use_custom_goal:
        extraction_goal = input("Enter extraction goal: ")
    
    text_to_process = input("Enter the text to process: ")

    result = process_text(text_to_process, extraction_goal)
    print(f"\nProcessed text:")
    
    print(f"\nOriginal text: {result['original_text']}")
    
    if "extraction_goal" in result:
        print(f"Extraction goal: {result['extraction_goal']}")
        print(f"Distilled result: {result['distilled_result']}")
    
    if "typo_check_result" in result:
        print(f"Typo check result: {result['typo_check_result']}")
    
    print(f"\nFinal output: {result['final_output']}")
