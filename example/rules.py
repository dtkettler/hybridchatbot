from durable.lang import *


# This is obviously fake data, in a real use case it should be tied to a database or something
orders = [
    {"order_num": '12345', "status": "delivered"},
    {"order_num": '12346', "status": "out for delivery"}
]
def make_ruleset(rset, messages):
    with ruleset(rset):
        @when_all(s.status == "start")
        def start(c):
            messages.add_system("Hello. Would you like to check order status or file an RMA?")
            c.s.status = "wait"

        @when_all(m.order_status == True)
        def set_order_status_requirements(c):
            c.s.needs_has_order_number = True
            c.s.needs_order_number = True
            c.s.display_order_status = True

        @when_all(m.rma == True)
        def set_rma_requirements(c):
            c.s.needs_has_order_number = True
            c.s.needs_order_number = True
            c.s.display_rma = True

        @when_all(pri(20),
                  (s.status == "go") & +s.needs_has_order_number,
                  -m.has_order_number)
        def has_order_number(c):
            messages.add_system("Do you have your order number?")
            c.s.status = "wait"

        @when_all(pri(10),
                  (s.status == "go") & +s.needs_order_number,
                  -m.order_number, m.has_order_number == True)
        def order_number(c):
            messages.add_system("What is your order number?")
            c.s.status = "wait"

        @when_all(pri(1),
                  (s.status == "go") & +s.display_order_status,
                  c.first << +m.order_number)
        def display_status(c):
            order_number = c.first.order_number
            #order = next((x for x in orders if x['order_num'] == c.m.order_number), None)
            order = None
            for o in orders:
                if o['order_num'] == order_number:
                    order = o
                    break

            if order:
                messages.add_system("Status of order number {}: {}".format(order_number, order["status"]))
                c.s.status = "wait"
            else:
                messages.add_system("Sorry but I could not find that order number")
                #c.delete_state(rset)
                #c.s.status = "wait"
                to_retract = []
                for fact in c.get_facts():
                    if "has_order_number" in fact or "order_number" in fact:
                        #c.retract_fact(rset, fact)
                        to_retract.append(fact)
                c.retract_facts(to_retract)
                #c.s.status = "go"

    update_state(rset, {"status": "start"})


if __name__ == "__main__":
    from messages import Messages
    msg = Messages()
    make_ruleset("test", msg)

    print(msg.get_latest())

    post("test", {'order_status': True})
    state = get_state("test")
    state["status"] = "go"
    update_state("test", state)
    print(msg.get_latest())

    assert_fact("test", {'has_order_number': True})
    state = get_state("test")
    state["status"] = "go"
    update_state("test", state)
    print(msg.get_latest())

    assert_fact("test", {"order_number": "12345"})
    state = get_state("test")
    state["status"] = "go"
    update_state("test", state)
    print(msg.get_latest())

