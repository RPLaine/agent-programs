def enforce_binary_output(response):
    response = response.lower()
    
    true_unique = {'t', 'u'}
    false_unique = {'a', 'l', 's'}
    
    true_score = sum(1 for letter in response if letter in true_unique)
    false_score = sum(1 for letter in response if letter in false_unique)
    
    if true_score > false_score:
        return True
    else:
        return False

def enforce_number_output(response):
    import re
    
    # Extract all numbers from the response
    numbers = re.findall(r'-?\d+\.?\d*', response)
    
    # Return first number found or 0 if none found
    if numbers:
        try:
            # First try to convert to int if it's a whole number
            if '.' not in numbers[0]:
                return int(numbers[0])
            else:
                return float(numbers[0])
        except ValueError:
            pass
    
    return 0

def extract_multi_option_selection(response, options):
    """
    Extracts the selected option from the AI's response.
    
    Args:
        response (str): The AI's response text
        options (list): List of possible options to select from
        
    Returns:
        str: The selected option or the first option if no match is found
    """
    response = response.lower().strip()
    
    # If response directly matches one of the options (exact match)
    for option in options:
        if option.lower() == response:
            return option
    
    # Check for option mention in the response
    option_scores = {}
    for option in options:
        # Calculate how many words from this option appear in the response
        option_words = set(option.lower().split())
        matches = sum(1 for word in option_words if word in response)
        option_scores[option] = matches
    
    # Return option with highest score
    if option_scores:
        max_score = max(option_scores.values())
        # If any options were found in the response
        if max_score > 0:
            # Get all options with the max score
            best_options = [opt for opt, score in option_scores.items() if score == max_score]
            return best_options[0]  # Return the first best match
    
    # If no good matches, return the first option as default
    return options[0] if options else "No option selected"