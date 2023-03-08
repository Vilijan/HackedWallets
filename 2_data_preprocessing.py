import pandas as pd
from typing import List
from datetime import datetime

import algosdk
from utils.models import HackedTransaction, AccountInfo
from utils.utils import load_json
from tqdm import tqdm

HACKED_TRANSACTIONS_JSON_PATH = 'hacked_transactions.json'

headers = {
    "User-Agent": "Python3",
}

client: algosdk.v2client.indexer.IndexerClient = algosdk.v2client.indexer.IndexerClient(indexer_token="",
                                                                                        indexer_address="https://mainnet-idx.algonode.cloud",
                                                                                        headers=headers)

hacked_transactions: List[HackedTransaction] = [
    HackedTransaction(**txn) for txn in load_json(HACKED_TRANSACTIONS_JSON_PATH)['list']
]

df_data = []

for transaction in hacked_transactions:
    df_data.append(list(transaction.dict().values()))

df_columns = list(hacked_transactions[0].dict().keys())

df = pd.DataFrame(data=df_data,
                  columns=df_columns)

df['day'] = [datetime.fromtimestamp(time).strftime("%m/%d/%Y") for time in df.time.values]
df['hour'] = [datetime.fromtimestamp(time).strftime("%m/%d/%Y %H CEST") for time in df.time.values]
df['count'] = 1

# Retrieve receivers ALGO balance
wallet_to_algos = {}

for wallet in tqdm(df.receiver.unique()):
    receiver_info_response = client.account_info(address=wallet)

    receiver_account_info = AccountInfo.init_from_account_info(response=receiver_info_response)

    wallet_to_algos[wallet] = receiver_account_info.amount

df['receiver_amount'] = [wallet_to_algos[wallet] for wallet in df.receiver.values]
df['amount_difference'] = [abs(arr[0] - arr[1]) for arr in df[['amount', 'receiver_amount']].values]

print(f'All potential hack transactions: {len(df)}')

potential_hack_transactions_df = df[df.amount_difference < 1].reset_index(drop=True)

print(f'Potential hack transactions without moving receiver funds: {len(potential_hack_transactions_df)}')

potential_hack_transactions_df.to_csv('hack_transactions.csv', index=False)