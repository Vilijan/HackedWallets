from pydantic import BaseModel


class PaymentTransaction(BaseModel):
    tx_id: str
    sender: str
    receiver: str
    time: int
    block: int
    amount: float

    @staticmethod
    def init_from_payment_transaction(transaction: dict):
        if transaction['tx-type'] != 'pay':
            raise NotImplementedError

        return PaymentTransaction(tx_id=transaction['id'],
                                  sender=transaction['sender'],
                                  receiver=transaction['payment-transaction']['receiver'],
                                  time=transaction['round-time'],
                                  block=transaction['confirmed-round'],
                                  amount=transaction['payment-transaction']['amount'] / 1e6)


class AccountInfo(BaseModel):
    account: str
    created_block: int
    amount: float
    block: int

    @staticmethod
    def init_from_account_info(response: dict):
        return AccountInfo(account=response['account']['address'],
                           created_block=response['account']['created-at-round'],
                           amount=response['account']['amount'] / 1e6,
                           block=response['account']['round'])


class HackedTransaction(BaseModel):
    tx_id: str
    sender: str
    receiver: str
    amount: float
    amount_percent: float
    block: int
    time: int
    sender_created_block: int
    receiver_created_block: int
