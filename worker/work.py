import asyncio

async def main(data: dict = {}) -> None:
    for task in data["tasks"]:
        for tool in task["tools"]:
            if tool == "Let AI do a web search":
                # Simulate web search
                print(f"Performing web search for task: {task['task']}")
                # wait a second
                await asyncio.sleep(1)
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

    content: str = "The world, as we see today, is at the cusp of a new era, when the process of global rebalancing has reached a critical point. While global crises have highlighted over-dependencies and vulnerabilities, heightened uncertainties have jolted us to recalibrate our thinking of the global world order. This global landscape provides a strong rationale for India and the European Union to engage deeper. The recent College of Commissioners\u2019 visit to India in February 2025 \u2013 the first-ever undertaken by the Commission to a non-European bilateral partner, befittingly captured the consequentiality of the India \u2013 EU partnership, and its reimagination and realignment.\nGlobal geopolitics, particularly the challenges in the Indo-Pacific region are attracting attention worldwide. The region, surrounded by not less than thirty seven countries, not only holds more than sixty percent of the world\u2019s population, but is also crucial to the world\u2019s trade, economy and security contributing over sixty percent of the world\u2019s GDP and with forty five percent of global trade passing through it. It is, thus, only natural to find the Indo-Pacific region as an area of not just deep interest, but also intense coordination and cooperation.\nPrime Minister Modi had outlined India\u2019s broader approach to the Indo-Pacific in his speech at Shangri La Dialogue in Singapore in 2018. India envisages a free, inclusive, open, peaceful and a prosperous Indo-Pacific which is built on a rules based order and founded on principles of international law including the law of the sea (UNCLOS). Such an Indo-Pacific holds sustainable infrastructure, transparent investments, freedom of navigation and secure supply chains as its hallmarks. India\u2019s vision of the Indo-Pacific is inclusive of all nations including, but not limited to its immediate geography. This is encapsulated by the acronym \u2018SAGAR\u2019 which stands for \u2018security and growth for all\u2019 and means ocean in Hindi.\nToday, the Indo-Pacific features prominently in India\u2019s foreign policy and defence strategy. It is equally an important term in the lexicon of its various partnerships - bilateral and multilateral. In 2019, Prime Minister Modi announced the Indo-Pacific Oceans\u2019 Initiative at the 14th East Asia Summit in Bangkok. India has also been at the forefront of cooperation on ensuring maritime security. Notably, it was for the first time that the United Nations Security Council discussed maritime security comprehensively during India\u2019s presidency in 2021. It is also actively engaging in cooperation with navies of other littoral states, as well as of powers with interests in the region. The Indian Ocean Naval Symposium, Information Fusion Centre and\nvarious joint exercises are emblematic of the same. India has proved its reliability as a first responder in many situations needing urgent humanitarian assistance - during disasters or dealing with piracy, emerging as a \u2018net security provider\u2019. One of the strongest pillars of India\u2019s policy towards the Indo-Pacific is collaboration with like-minded partners, through fora such as the Forum for India-Pacific Islands Cooperation, the Indo-Pacific Economic Framework (IPEF), mini-laterals such as the Quad, or even at a bilateral level such as with France, Germany, Spain and Greece.\nLike India, many States have brought out their national strategies or guidelines with respect to the Indo-Pacific, notably, France, Germany and Italy. The EU also released its Indo-Pacific Strategy in 2021, with a focus on seven priority areas of sustainable and inclusive prosperity, green transition, ocean governance, digital governance and partnerships, connectivity, security and defence, and human security, which echo the policy goals of India. India welcomes the EU\u2019s decision to engage more in the Indo-Pacific region, including with partners such as the ASEAN; with Japan, Republic of Korea through Security and Defence Partnerships; and connectivity projects such as the Global Gateway. This holds even greater significance, when the foundational approaches of India and the EU towards the Indo-Pacific are coherent. Both India and the EU seek to keep the oceans peaceful, open, and secure, and at the same time, contribute to conserve its resources and keep it clean.\nIn the twenty years of the strategic partnership, India and the EU have come a long way. We have already shown our commitment to the region through our Maritime Dialogues. The maritime domain is one of the three avenues in the EU\u2019s Strategic Compass where it identifies itself working closely with India. While sharing a commitment towards security of the region, India and the EU are deepening their maritime security partnership. The first joint exercise in the Gulf of Guinea in 2023, the recent visit of Indian officials to the Naval Force Operation ATALANTA headquarters in Rota, ATALANTA\u2019s kinetic engagement with the Indian Navy as well as, numerous joint workshops to foster maritime security are noteworthy in this regard. Additionally, cooperation on non-traditional security threats, including piracy, trafficking and cyber related issues is also underway. Through the India-EU Connectivity Partnership adopted in 2021, both India and the EU aim to establish transparent, viable, inclusive and sustainable connectivity in the region through a rules based approach, and which caters to the local needs. The recently signed India-Middle East Economic Corridor stands as a testimony to not just our mutual focus on connectivity, but also aligns with the broad geographical understanding of the region that India and the EU have. The two also recognise the need for sustainable development and sound marine ecology. Notably, expansion of cooperation in the region was also reiterated in the Leaders\u2019 Statement post the College of Commissioners\u2019 Visit. While India welcomed the EU\u2019s joining of the Indo-Pacific Oceans Initiative and of the Indian Ocean Rim Association as a dialogue partner, both sides also committed to explore trilateral co-operation in the region.\nMaritime winds and waves have supported not just economic activities across the Indian Ocean, but have also carried cultural rhythms from India, in the east till the Hindu temples of Bali, and across the cotton route to Europe towards west. Amidst its emergence as a critical theatre for geopolitical competition, the Indian Ocean offers a reminder of its old legacy of a zone of syncretism and openness and an ecosystem of people, culture and commerce. Symbolising both, an ethical framework to resolve conflicts through the spread of Buddhism, as well as concepts of freedom of high seas and continental security, in the policies of the Cholas of medieval Southern India, the Indo-Pacific region provides pertinent lessons.\nIn 2022, at the Indo-Pacific Forum in Paris, External Affairs Minister Dr. S. Jaishankar had appreciated the enormous contribution that Europe can make to world affairs with its \u2018considered voice and mature capabilities\u2019. As political democracies, market economies and pluralistic societies based on democratic principles, the Indo-Pacific is certainly a zone of more collaboration for India and the EU."

    data: dict = {
        "claim": "a publishable news article",
        "content": content,
        "iterations": 3,
        "tasks": [
            {
                "task": "Rephrase the introduction to clearly state the article's purpose and the importance of the India-EU partnership.",
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