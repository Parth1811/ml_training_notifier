import os
import time
import re
from slackclient import SlackClient

from commands import POSSIBLE_COMMANDS
from commands import execute_command

# constants
AUTH_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
RTM_READ_DELAY = 1 # delay between reading from RTM in seconds
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = None
slack_bot_id = None


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == slack_bot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    default_response = "Not sure what you mean. Try *help*"

    response = None
    if command.startswith(POSSIBLE_COMMANDS):
        response = execute_command(command)

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if AUTH_TOKEN is None:
        raise EnvironmentError('SLACK_BOT_TOKEN not found \n'
                               '    Try: Run the following command\n'
                               '        export SLACK_BOT_TOKEN="<your-token>"')

    slack_client = SlackClient(AUTH_TOKEN)
    if slack_client.rtm_connect(with_team_state=False):
        print("Slack Training Notifier Bot connected and running!")
        slack_bot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command is not None:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
