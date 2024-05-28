import logging
from llm_selector import get_llm


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

def run_llm(llm_control, schema, user_prompt, history):
    function = {"name": "get_parameters",
                "description": "Based on the user input output the appropriate parameters",
                "parameters": schema}

    output = llm_control.run_llm_with_history("""You are interpreting the user's commands and outputing the appropriate JSON object.
Do not include any information the user has not provided and if they correct or change a response use their latest response.
""",
                                              user_prompt, history, temperature=0.2,
                                              functions=[function])

    return output

def run(runner, schema, messages):
    llm_control = get_llm()

    #function = {"name": "get_parameters",
    #            "description": "Based on the user input output the appropriate parameters",
    #            "parameters": schema}

    while True:
        #for message in messages.get_latest():
        #    print(message)
        print(messages.get_latest())
        user_prompt = input("> ")
        messages.add_user(user_prompt.strip())

        #output = llm_control.run_llm_with_history("""You are interpreting the user's commands and outputing the appropriate JSON object.
#Do not include any information the user has not provided and if they correct or change a response use their latest response.
#""",
        #                                         user_prompt, messages.get_formatted(), temperature=0.2, functions=[function])
        output = run_llm(llm_control, schema, user_prompt, messages.get_formatted())
        logging.debug(output)

        runner.run(output)
