import algosdk
from utils.models import HackedTransaction, AccountInfo, PaymentTransaction
from typing import List, Optional
from utils.utils import load_json, save_json, save_list
import time


def is_hacked_transaction(payment_transaction: PaymentTransaction,
                          sender_account_info_before: AccountInfo,
                          receiver_account_info: AccountInfo) -> bool:
    amount_percent_sent = round(payment_transaction.amount / sender_account_info_before.amount * 100, 2)

    # If the hacker send more than 90% of the funds and it used a completely new wallet.
    if amount_percent_sent > 90 and receiver_account_info.created_block == payment_transaction.block:
        return True

    return False


def retrieve_hacked_transaction(payment_transaction: PaymentTransaction,
                                indexer: algosdk.v2client.indexer.IndexerClient) -> Optional[HackedTransaction]:
    sender_info_response = indexer.account_info(address=payment_transaction.sender,
                                                block=payment_transaction.block - 1)

    sender_account_info_before = AccountInfo.init_from_account_info(response=sender_info_response)

    receiver_info_response = indexer.account_info(address=payment_transaction.receiver)

    receiver_account_info = AccountInfo.init_from_account_info(response=receiver_info_response)

    is_hacked = is_hacked_transaction(payment_transaction=payment_transaction,
                                      sender_account_info_before=sender_account_info_before,
                                      receiver_account_info=receiver_account_info)

    if not is_hacked:
        return None

    amount_percent_sent = round(payment_transaction.amount / sender_account_info_before.amount * 100, 2)

    return HackedTransaction(tx_id=payment_transaction.tx_id,
                             sender=payment_transaction.sender,
                             receiver=payment_transaction.receiver,
                             amount=payment_transaction.amount,
                             amount_percent=amount_percent_sent,
                             block=payment_transaction.block,
                             time=payment_transaction.time,
                             sender_created_block=sender_account_info_before.created_block,
                             receiver_created_block=receiver_account_info.created_block)


def retrieve_block_payment_transactions(indexer: algosdk.v2client.indexer.IndexerClient,
                                        block: int,
                                        limit: int = 3000) -> List[PaymentTransaction]:
    curr_block = indexer.health()['round']

    if block > curr_block:
        raise NotImplementedError

    next_token = None
    payment_transactions: List[PaymentTransaction] = []

    while True:
        if next_token is None:
            round_transactions = indexer.search_transactions(round_num=block,
                                                             limit=limit)
        else:
            round_transactions = indexer.search_transactions(round_num=block,
                                                             limit=limit,
                                                             next_page=next_token)

        next_token = round_transactions.get("next-token", -1)

        if next_token == -1:
            break

        if len(round_transactions["transactions"]) == 0:
            break

        for txn in round_transactions["transactions"]:
            try:
                payment_transaction = PaymentTransaction.init_from_payment_transaction(transaction=txn)
                payment_transactions.append(payment_transaction)
            except:
                pass

    return payment_transactions


headers = {
    "User-Agent": "Python3",
}

client: algosdk.v2client.indexer.IndexerClient = algosdk.v2client.indexer.IndexerClient(indexer_token="",
                                                                                        indexer_address="https://mainnet-idx.algonode.cloud",
                                                                                        headers=headers)

curr_block = load_json('block.json')['block']

hacked_transactions_json = load_json('hacked_transactions.json')

hacked_transactions: List[HackedTransaction] = [
    HackedTransaction(**txn) for txn in hacked_transactions_json['list']
]

while True:
    block_payment_transactions: List[PaymentTransaction] = []
    try:
        block_payment_transactions = retrieve_block_payment_transactions(indexer=client,
                                                                         block=curr_block)
    except:
        time.sleep(15)

    for payment_transaction in block_payment_transactions:
        if payment_transaction.amount < 100:
            continue

        try:
            hacked_transaction = retrieve_hacked_transaction(payment_transaction=payment_transaction,
                                                             indexer=client)
            if hacked_transaction is not None:
                hacked_transactions.append(hacked_transaction)
        except:
            pass

    curr_block += 1

    save_list('hacked_transactions.json', hacked_transactions)
    save_json('block.json', {'block': curr_block})
