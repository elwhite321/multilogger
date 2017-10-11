import sys
import json
import copy
import logging
import datetime
from slackclient import SlackClient
from datalib.tool.logging import Logging

class SlackbotLogger(object):
    def __init__(self, slack_token, log_level=logging.WARN,
                 json_encoder=json.JSONEncoder):
        self.sc = SlackClient(slack_token)
        self.log_level = log_level
        self.colors = {
            logging.NOTSET: "#000099",
            logging.INFO: "good",
            logging.WARN: "warning",
            logging.ERROR: "danger",
            logging.DEBUG: "#708090"
        }
        self.meta_data = {"fields": []}
        self.msg = {"attachments": []}
        self.msg_levels = []
        self.premsg_text = lambda: f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\t"
        self.json_encoder = json_encoder

    def set_level(self, level):
        self.log_level = level

    def get_color(self, level):
        if level in self.colors:
            return self.colors[level]
        else:
            key = {abs(level - k):v for k,v in self.colors.items()}
            print(key)
            return key[min(key.keys())]

    def log(self, level, msg):
        color = self.get_color(level)
        self.push_msg(msg, level, color=color)

    def set_premsg_text(self, premsg):
        self.premsg_text = lambda: premsg

    def set_title(self, title):
        self.msg["text"] = f"*{title}*"

    def push_error(self, msg):
        self.log(logging.ERROR, f"<!here> {msg}")

    def push_okay(self, msg):
        self.log(logging.INFO, msg)

    def push_normal(self, msg):
        self.log(logging.INFO, msg)

    def push_warning(self, msg):
        self.log(logging.WARN, msg)

    def push_debug(self, msg):
        self.log(logging.DEBUG, msg)

    def push_msg(self, msg, log_level, **kwargs):
        self.msg["attachments"].append(
            {
                "text": f"{self.premsg_text()}{msg}",
                **kwargs
            }
        )
        self.msg_levels.append(log_level)

    def push_meta_data(self, name, msg, **kwargs):
        """always include any meta data added"""
        self.meta_data["fields"].append({
            "title": name,
            "value": msg,
            "short": True,
            **kwargs
        })

    def send(self, channels, **kwargs):
        send_msg = copy.deepcopy(self.msg)
        send_msg["attachments"] = []
        del_msg_idx = []
        for n in range(len(self.msg_levels)):
            if self.msg_levels[n] >= self.log_level:
                send_msg["attachments"].append(
                    copy.deepcopy(self.msg["attachments"][n])
                )
                del_msg_idx.append(n)
        for n in reversed(del_msg_idx):
            del self.msg["attachments"][n]
            del self.msg_levels[n]
        res = None
        if send_msg != {"attachments": []} and channels:
            if self.meta_data["fields"]:
                send_msg["attachments"].insert(0, self.meta_data)
            msg = json.loads(json.dumps({
                **send_msg,
                **kwargs
            }, cls=self.json_encoder))
            # don't send empty msgs
            for channel in channels:
                res = self.sc.api_call(
                    "chat.postMessage",
                    channel=channel,
                    as_user=True,
                    **msg
                )
        return res

    def clear(self):
        self.meta_data = {"fields": []}
        self.msg = {"attachments": []}
        self.msg_levels = []

    def empty(self):
        return not [k for k in self.msg if k != "attachments"] \
               and not self.msg["attachments"] \
               and not [k for k in self.meta_data if k != "fields"] \
               and not self.meta_data["fields"] \
               and not self.msg_levels


class MultiLogger(object):

    def __init__(self, service_name, log_level=logging.INFO, slack_token=None,
                 json_encoder=json.JSONEncoder, log_stream=sys.stdout):
        self.logger = Logging(service_name, stream=log_stream)
        self.logger.setLevel(log_level)
        self.slack_logger = SlackbotLogger(slack_token, log_level=log_level,
                                           json_encoder=json_encoder)
        self.log_meta = {}

    def set_level(self, level):
        self.logger.setLevel(level)
        self.slack_logger.set_level(level)

    def set_slack_level(self, level):
        self.slack_logger.set_level(level)

    def set_log_level(self, level):
        self.logger.setLevel(level)

    def log(self, lvl, msg):
        self.logger.log(lvl, msg)
        self.slack_logger.log(lvl, msg)

    def send(self, channels, **kwargs):
        self.slack_logger.send(channels, **kwargs)

    def set_meta(self, name, value, **kwargs):
        self.log_meta[name] = value
        self.slack_logger.push_meta_data(name, value, **kwargs)

