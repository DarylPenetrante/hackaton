import re
import os

from slackclient import SlackClient
from github import Github

def get_latest_PR(events):
    for event in events:
        if event.type == 'PullRequestEvent' and event.payload['action'] == 'opened':
            return event.payload

def get_emails(reviewers, owner_email):
    im_list = sc.api_call("users.list")
    users = []
    owner = ''
    for im in im_list['members']:
        if 'email' in im['profile']:
            if im['profile']['email'] in reviewers:
                name = im['name']
                users.append(name)

            if im['profile']['email'] == owner_email:
                owner = im['name']
    return users, owner

def send_message(users, pr, owner):
    for user in users:
        sc.api_call("chat.postMessage",
            channel="@{}".format(user),
            attachments=[
                {
                    "fallback": "@{0} wants your review - {1}".format(owner, pr['pull_request']['html_url']),
                    "color": "#36a64f",
                    "pretext": "@{0} wants your review - {1}".format(owner, pr['pull_request']['html_url']),
                    "author_name": pr['pull_request']['user']['login'],
                    "author_link": pr['pull_request']['user']['html_url'],
                    "author_icon": pr['pull_request']['user']['avatar_url'],
                    "title": pr['pull_request']['title'],
                    "title_link": pr['pull_request']['html_url'],
                    "text": pr['pull_request']['body'],
                    "footer": "GitSlack",
                    "footer_icon": "https://assets-cdn.github.com/images/modules/logos_page/Octocat.png",
                }
            ],
            as_user="false",
            icon_url="https://assets-cdn.github.com/images/modules/logos_page/Octocat.png",
            username="GitSlack"
            )


if __name__ == '__main__':
    result = {}
    g = Github(os.environ['GITHUB_USER'], os.environ['GITHUB_TOKEN'], api_preview=True)

    repo = g.get_user().get_repo('hackaton')
    latest_PR = get_latest_PR(repo.get_events())
    owner_email = g.get_user(latest_PR['pull_request']['user']['login']).email

    pull_request = repo.get_pull(latest_PR['number'])

    reviewer_emails =[]
    for reviewer in pull_request.get_reviewer_requests():
        r = g.get_user(reviewer.login)
        reviewer_emails.append(r.email)

    reviewer_emails.append('daryl.penetrante@gengo.com')
    reviewer_emails.append('daryl.berza@gengo.com')
    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)
    users, owner = get_emails(reviewer_emails, owner_email)
    send_message(users, latest_PR, owner)
