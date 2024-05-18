import json
from cli import run
from rule_runner import RuleRunner
from messages import Messages

from rules import make_ruleset


with open("schema.json") as f:
    schema = json.load(f)

messages = Messages()
make_ruleset("Ecommerce example", messages)
runner = RuleRunner("Ecommerce example")

run(runner, schema, messages)
