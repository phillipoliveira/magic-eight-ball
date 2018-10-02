from flask import Flask, request, Response
from models.slack_commands import SlackCommands
import random
import json

app = Flask(__name__)


@app.route("/eight_ball/begin_auth", methods=["GET"])
def pre_install():
    return '''
      <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
          Add to Slack
      </a>
  '''.format(SlackCommands.get_app_credentials()["SLACK_OAUTH_SCOPE"],
             (SlackCommands.get_app_credentials()["SLACK_BOT_CLIENT_ID"]))


@app.route("/eight_ball/finish_auth", methods=["GET", "POST"])
def post_install():
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        auth_code = request.args['code']
        # An empty string is a valid token for this request
        auth_response = SlackCommands.slack_token_request(auth_code)
        try:
            token = SlackCommands.get_token_from_database(team_id=auth_response['team_id'],
                                                          user_id=auth_response['user_id'])
            token.update_token(auth_response)
        except KeyError:
            token = SlackCommands()
            token.add_token(auth_response)
        return Response('It worked!')


@app.route('/eight_ball/commands', methods=['POST'])
def commands():
    # Echo the URL verification challenge code back to Slack
    answer = random.choice(answers)
    response = app.response_class(
        response=json.dumps({"text": answer,
                             "response_type": "in_channel"}),
        status=200,
        mimetype='application/json',)
    return response


answers = ["It is certain",
           "It is decidedly so",
           "Without a doubt",
           "Yes, definitely",
           "You may rely on it",
           "As I see it, yes",
           "Most likely",
           "Outlook good",
           "Yes",
           "Signs point to yes",
           "Reply hazy try again",
           "Ask again later",
           "Better not tell you now",
           "Cannot predict now",
           "Concentrate and ask again",
           "Don’t count on it",
           "My reply is no",
           "My sources say no",
           "Outlook not so good",
           "Very doubtful"]

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=4000)