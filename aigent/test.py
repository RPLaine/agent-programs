from aigent.test_claim import main as test_claim

async def main(data: dict = {}) -> dict:
    """
    Test if user_input is the desired product.
    
    Args:
        data (dict): A dictionary containing the user input, desired product, and iteration count.
    
        Example:
            {
                "user_input": "I went to a zoo. There was a giraffe. It looked at me. I looked at it. That was my day.",
                "desired_product": "a good list of executable tasks",
                "iteration_count": 5
            }

    Returns:
        dict: A dictionary containing the test results.
    """
    if not data:
        data["error"] = "No data."
        return data
    
    result: dict = await test_claim(data["user_input"], data["desired_product"], data["iteration_count"])
    data["result"] = result
    return data