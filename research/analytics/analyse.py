import orjson
import pandas as pd
import matplotlib.pyplot as plt

ACDB_ID = 659179833401540644
plt.style.use('dark_background')

def combine():
    fns = [
        'botspam.json',
        'botspam2.json',
        'botspam3.json',
    ]
    combined_msgs = []
    for fn in fns:
        with open(fn, 'rb') as f:
            combined_msgs.extend(orjson.loads(f.read())['messages'])

    with open('out_merged.json', 'wb') as f:
        f.write(orjson.dumps(combined_msgs, option=orjson.OPT_INDENT_2))

#%%
def process():
    with open('out_merged.json', 'rb') as f:
        data = orjson.loads(f.read())
    df = pd.json_normalize(data)
    df = df[['id', 'type', 'timestamp', 'content', 'embeds', 'author.id', 'author.name', 'author.discriminator', 'author.nickname', 'author.isBot']]
    df.drop_duplicates(subset=['id'], inplace=True)

    # cast id to int, author.id to int, timestamp to unix timestamp
    df['id'] = df['id'].astype(pd.Int64Dtype())
    df['author.id'] = df['author.id'].astype(pd.Int64Dtype())
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    df.to_parquet('data.parquet')
    df.to_json('data.json', orient='records', indent=2)
#%%
df = pd.read_parquet('data.parquet')
df = df[df['author.id'] == ACDB_ID]
# plot time series of messages
ts_series = df.groupby(pd.Grouper(key='timestamp', freq='1D')).count()['id']
plt.plot(ts_series, lw=.5)
plt.title('Daily ACDB Responses')
plt.xlabel('Date')
# plt.show(block=True)

plt.savefig('daily_acdb_responses.png', dpi=600)

# combine()
# process()