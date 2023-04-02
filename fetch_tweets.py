import time
import asyncio
import feedparser
import httpx
from rich import print
from rich.prompt import Prompt
from rich.table import Table
from rich.console import Console

async def fetch_tweets_async(username, count=5):
    try:
        url = f"https://nitter.net/{username}/rss"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            feed = feedparser.parse(response.text)
        if feed.bozo: 
            raise Exception(f"Error fetching {username}'s tweets.")
        return feed.entries[:count]
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        return []

def display_tweets(tweets, username, show_metadata):
    console = Console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column(f"🐦‍🔥 Tweets from {username}")

    if show_metadata:
        table.add_column("Timestamp", style="dim")
        table.add_column("Link", style="dim")

    for tweet in tweets:
        if show_metadata:
            table.add_row(tweet.title, tweet.published, tweet.link)
        else:
            table.add_row(tweet.title)

    console.print(table)

async def fetch_and_display(user_list, show_metadata):
    tweet_fetch_tasks = [fetch_tweets_async(user) for user in user_list]
    fetched_tweets = await asyncio.gather(*tweet_fetch_tasks)
    total_tweets = 0

    for idx, user in enumerate(user_list):
        tweets = fetched_tweets[idx]
        total_tweets += len(tweets)
        display_tweets(tweets, user, show_metadata)
        print("\n")

    print(f"[bold green]Total tweets fetched:[/bold green] {total_tweets}")

async def main():
    user_list = ["tferriss", "paulg", "elonmusk"]

    #how frequently we want to update
    refresh_interval = int(Prompt.ask("Enter the refresh interval in minutes", default="1"))
    refresh_interval *= 60

    #metadata
    show_metadata_input = Prompt.ask("Display tweet metadata? (yes/no)", default="no")
    show_metadata = True if show_metadata_input.lower() == "yes" else False

    while True:
        await fetch_and_display(user_list, show_metadata)

        #say "add" -> vaibhavkapoor(enter)
        action = Prompt.ask("Add/Remove user, Refresh, or Quit? (add/remove/refresh/quit)", choices=["add", "remove", "refresh", "quit"])

        if action == "add":
            new_user = Prompt.ask("Enter the username to add")
            user_list.append(new_user)
            await fetch_and_display([new_user], show_metadata)
        elif action == "remove":
            remove_user = Prompt.ask("Enter the username to remove")
            if remove_user in user_list:
                user_list.remove(remove_user)
            else:
                print(f"[bold red]Error:[/bold red] {remove_user} not found in the user list.")
        elif action == "refresh":
            continue
        elif action == "quit":
            break

        time.sleep(refresh_interval)

if __name__ == "__main__":
    asyncio.run(main())