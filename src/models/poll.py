import uuid
import json
from pprint import pprint
import re


class Poll(object):
    def __init__(self, question, options, _id=None):
        self.queston = question
        self.options = options
        self._id = uuid.uuid4().hex if _id is None else _id


    @staticmethod
    def emoji_dict(num):
        emoji_dict = {1: ":one:",
                     2: ":two:",
                     3: ":three:",
                     4: ":four:",
                     5: ":five:",
                     6: ":six:",
                     7: ":seven:",
                     8: ":eight:",
                     9: ":nine:",
                     10: ":keycap_ten:"}
        return emoji_dict[num]

    @classmethod
    def create_poll(cls, poll):
        question = poll[0]
        options = poll[1:]
        formatted_options = ""
        actions = list()
        count = 0
        for option in options:
            count += 1
            option_stg = "{} {}\n".format(cls.emoji_dict(count), (options[count - 1])[0])
            formatted_options = formatted_options + option_stg
            actions.append({"name": "game",
                            "text": "{}".format(cls.emoji_dict(count)),
                            "type": "button",
                            "value": "{}".format(cls.emoji_dict(count))})
        poll_head = {
                    "text": question[0],
                    "response_type": "in_channel",
                    "attachments": [
                                        {
                                            "text": formatted_options,
                                            "fallback": "Something went wrong!",
                                            "callback_id": "poll",
                                            "color": "#3AA3E3",
                                            "attachment_type": "default",
                                            "actions": actions
                                        }
                                   ]
                    }
        pprint(poll_head)
        return json.dumps(poll_head)

    @staticmethod
    def form_response(user, action_value, question, attachments):
        for attachment in attachments:
            if "actions" in attachment:
                formatted_options = attachment["text"]
                for action in attachment["actions"]:
                    action["text"] = action["text"].replace("@" + user, "")
                    if action["value"] == action_value:
                        if re.search("\n", action["text"]):
                            action["text"] = action["text"] + " @" + user
                        else:
                            action["text"] = action["text"] + "\n@" + user
                attachments = [
                                  {"text": formatted_options,
                                   "fallback": "Something went wrong!",
                                   "callback_id": "poll",
                                   "color": "#3AA3E3",
                                   "attachment_type": "default",
                                   "actions": attachment["actions"]}
                              ]
                response = json.dumps({"text": question,
                                       "response_type": "in_channel",
                                       "attachments": attachments
                            })
                return response



