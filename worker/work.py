import asyncio

from worker.tools.create_query import main as create_query
from worker.tools.improve_content import main as improve_content


async def websearch(task: str = "", data: dict = {}) -> dict:
    if not task or not data:
        print("No task or data provided for web search.")
        return { "error": "No task or data provided" }
    
    from tools.explanation_websearch import explanation_with_websearch as get_web_research

    query_text: str = await create_query(data, task)
    result = await get_web_research(query_text)

    return result

async def use_new_data(data: dict = {}, new_data: str = "", task: str = "") -> str:
    if not data or not new_data or not data:
        print("No data, new data, or task provided for use_data.")
        return ""


    result = await improve_content(data, new_data, task)

    return result

async def main(data: dict = {}) -> None:
    for task in data["tasks"]:
        print(f"Processing task: {task['task']}")

        task["data"] = []

        for tool in task["tools"]:
            if tool == "Let AI do a web search":
                print(f"Performing web search for task: {task['task']}")

                websearch_result = await websearch(task["task"], data)
                task["data"].append(websearch_result)

                improved_content = await use_new_data(data, websearch_result["result"], task)
                
                # test if data["content"] is a string
                if isinstance(data["content"], str):
                    content_list = [data["content"]]
                    data["content"] = content_list

                data["content"].append(improved_content)
                
                return # DEVELOPMENT ENDPOINT - remove this line in production
                
            elif tool == "Let AI search RSS feeds":
                # Simulate searching RSS feeds
                print(f"Searching RSS feeds for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
            elif tool == "Let a journalist take a photo":
                # Simulate taking a photo
                print(f"Taking photo for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
            elif tool == "Let a journalist interview a person":
                # Simulate interviewing a person
                print(f"Interviewing for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
            else:
                print(f"Unknown tool: {tool}")
                # wait a second
                await asyncio.sleep(1)
        # Simulate task completion


if __name__ == "__main__":
    import asyncio
    import json

    content: str = "9, 8, 7, 6, 5, 4, 3, 2, 1"

    data: dict = {
        "claim": "ascending list of numbers",
        "content": content,
        "iterations": 3,
        "tasks": [
            {
                "task": "Check the numbers are ascending.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            },
            {
                "task": "Use subheadings to organize the article into distinct sections focusing on key points such as the geopolitical importance of the Indo-Pacific, India's vision for the region, and the EU's strategy.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            },
            {
                "task": "Provide concrete examples and statistics to support claims about the region's economic and security significance, making the article more engaging and credible.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds",
                    "Let a journalist take a photo"
                ]
            },
            {
                "task": "Integrate quotes or statements from key figures like Prime Minister Modi and External Affairs Minister Dr. S. Jaishankar to add depth and authenticity to the piece.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            },
            {
                "task": "Include visual elements like maps or infographics to help readers understand the geographical scope of the Indo-Pacific and the global flow of trade and security partnerships.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds",
                    "Let a journalist take a photo",
                    "Let a journalist interview a person"
                ]
            },
            {
                "task": "Expand on the mention of specific initiatives and strategies, such as the Indo-Pacific Oceans' Initiative, the Forum for India-Pacific Islands Cooperation, and the Indo-Pacific Economic Framework, explaining their objectives and impact.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            },
            {
                "task": "Elaborate on the shared values and goals between India and the EU, including their commitment to peace, security, and sustainable development in the Indo-Pacific.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            },
            {
                "task": "Emphasize the historical and cultural links between the Indian Ocean and the regions it connects, enriching the narrative with stories of trade routes and syncretism.",
                "tools": [
                    "Let AI do a web search",
                    "Let a journalist interview a person"
                ]
            },
            {
                "task": "Conclude the article with a forward-looking perspective, discussing the potential for future collaboration and the role of India and the EU in shaping a secure and prosperous Indo-Pacific.",
                "tools": [
                    "Let AI do a web search",
                    "Let AI search RSS feeds"
                ]
            }
        ]
    }

    asyncio.run(main(data))

    print(json.dumps(data, indent=4))