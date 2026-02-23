# qaai_system/brokers/dhan_live.py #
class DhanBrokerLive:
    def __init__(self, api_key: str, secret: str, base_url: str):
        self.api_key = api_key
        self.secret = secret
        self.base_url = base_url
        # TODO: session, auth headers

    def place_order(
        self,
        symbol: str,
        side: str,
        qty: int,
        order_type: str,
        limit_price=None,
        tif="DAY",
    ) -> str:
        # TODO: call REST; return broker order id
        raise NotImplementedError

    def fetch_order(self, order_id: str) -> dict:
        # TODO: poll order; map fields to normalized schema
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError

    def positions(self) -> list:
        raise NotImplementedError

    def account(self) -> dict:
        raise NotImplementedError
