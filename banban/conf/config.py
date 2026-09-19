"""
配置模块：集中管理项目运行所需的全局配置项。

本模块基于 pydantic-settings 定义 Settings 类，从项目根目录下的 .env
文件读取配置，并以全局单例 settings 的形式对外暴露。
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    配置类：基于 pydantic-settings 的 BaseSettings，用于声明并加载项目配置项。

    每个类属性对应一个环境变量，字段类型由类型注解决定，
    配置来源为项目根目录下的 .env 文件。
    """
    model_config = SettingsConfigDict(
        env_file = Path(__file__).parents[2] / ".env" , # 指向项目根目录的 .env
        env_file_encoding = "utf-8" ,                   # .env 文件编码
        extra = 'ignore' ,                              # 忽略 .env 中多余的键(适合临时传入少量参数测试)
    )

    llm_model : str
    llm_base_url : str
    llm_api_key : str

    commerce_api_base_url : str

    database_url : str

    app_host : str
    app_port : int

# 创建全局单例 settings，供全项目导入使用
settings = Settings()