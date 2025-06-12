class Scenario:
    def __init__(self, px: float, nt: int, exchange_rate_variation: float, oil_price_variation: float,
                 port_call_price_variation: float, intermodal_price_variation: float, demand_variation: float,
                 freight_variation: float):
        self.px = px
        self.nt = nt
        self.exchange_rate_variation = exchange_rate_variation
        self.oil_price_variation = oil_price_variation
        self.port_call_price_variation = port_call_price_variation
        self.intermodal_price_variation = intermodal_price_variation
        self.demand_variation = demand_variation
        self.freight_variation = freight_variation
        self.name = f"Scenario_{px}_{nt}_{exchange_rate_variation}_{oil_price_variation}_{port_call_price_variation}_{intermodal_price_variation}_{demand_variation}_{freight_variation}"
        self.description = f"PX: {px}, NT: {nt}, Exchange Rate Variation: {exchange_rate_variation}, Oil Price Variation: {oil_price_variation}, \
Port Call Price Variation: {port_call_price_variation}, Intermodal Transport Price Variation: {intermodal_price_variation}, \
Demand Variation: {demand_variation}, Freight Variation: {freight_variation}"

    def __repr__(self):
        return f"Scenario(name={self.name}, description={self.description})"