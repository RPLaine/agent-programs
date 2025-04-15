import tools.utils.api as api

def html_text_extractor(html_content):
    """
    Extracts the main text content from HTML using an AI-powered extraction process.
    
    Args:
        html_content (str): The HTML content from BeautifulSoup parser
        
    Returns:
        str: The extracted main text content
    """
    system_prompt = """
You are an HTML content extraction specialist. Your task is to analyze HTML content and extract the main body text while removing navigation elements, advertisements, footers, headers, and other non-essential content. Follow these guidelines:

1. Identify and extract only the main content from the provided HTML.
2. Remove all navigation menus, sidebars, footers, headers, and advertisements.
3. Preserve important headings, paragraphs, and relevant formatted text.
4. Maintain the hierarchical structure of the content where appropriate.
5. Ignore boilerplate text, cookie notices, social media buttons, and other non-essential elements.
6. Return only the cleaned, readable main content with basic formatting preserved.

Your output should be clean, well-formatted text that represents only the essential content from the webpage.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
The HTML content is as follows:

{html_content}

The instructions:

1. Identify and extract only the main content from the provided HTML.
2. Remove all navigation menus, sidebars, footers, headers, and advertisements.
3. Preserve important headings, paragraphs, and relevant formatted text.
4. Maintain the hierarchical structure of the content where appropriate.
5. Ignore boilerplate text, cookie notices, social media buttons, and other non-essential elements.
6. Return only the cleaned, readable main content with basic formatting preserved.

Your output should be clean, well-formatted text that represents only the essential content from the webpage.
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 2048}
    response = api.request(data)

    return response

if __name__ == "__main__":
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Article Page</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
        <div class="search">
            <input type="text" placeholder="Search...">
            <button>Search</button>
        </div>
    </header>

    <div class="cookie-notice">
        This website uses cookies. By continuing to browse, you agree to our use of cookies.
        <button>Accept</button>
    </div>

    <aside class="sidebar">
        <h3>Popular Posts</h3>
        <ul>
            <li><a href="#">Article 1</a></li>
            <li><a href="#">Article 2</a></li>
            <li><a href="#">Article 3</a></li>
        </ul>
        <div class="advertisement">
            <p>Special Offer: 50% off new subscriptions!</p>
        </div>
    </aside>

    <main>
        <article>
            <h1>Understanding Machine Learning Algorithms</h1>
            <div class="author">By John Smith | May 15, 2023</div>
            
            <p>Machine learning has revolutionized the way we approach problem solving in the digital age. This article explores the fundamental concepts behind popular algorithms.</p>
            
            <h2>Supervised Learning</h2>
            <p>Supervised learning algorithms build models based on labeled training data. These algorithms learn from known examples to make predictions on new, unseen data.</p>
            <p>Common supervised learning algorithms include:</p>
            <ul>
                <li>Linear Regression</li>
                <li>Logistic Regression</li>
                <li>Decision Trees</li>
                <li>Support Vector Machines (SVM)</li>
            </ul>
            
            <h2>Unsupervised Learning</h2>
            <p>Unlike supervised learning, unsupervised algorithms work with unlabeled data. They identify patterns and structures within the data without predefined outputs.</p>
            <p>Key unsupervised learning approaches include clustering and dimensionality reduction techniques.</p>
            
            <h3>Deep Learning</h3>
            <p>Deep learning is a subset of machine learning that uses neural networks with multiple layers. These deep neural networks have transformed fields like computer vision and natural language processing.</p>
        </article>
    </main>

    <div class="social-buttons">
        <button>Share on Twitter</button>
        <button>Share on Facebook</button>
        <button>Share on LinkedIn</button>
    </div>

    <footer>
        <div class="footer-links">
            <ul>
                <li><a href="/terms">Terms of Service</a></li>
                <li><a href="/privacy">Privacy Policy</a></li>
                <li><a href="/sitemap">Sitemap</a></li>
            </ul>
        </div>
        <p>&copy; 2023 Example Company. All rights reserved.</p>
    </footer>
</body>
</html>
"""
    extracted_text = html_text_extractor(html_content)
    print(extracted_text)
