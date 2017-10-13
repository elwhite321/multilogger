import sys
import json
import copy
import logging
from datetime import datetime
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

    def set_token(self, token):
        self.sc = SlackClient(token)

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
                 json_encoder=json.JSONEncoder, slack_channels=None, log_stream=sys.stdout):
        self.json_encoder = json_encoder
        self.logger = Logging(service_name, stream=log_stream).logger
        self.logger.setLevel(log_level)
        self.slack_logger = SlackbotLogger(slack_token, log_level=log_level,
                                           json_encoder=json_encoder)

        self.log_meta = {}
        if self.json_encoder != json.JSONEncoder:
            self.log_meta["json_encoder"] = str(self.json_encoder)
        self.slack_channels = slack_channels

    def set_level(self, level):
        self.logger.setLevel(level)
        self.slack_logger.set_level(level)

    def set_slack_level(self, level):
        self.slack_logger.set_level(level)

    def set_log_level(self, level):
        self.logger.setLevel(level)

    def log(self, lvl, msg):
        log_msg = copy.deepcopy(msg)
        if self.log_meta:
            log_msg = {"msg": log_msg, **self.log_meta}
        log_msg = json.loads(json.dumps(log_msg, cls=self.json_encoder))
        self.logger.log(lvl, log_msg)
        self.slack_logger.log(lvl, msg)

    def send(self, channels=None, **kwargs):
        if not channels:
            channels = self.slack_channels
        if channels:
            res = self.slack_logger.send(channels, **kwargs)
            if res and not res.get("ok"):
                self.logger.log(logging.WARN, f"slackbot error: {res}")
        else:
            msg = "Attempted to send slack logs but no channels specified"
            self.logger.log(logging.DEBUG, msg)

    def set_meta(self, **kwargs):
        self.log_meta = {**self.log_meta, **kwargs}
        for name, msg in kwargs.items():
            self.slack_logger.push_meta_data(name, msg)

