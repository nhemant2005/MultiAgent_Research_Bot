from src.agents.agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, reviser_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    print("\n"+" ="*50)
    print("Step 1 = search agent is working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state['search_results'] = search_result['messages'][-1].content

    #print("\n search result",state['search_results'])


    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    #print("\nscraped content: \n", state['scraped_content'])


    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n"+" ="*50)
    print("step 4 - Critic is reviewing the draft ...")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n Critic Feedback\n", state['feedback'])

    print("\n"+" ="*50)
    print("step 5 - Writer is revising based on feedback ...")
    print("="*50)

    state["revised_report"] = reviser_chain.invoke({
        "topic": topic,
        "report": state['report'],
        "feedback": state['feedback']
    })

    print("\n Final Revised Report\n", state['revised_report'])

    return state


