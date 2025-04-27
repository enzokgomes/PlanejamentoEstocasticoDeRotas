class Scenario:
    def __init__(self, px: float, nt: int, exchange_rate_variation: float, oil_price_variation: float):
        self.px = px
        self.nt = nt
        self.exchange_rate_variation = exchange_rate_variation
        self.oil_price_variation = oil_price_variation
        self.name = f"Scenario_{px}_{nt}_{exchange_rate_variation}_{oil_price_variation}"
        self.description = f"PX: {px}, NT: {nt}, Exchange Rate Variation: {exchange_rate_variation}, Oil Price Variation: {oil_price_variation}"

    def __repr__(self):
        return f"Scenario(name={self.name}, description={self.description})"