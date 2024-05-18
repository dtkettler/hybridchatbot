from llm_selector import get_llm


def run(runner, schema, messages):
    llm_control = get_llm()

    state = {"complete": False}

    function = {"name": "get_parameters",
                "description": "Based on the user input output the appropriate parameters",
                "parameters": schema}

    while not state["complete"]:
        #for message in messages.get_latest():
        #    print(message)
        print(messages.get_latest())
        user_prompt = input("> ")
        messages.add_user(user_prompt.strip())

        output = llm_control.run_llm_with_history("You are interpreting the user's commands and outputing the appropriate JSON object",
                                                  user_prompt, messages.get_formatted(), temperature=0.2, functions=[function])
        print(output)

        runner.run(output)
