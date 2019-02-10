import uuid
import json
from pprint import pprint
import re


class Poll(object):
    def __init__(self, emoji_dict=None):
        self.emoji_dict = {1: ":one:",
                           2: ":two:",
                           3: ":three:",
                           4: ":four:",
                           5: ":five:",
                           6: ":six:",
                           7: ":seven:",
                           8: ":eight:",
                           9: ":nine:",
                           10: ":keycap_ten:"} if emoji_dict is None else emoji_dict

    def define_emoji_dict(self, options):
            count = 0
            clean_options = list()
            for option in options:
                option = str(option[0])
                try:
                    count += 1
                    emoji = ":" + re.search(r'\:(\S+)\:', option).group(1) + ":"
                    self.emoji_dict[count] = emoji
                    clean_options.append(option.replace(emoji, "").lstrip())
                except AttributeError:
                    clean_options.append(option)
                    continue
            return clean_options

    def form_emoji_dict_from_actions(self, actions):
        for action in actions:
            self.emoji_dict[int(action['value']) + 1] = action['text']

    def create_poll(self, poll):
        question = poll[0]
        options = self.define_emoji_dict(poll[1:])
        formatted_options = ""
        actions = list()
        count = 0
        for option in options:
            count += 1
            option_stg = "{} {}\n".format(self.emoji_dict[count], option.rstrip())
            option_stg = "*" + option_stg + "*"
            formatted_options = formatted_options + option_stg
            actions.append({"name": "game",
                            "text": "{}".format(self.emoji_dict[count]),
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
        return json.dumps(poll_head)

    def reformat_text(self, formatted_options, user, action_value):
        options = filter(None, re.split(r'|'.join(self.emoji_dict.values()), formatted_options))
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
            split_options[0] = self.emoji_dict[count + 1] + " " + split_options[0] + "\n"
            if len(split_options) != 1:
                option_string = " ".join(split_options) + "\n"
            else:
                option_string = " ".join(split_options)
            option_string = re.sub(' +', ' ', option_string)
            formatted_options_list.append(option_string)
            count += 1
        return "".join(formatted_options_list)

    def form_response(self, user, action_value, question, attachments):
        for attachment in attachments:
            if "actions" in attachment:
                self.form_emoji_dict_from_actions(attachment["actions"])
                formatted_options = self.reformat_text(formatted_options=attachment["text"],
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

