from durable.lang import *
from durable.engine import MessageNotHandledException, MessageObservedException
import logging


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)


class RuleRunner:
    def __init__(self, ruleset_name):
        self.ruleset_name = ruleset_name

    def run(self, output):
        #existing_facts = get_facts(self.ruleset_name)
        #facts = []
        #for key, val in output.items():
        #    skip = False
        #    for fact in existing_facts:
        #        if key in fact and fact[key] == val:
        #            skip = True
        #    if not skip:
        #        facts.append({key: val})

        try:
            #assert_fact(self.ruleset_name, {key: val})
            #assert_facts(self.ruleset_name, facts)
            #state = get_state(self.ruleset_name)
            #state["status"] = "go"
            #update_state(self.ruleset_name, state)
            post(self.ruleset_name, output)
        except MessageNotHandledException as error:
            logging.error(error)
            pass
        except MessageObservedException as error:
            pass
