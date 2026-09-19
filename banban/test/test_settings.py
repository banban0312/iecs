"""
测试 conf/config.py 文件：用于验证配置模块能否正常加载与读取。

本模块导入 settings 对象，并打印其中的 llm_model 配置项，
以确认配置来源（环境变量 / .env / 默认值）已正确生效。
"""
from banban.conf.config import settings

if __name__ == '__main__':
    # 打印配置项 llm_model，验证配置是否加载成功
    print(settings.llm_model)