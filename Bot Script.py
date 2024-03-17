import time
import tweepy
import requests
from fuzzywuzzy import fuzz
from pycoingecko import CoinGeckoAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import threading
cg = CoinGeckoAPI(api_key='')
api_key = ""
api_secret = ""
bearer_token = r""
access_token = ""
access_token_secret = ""

client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

Chrome_options = webdriver.ChromeOptions()
Chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=Chrome_options)
 
last_replied_id = None

def get_mentioned_tweets():
    global last_replied_id
    my_headers = {'Authorization' : 'Bearer AAAAAAAAAAAAAAAAAAAAABySnwEAAAAAzFQ%2Bh04AKHpS%2F7YcJzRBQqNqVBk%3DBFJ3lXqY13TvmVPXwWKTc8YGkISNfK4tjcAz7SiS3uHzwgLKKo'}
    url = 'https://api.twitter.com/2/users/1664004857374601216/mentions'
    if last_replied_id:
        url += f'?since_id={last_replied_id}'
    response = requests.get(url, headers=my_headers)
    if response.status_code == 200:
        responseObj = response.json()
        if 'data' in responseObj:
            tweets = responseObj['data']
            new_tweets = []
            for tweet in tweets:
                if tweet['id'] != last_replied_id:
                    new_tweets.append(tweet)
            if tweets:
                last_replied_id = tweets[0]['id']
            return new_tweets
        else:
            print("Error: No data key in response.")
    else:
        print(f"Error: Status code {response.status_code} returned from API.")

def process_mention(tweet):
    if '@chartthisbart' in tweet['text']:
        content = tweet['text'].split('@chartthisbart', 1)[1].strip()
        tweet_id = tweet['id']
        print("Tweet ID:", tweet_id)
        print("Content:", content)

        available_coins = cg.get_coins_list()

        best_match = None
        best_match_ratio = 0

        for coin in available_coins:
            coin_name = coin['name']
            match_ratio = fuzz.ratio(content.lower(), coin_name.lower())
            if match_ratio > best_match_ratio:
                best_match = coin
                best_match_ratio = match_ratio

        if best_match:
            print('best match', best_match)

            Chrome_options = webdriver.ChromeOptions()
            Chrome_options.add_argument("--headless")

            driver = webdriver.Chrome(options=Chrome_options)

            url = f"http://146.190.34.5/coin/{best_match['name']}"

            try:
                # Navigate to the URL
                driver.get(url)
                print("Navigated to:", url)

                def check_condition():
                    try:
                        driver.find_element(By.XPATH, "//div[@id='WS1']")
                        return True
                    except NoSuchElementException:
                        return False

                # Continuously check for the condition until it becomes true
                while not check_condition():
                    time.sleep(1)  # Adjust the time interval as needed

                div_element = driver.find_element(By.XPATH, "//div[@id='WS1']")
                screenshot_path = f"screenshot_{tweet_id}.png"
                div_element.screenshot(screenshot_path)

                # Close the WebDriver instance
                driver.quit()

                print("Screenshot saved as:", screenshot_path)

                # Upload the screenshot and reply
                with open(screenshot_path, "rb") as media_file:
                    media = api.media_upload(screenshot_path, file=media_file)

                client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
                client.create_tweet(in_reply_to_tweet_id=tweet_id, media_ids=[media.media_id])

                print("Media upload successful. Media ID:", media.media_id)
                print("Replied successfully to tweet:", tweet_id)

            except Exception as e:
                print(f"Error processing tweet {tweet_id}: {str(e)}")

            finally:
                # Make sure to quit the WebDriver in case of an exception
                driver.quit()


if __name__ == "__main__":
    while True:
        new_mentions = get_mentioned_tweets()
        if new_mentions:
            print("New mentioned tweets:")
            for tweet in new_mentions:
                # Call the process_mention function for each mentioned tweet
                process_thread = threading.Thread(target=process_mention, args=(tweet,))
                process_thread.start()
        else:
            print("No new mentioned tweets found.")
        time.sleep(60)
