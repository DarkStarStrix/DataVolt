import requests
import pandas as pd

def scrape_reddit_json(subreddit, limit=50):
    url = f"https://old.reddit.com/r/{subreddit}.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    posts = []
    after = None

    while len(posts) < limit:
        params = {'limit': 100, 'after': after}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Error:", response.status_code)
            break

        data = response.json()
        children = data['data'].get('children', [])
        if not children:
            break

        for child in children:
            post_data = child['data']
            posts.append({
                'title': post_data.get('title'),
                'author': post_data.get('author'),
                'score': post_data.get('score'),
                'num_comments': post_data.get('num_comments'),
                'created_utc': post_data.get('created_utc')
            })
            if len(posts) >= limit:
                break

        after = data['data'].get('after')
        if not after:
            break

    return pd.DataFrame(posts)

def save_data(df, filename):
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    df = scrape_reddit_json("dataengineering", limit=50)
    save_data(df, "dataengineering_posts.csv")
    print(df)

