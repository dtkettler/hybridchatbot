import unittest
import json

from gpt import GPT
from cli import run_llm


model = GPT("gpt-3.5-turbo")
with open("schema.json") as f:
    schema = json.load(f)

class TestGPTResponses(unittest.TestCase):
    def test_nonsense(self):
        history = [{'assistant': 'Hello. Would you like to check order status or file an RMA?', 'user': 'Hello'}]
        output = run_llm(model, schema, "Scooby Doo where are you", history)
        self.assertEqual(output, {'do_not_understand': True})

    def test_order_status(self):
        history = [{'assistant': 'Hello. Would you like to check order status or file an RMA?', 'user': 'Hello'}]
        output = run_llm(model, schema, 'Order status', history)
        self.assertEqual(output, {'order_status': True})

    def test_order_number(self):
        history = [{'assistant': 'Hello. Would you like to check order status or file an RMA?', 'user': 'Hello'},
                   {'assistant': 'Do you have your order number?', 'user': 'Order status'}]
        output = run_llm(model, schema, "It's 12347", history)
        self.assertEqual(output, {'has_order_number': True, 'order_number': '12347', 'order_status': True})

    def test_not_have_number(self):
        history = [{'assistant': 'Hello. Would you like to check order status or file an RMA?', 'user': 'Hello'},
                   {'assistant': 'Do you have your order number?', 'user': 'Order status'},
                   {'assistant': 'Sorry but I could not find that order number\nWhat is your order number?', 'user': "It's 12347"}]
        output = run_llm(model, schema, "I don't have my order number", history)
        self.assertEqual(output, {'has_order_number': False, 'order_status': True})

    def switch_to_rma(self):
        history = [{'assistant': 'Hello. Would you like to check order status or file an RMA?', 'user': 'Hello'},
                   {'assistant': 'Do you have your order number?', 'user': 'Order status'},
                   {'assistant': 'Sorry but I could not find that order number\nWhat is your order number?', 'user': "It's 12347"},
                   {'assistant': 'Your recent orders:\nOrder Number\tDate\n12345\t\t\t4/20/2024\n12346\t\t\t5/2/2024\nWhat is your order number?', 'user': "I don't have my order number"},
                   {'assistant': 'Status of order number 12345: delivered\nIs there anything else?', 'user': '12345'}]
        output = run_llm(model, schema, 'Could I start an RMA for that order', history)
        self.assertEqual(output, {'has_order_number': True, 'order_number': '12345', 'rma': True})

if __name__ == '__main__':
    unittest.main()
