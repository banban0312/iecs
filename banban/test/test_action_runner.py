from banban.domain.contexts import TaskContext
from banban.domain.state import DialogueState
from banban.infrastructure.http_util import init_http_client
from banban.task.action.base import ActionResult
from banban.task.action.builder import build_action_runner
from banban.task.action.runner import ActionCall

async def test():

    # 【FlowExecutor的外层循环中】
    # 1.准备测试数据
    action_call = ActionCall(
        action_name="action_response",
        action_args={
            "mode":"static",
            "text":"你好，你的编号为{{slots.order_number}}的订单已经发货"
        }
    )

    state = DialogueState(sender_id='u1001')
    state.active_task = TaskContext(
        flow_id="****",
        step_id="****",
        slots={
            "order_number": "B20260409001"
        }
    )

    # 2.创建ActionRunner实例
    runner = build_action_runner()

    # 3.初始化http_client
    init_http_client()

    # 4. 通过runner执行Action类
    result:ActionResult = await runner.execute_action(action_call, state)

    # 5.打印Action执行之后返回的结果
    print(result.messages)
    print(result.slot_updates)




if __name__ == '__main__':
    import asyncio
    asyncio.run(test())
