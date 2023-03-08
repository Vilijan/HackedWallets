import pandas as pd

POTENTIAL_WRONG_TRANSACTIONS = [
    "L4EWVCGIQKMF7KS3NLWJH4W2SNSQ3VF3ATCKDRIZNCJQC65LNDPA"
]

df = pd.read_csv('hack_transactions.csv')

df = df[~df.tx_id.isin(POTENTIAL_WRONG_TRANSACTIONS)].reset_index(drop=True)

print(f'Total Hacked Volume: {int(df.amount.sum()):,} ALGO')
print(f'Median per transaction: {int(df.amount.median()):,} ALGO')
print(f'Mean per transaction: {int(df.amount.mean()):,} ALGO')
print(f'Unique Hacked Wallets: {len(df.receiver.unique()):,}')

# 1. Transactions Per Hour

txns_per_hour = df.groupby(['hour'])['count'].sum()

for hour, total_transactions in txns_per_hour.items():
    print(f'Hour: {hour} \t Total Transactions: {total_transactions}')

# 2. Amount Per Hour
amount_per_hour = df.groupby(['hour'])['amount'].sum()

for hour, total_amount in amount_per_hour.items():
    print(f'Hour: {hour} \t Total Amount: {int(total_amount):,}')


# Buckets

def map_amount_to_bucket(amount: float) -> str:
    if amount < 1000:
        return "[0, 1000)"

    if 1000 <= amount < 5000:
        return "[1000, 5,000)"

    if 5000 <= amount < 10000:
        return "[5,000, 10,000)"

    if 10000 <= amount < 50000:
        return "[10,000, 50,000)"

    if 50000 <= amount < 100000:
        return "[50,000, 100,000)"

    return "[100,000, +)"


df['bucket'] = df.amount.apply(lambda x: map_amount_to_bucket(amount=x))

# 3. Transactions per bucket

txns_per_bucket = df.groupby(['bucket'])['count'].sum()

for bucket, total_transactions in txns_per_bucket.items():
    print(f'Bucket: {bucket} \t Total Transactions: {total_transactions}')

# 4. Volume per bucket
amount_per_bucket = df.groupby(['bucket'])['amount'].sum()

for bucket, total_amount in amount_per_bucket.items():
    print(f'Bucket: {bucket} \t Total Amount: {int(total_amount):,}')
