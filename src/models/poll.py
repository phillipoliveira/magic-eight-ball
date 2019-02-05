import uuid
import json
from pprint import pprint
import re


class Poll(object):
    def __init__(self, question, options, _id=None):
        self.queston = question
        self.options = options
        self._id = uuid.uuid4().hex if _id is None else _id

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

    @classmethod
    def create_poll(cls, poll):
        question = poll[0]
        options = poll[1:]
        formatted_options = ""
        actions = list()
        count = 0
        for option in options:
            count += 1
            option_stg = "{} {}\n".format(cls.emoji_dict[count], (options[count - 1])[0].rstrip())
            formatted_options = formatted_options + option_stg
            actions.append({"name": "game",
                            "text": "{}".format(cls.emoji_dict[count]),
                            "type": "button",
                            "value": "{}".format(count - 1)})
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

    @classmethod
    def reformat_text(cls, formatted_options, user, action_value):
        options = filter(None, re.split(r'|'.join(cls.emoji_dict.values()), formatted_options))
        formatted_options_list = list()
        count = 0
        user = "@" + user
        for option in options:
            dirty_split_options = option.split("\n")
            split_options = list()
            for i in dirty_split_options:
                option = i.lstrip().rstrip().replace(user, "")
                if re.search('[a-zA-Z]', option):
                    split_options.append(option)
            if count == action_value:
                split_options.append(user)
            split_options[0] = cls.emoji_dict[count + 1] + " " + split_options[0] + "\n"
            if len(split_options) != 1:
                option_string = " ".join(split_options) + "\n"
            else:
                option_string = " ".join(split_options)
            option_string = re.sub(' +', ' ', option_string)
            formatted_options_list.append(option_string)
            count += 1
        return "".join(formatted_options_list)

    @classmethod
    def form_response(cls, user, action_value, question, attachments):
        for attachment in attachments:
            if "actions" in attachment:
                print(attachment["text"])
                print(user)
                print(action_value)
                formatted_options = cls.reformat_text(formatted_options=attachment["text"],
                                                      user=user,
                                                      action_value=int(action_value))

                pprint(formatted_options)
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



