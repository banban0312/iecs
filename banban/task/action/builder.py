import importlib
import inspect
import pkgutil

from banban.task.action.base import Action
from banban.task.action.builtin.action_listen import ActionListen
from banban.task.action.builtin.action_response import ActionResponse
from banban.task.action.registry import ActionRegistry
from banban.task.action.runner import ActionRunner


def register_custom_actions(registry: ActionRegistry):
    # 完成自定义Action类的注册
    # 1.导入banban.task.action.custom包
    package = importlib.import_module("banban.task.action.custom")
    # 2.遍历包中的所有模块
    for __,name,is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        if is_pkg:
            continue
        # 导入custom包中的模块
        module = importlib.import_module(name)
        # 3.获取模块中的所有类
        for __,obj in inspect.getmembers(module,inspect.isclass):
            # 如果模块中的类是Action的子类，但不是Action类，则进行注册
            if issubclass(obj,Action) and obj is not Action:
                registry.register( obj() )


def register_builtin_actions(registry: ActionRegistry):
    registry.register(ActionResponse())
    registry.register(ActionListen())


def build_action_runner()->ActionRunner:
    registry = ActionRegistry()
    # 注册内置Action（静态注册）
    register_builtin_actions(registry)
    # 注册自定义Action（通过扫描包来完成自定义Action的注册）
    register_custom_actions(registry)
    return ActionRunner(registry)

if __name__ == '__main__':
    runner = build_action_runner()
    print(type(runner.registry.get("test_action")))