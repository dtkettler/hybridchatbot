import logging
from durable.lang import *


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

# This is obviously fake data, in a real use case it should be tied to a database or something
orders = [
    {"order_num": '12345', "status": "delivered", "date": "4/20/2024"},
    {"order_num": '12346', "status": "out for delivery", "date": "5/2/2024"}
]
def make_ruleset(rset, messages):
    def duplicate_fact(fact, to_exclude=[]):
        new_fact = {}
        for key, val in fact.items():
            if key != 'sid' and key not in to_exclude:
                new_fact[key] = val
        return new_fact

    with ruleset(rset):
        @when_all(s.status == "start")
        def start(c):
            messages.add_system("Hello. Would you like to check order status or file an RMA?")
            c.s.status = "wait"

        @when_all(pri(0), c.first << (m.order_status == True) & -m.order_status_requirements_set)
        def set_order_status_requirements(c):
            logging.debug("Rule: set_order_status_requirements")
            fact = duplicate_fact(c.first)
            fact["needs_has_order_number"] = True
            fact["display_order_status"] = True
            fact["order_status_requirements_set"] = True
            c.post(fact)

        @when_all(pri(0), c.first << (m.rma == True) & -m.rma_requirements_set)
        def set_rma_requirements(c):
            logging.debug("Rule: set_rma_requirements")
            fact = duplicate_fact(c.first)
            fact["needs_has_order_number"] = True
            fact["display_rma"] = True
            fact["rma_requirements_set"] = True
            c.post(fact)

        @when_all(pri(0), c.first << (m.has_order_number == True) & -m.order_number_requirements_set)
        def set_order_number_requirements(c):
            logging.debug("Rule: set_order_number_requirements")
            fact = duplicate_fact(c.first)
            fact["needs_order_number"] = True
            fact["order_number_requirements_set"] = True
            c.post(fact)

        @when_all(pri(0), c.first << (m.has_order_number == False) & -m.no_order_number_requirements_set)
        def set_no_order_number_requirements(c):
            logging.debug("Rule: set_no_order_number_requirements")
            fact = duplicate_fact(c.first)
            fact["display_recent_orders"] = True
            fact["needs_order_number"] = True
            fact["no_order_number_requirements_set"] = True
            c.post(fact)

        @when_all(pri(20),
                  #(s.status == "go"),
                  c.first << +m.needs_has_order_number & -m.has_order_number)
        def has_order_number(c):
            logging.debug("Rule: has_order_number")
            messages.add_system("Do you have your order number?")
            c.s.status = "wait"

        @when_all(pri(10),
                  #(s.status == "go"),
                  c.first << +m.needs_order_number & -m.order_number)
        def order_number(c):
            logging.debug("Rule: order_number")
            messages.add_system("What is your order number?")
            c.s.status = "wait"

        @when_all(pri(5),
                  c.first << +m.display_recent_orders & -m.recent_orders_displayed)
        def display_recent_orders(c):
            messages.add_system("Your recent orders:")
            messages.add_system("Order Number\tDate")
            for order in orders:
                messages.add_system("{}\t\t\t{}".format(order["order_num"], order["date"]))
            fact = duplicate_fact(c.first)
            fact["recent_orders_displayed"] = True
            c.post(fact)

        @when_all(pri(1),
                  #(s.status == "go"),
                  c.first << +m.display_order_status & +m.order_number)
        def display_status(c):
            order_number = c.first.order_number
            order = next((x for x in orders if x['order_num'] == order_number), None)

            if order:
                messages.add_system("Status of order number {}: {}".format(order_number, order["status"]))
                messages.add_system("Is there anything else?")
                c.s.status = "wait"
            else:
                messages.add_system("Sorry but I could not find that order number")
                c.post(duplicate_fact(c.first, ["order_number"]))

        @when_all(pri(1),
                  c.first << +m.display_rma & +m.order_number)
        def display_rma(c):
            order_number = c.first.order_number
            order = next((x for x in orders if x['order_num'] == order_number), None)

            if order:
                if order["status"] == "delivered":
                    messages.add_system("Starting RMA process for order {}...".format(order_number))
                else:
                    messages.add_system("Sorry but you can't start an RMA request for an order that has not been delivered yet.")

                messages.add_system("Is there anything else?")
            else:
                messages.add_system("Sorry but I could not find that order number")
                c.post(duplicate_fact(c.first, ["order_number"]))

        @when_all(pri(100),
                  m.do_not_understand == True)
        def did_not_understand(c):
            messages.add_system("Sorry but I did not understand that.")

    update_state(rset, {"status": "start"})


if __name__ == "__main__":
    from messages import Messages
    msg = Messages()
    make_ruleset("test", msg)

    print(msg.get_latest())

    post("test", {'order_status': True})
    #state = get_state("test")
    #state["status"] = "go"
    #update_state("test", state)
    print(msg.get_latest())

    post("test", {'order_status': True, 'has_order_number': True})
    #state = get_state("test")
    #state["status"] = "go"
    #update_state("test", state)
    print(msg.get_latest())

    #facts = get_facts("test")
    #retract_facts("test", facts)

    post("test", {'order_status': True, 'has_order_number': True, "order_number": "12347"})
    #facts = get_facts("test")
    #state = get_state("test")
    #state["status"] = "go"
    #update_state("test", state)
    print(msg.get_latest())

    post("test", {'order_status': True, 'has_order_number': False})
    print(msg.get_latest())

    post("test", {'order_status': True, 'has_order_number': True, "order_number": "12345"})
    print(msg.get_latest())

    post("test", {'rma': True, 'has_order_number': True, "order_number": "12345"})
    print(msg.get_latest())

