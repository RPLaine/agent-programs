import asyncio

from worker.tools.create_query import main as create_query
from worker.tools.improve_content import main as improve_content
from tools.web.web_research import get_web_research


async def main(data: dict = {}) -> None:
    print(f"\n==== STARTING WORK MODULE ====")
    print(f"Processing {len(data['tasks'])} tasks")
    
    for i, task in enumerate(data["tasks"]):
        print(f"\n[Task {i+1}/{len(data['tasks'])}] Processing: {task['task']}")

        task["data"] = []

        for tool in task["tools"]:
            if tool == "Let AI do a web search":
                print(f"🔍 Performing web search for task: {task['task']}")

                web_research_query = await create_query(data, task["task"])
                print(f"  ├─ Created query: {web_research_query[:50]}..." if len(web_research_query) > 50 else f"  ├─ Created query: {web_research_query}")
                
                websearch_result = await get_web_research(web_research_query, 3)
                print(f"  ├─ Web search completed: {len(websearch_result['summary'])} characters in summary")
                
                task["data"].append(websearch_result)

                print(f"  ├─ Improving content based on search results...")
                improved_content = await improve_content(data, websearch_result["summary"], task)
                print(f"  └─ Content improved: {len(improved_content)} characters")
            

                data["content"].append(improved_content)
                
                return # DEVELOPMENT ENDPOINT - remove this line in production
                
            elif tool == "Let AI search RSS feeds":
                # Simulate searching RSS feeds
                print(f"📰 Searching RSS feeds for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
                print(f"  └─ RSS search completed (simulated)")
            elif tool == "Let a journalist take a photo":
                # Simulate taking a photo
                print(f"📷 Taking photo for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
                print(f"  └─ Photo captured (simulated)")
            elif tool == "Let a journalist interview a person":
                # Simulate interviewing a person
                print(f"🎤 Interviewing for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
                print(f"  └─ Interview completed (simulated)")
            else:
                print(f"❓ Unknown tool: {tool}")
                # wait a second
                await asyncio.sleep(1)
        
        print(f"✅ Task {i+1} completed: {task['task']}")
    
    print(f"\n==== WORK MODULE COMPLETED ====")


if __name__ == "__main__":
    import asyncio
    import json

    content: str = "9, 8, 7, 6, 5, 4, 3, 2, 1"

    data: dict = {
        "claim": "ascending list of numbers",
        "content": [content],
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