from banban.plan.models import TurnPlan

if __name__ == '__main__':
    dict_data = {
      "task": {
        "commands": [
            {
                "command": "start_flow",
                "flow": "refund_request"
            },
            {
                "command": "set_slots",
                "slots": {
                       "order_number":"A20260001"
                 }
            },
            {
                "command": "cancel_flow"
            },
             {
                "command": "resume_flow",
                "flow": "refund_request"
            }
        ]
      },
      "knowledge": {
          "intents":["product_info", "refund_policy"]
      },
      "chitchat": {}
    }
    # 将dict_data转化成TurnPlan对象
    turn_plan:TurnPlan = TurnPlan.from_dict(dict_data)
    print(turn_plan)