from flask import Flask, request, Response
from models.slack_commands import SlackCommands
import random
import json
from csv import reader
from models.poll import Poll
from foaas import fuck
from unidecode import unidecode
import re
from pprint import pprint

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


@app.route('/eight_ball/question', methods=['POST'])
def question():
    answer = random.choice(answers)
    response = app.response_class(
        response=json.dumps({"text": answer,
                             "response_type": "in_channel"}),
        status=200,
        mimetype='application/json',)
    return response


@app.route('/eight_ball/insult', methods=['POST'])
def insult():
    sender = request.form.getlist('user_name')[0]
    raw_text = request.form.getlist('text')[0]
    try:
        name = raw_text.split("@")[1].split()[0]
        insult = fuck.random(name=name, from_=sender).text
    except IndexError:
        insult = fuck.random(from_=sender).text
    response = app.response_class(
        response=json.dumps({"text": insult,
                             "response_type": "in_channel"}),
        status=200,
        mimetype='application/json',)
    return response


@app.route('/poll_bot/new_poll', methods=['POST'])
def poll():
    username = request.form.getlist('user_name')[0]
    text = request.form.getlist('text')[0]
    text = (unidecode(text))
    print(text)
    poll = list()
    for line in reader(text):
        if re.search('[a-zA-Z]', str(line)):
            poll.append(line)
    print(poll)
    if len(poll) < 2:
        response = return_error()
    else:
        response = Poll.create_poll(poll)
    return response


@app.route('/poll_bot/respond', methods=['POST'])
def respond_to_poll():
        print(request.__dict__)


def return_error():
    response = app.response_class(
        response=json.dumps(
            {"text": "Sorry, I don't understand. Double-check your formating.",
             "response_type": "in_channel"}),
        status=200,
        mimetype='application/json')
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
           "Don't count on it",
           "My reply is no",
           "My sources say no",
           "Outlook not so good",
           "Very doubtful"]

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=4000)
