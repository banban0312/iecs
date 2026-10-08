from typing import List

from banban.knowledge.providers import KnowledgeProvider, ProductAPIProvider, OrderAPIProvider, FAQProvider, RAGProvider


class KnowledgeProviderRegistry:

    def __init__(self, providers: List[KnowledgeProvider] ):
        self.provider = { p.provider_id: p for p in providers }

    def get(self, provider_id:str)->KnowledgeProvider:
        return self._providers[provider_id]

if __name__ == '__main__':
    registry = KnowledgeProviderRegistry([
        ProductAPIProvider(),
        OrderAPIProvider(),
        FAQProvider(),
        RAGProvider()
    ])

    provider = registry.get("api.order")
    print(type(provider))