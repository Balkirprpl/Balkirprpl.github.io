from keys import key, client, user_agent
from detect2 import scanAccount

import praw
import datetime
import csv
import os

reset = '\033[37m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'

file = open("database.csv", mode='a', newline='')
db = csv.writer(file)
if os.path.getsize("database.csv") == 0:
    headers = ['user_id','username','link_karma','comment_karma','created','verified','submissions','comments']
    db.writerow(headers)

import spacy

nlp = spacy.load("en_core_web_md")

def compare_text(text1, text2):
    similarity = nlp(text1).similarity(nlp(text2))
    return similarity

def check_comments(user):

    print(type(user))
    for comments in user.comments.new(limit=None):
        print(comments.body)

def add_to_db(data):
    db.writerow(data)

def display_info(user):
    #check_comments(user)
    #user = reddit.redditor(username)
    created = datetime.datetime.fromtimestamp(user.created_utc)
    created = created.strftime("%d/%m/%y")
    total_comments = 0
    comment_array = []
    for comments in user.comments.new(limit=None):
        total_comments += 1
        if total_comments <= 6 and "://www." not in comments.body:
            #print(comments.body)
            comment_array.append(comments.body)
    z = 1.0
    l = len(comment_array)
    for i1 in range(l):
        for i2 in range(i1 + 1, l):
            c1 = comment_array[i1]
            c2 = comment_array[i2]
            z *= compare_text(c1, c2)

    total_submissions = 0
    for submission in user.submissions.new(limit=None):
        total_submissions += 1
    data = [user.id,
            user.name,
            z,
            user.link_karma,
            user.comment_karma,
            user.total_karma,
            created,
            user.verified,
            total_submissions,
            total_comments]
    add_to_db(data)
    print(f"""Username: {cyan}{user.name}{reset}
Id: {green}{user.id}{reset}
Link Karma: {blue}{user.link_karma}{reset}
Comment Karma: {blue}{user.comment_karma}{reset}
Total Karma: {yellow}{user.total_karma}{reset}
Account age: {red}{created}{reset}
Is verified: {red}{user.verified}{reset}
Total submissions: {red}{total_submissions}{reset}
Total comments: {red}{total_comments}{reset}
""")
    if z > 0.3:
        print(f"Index of suspiciousty (Result of detection method 1): {red}{z} (Likely Bot){reset}")
    else:
        print(f"Index of suspiciousty (Result of detection method 1): {blue}{z} (Not Likely Bot){reset}")

    detect2_data = scanAccount(user.name, 50) # second detection algorithm
    if detect2_data > 129:
        print(f"""2nd Bot Detection Score: {red}{detect2_data} (Likely Bot){reset}""")
    else:
        print(f"""2nd Bot Detection Score: {blue}{detect2_data} (Not Likely Bot){reset}""")
              
    if ((detect2_data > 129 and z >= 0.3) or (detect2_data <= 129 and z < 0.3)):
        print(f"""{blue}Agreement in Detection{reset}\n""")
    else:
        print(f"""{red}Disagreement in Detection{reset}\n""")


def check_commentss(username):
    user = reddit.redditor(username)
    for comments in user.comments.new(limit=None):
        print(comments.body)
    print(f"checking comments for user {user.name}")
    z = 1.0
    seen = False
    for comments in user.comments.new(limit=5):
        print(comments.body)


def find_info(ids, depth):
    for i in ids:
        #try:
        if 1 == 1:
            submission = reddit.submission(id=i)
            print(f"Submission: {submission.url}")
            submission.comments.replace_more(limit=depth)
            for comment in submission.comments.list():
                if comment.author:
                    author = comment.author
                    user = reddit.redditor(author)
                    #for c in user.comments.new(limit=5):
                    #    print(1)
                    #check_comments(author)
                    display_info(user)
        #except RequestException:
        #    print("Request error occurred")
        #except Exception as e:
        #    print(f"Exception {e} ocurred")

if __name__ == "__main__":
    # Initialize the Reddit API client
    reddit = praw.Reddit(client_id=client,
                         client_secret=key,
                         user_agent=user_agent)

    x = input("1. Single search or 2. Submission search (1/2)? ")
    if x == '1':
        x = input("Username or 0 to leave: ")
        while x != '0':
            if '/u/' in x[0:3]:
                print(x)
                x = x[3:]
                print(x)
            try:
                user = reddit.redditor(x)
                display_info(user)
            except Exception as e:
                print(f"{red}Error While finding user {blue}{x}{reset}\n{e}")
            x = input(">>> ")

        exit()
    #Fetch the top posts from the "programming" subreddit
    x = input("What subreddit you want to look at? ")
    z = input("New, Hot or top submissions? (N/H/T) ")
    y = int(input("How many posts to retrieve? "))

    posts =[]
    try:
        if z.lower() == 'n':
            posts = reddit.subreddit(x).new(limit=y)
        if z.lower() == 'h':
            posts = reddit.subreddit(x).hot(limit=y)
        if z.lower() == 't':
            posts = reddit.subreddit(x).top(limit=y)
        depth = int(input("Depth: "))
        post_ids = [post.id for post in posts]
        find_info(post_ids, depth)
    except:
        print(f"{red}Error while fetching posts. Exiting.{reset}")
        exit()

    file.close()