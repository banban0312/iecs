from typing import Dict

from banban.task.action.base import Action
from banban.task.action.builtin.action_listen import ActionListen
from banban.task.action.builtin.action_response import ActionResponse
from banban.task.action.custom.action_lookup_order_logistics import LookupOrderLogisticsAction
from banban.task.action.custom.action_lookup_order_status import LookupOrderStatusAction
from banban.task.action.custom.action_recommend_similar_products import RecommendSimilarProductsAction
from banban.task.action.custom.action_submit_refund_request import SubmitRefundRequestAction

class ActionRegistry:

    def __init__(self):
        self._actions: Dict[str, Action] = {}

    def register(self, action: Action):
        self._actions[action.name] = action

    def get(self, action_name: str) -> Action:
        if action_name not in self._actions:
            raise KeyError(f"Action '{action_name}' not found")
        return self._actions[action_name]

if __name__ == '__main__':
    registry = ActionRegistry()
    # 注册内置Action
    registry.register( ActionResponse() )
    registry.register( ActionListen() )
    # 注册自定义Action
    registry.register( LookupOrderLogisticsAction() )
    registry.register( LookupOrderStatusAction() )
    registry.register( RecommendSimilarProductsAction() )
    registry.register( SubmitRefundRequestAction() )

    # 获取Action
    action = registry.get('action_lookup_order_status')
    print(type(action))
