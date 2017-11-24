import logging
from unittest.mock import patch
from multilogger import logger

def test_get_slack_logger():
    for n in range(0, 51):
        slack_log = logger.SlackbotLogger("test-api-token", log_level=n)
        assert slack_log.log_level == n
        assert slack_log.msg["attachments"] == []
        assert slack_log.meta_data["fields"] == []


def test_slack_push_error():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_error(msg)
        assert {
                   "text": f"{premsg}<!here> {msg}",
                   "color": "danger"
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_slack_push_warn():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_warning(msg)
        assert {
                   "text": f"{premsg}{msg}",
                   "color": "warning"
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_slack_push_okay():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_okay(msg)
        assert {
                   "text": f"{premsg}{msg}",
                   "color": "good"
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_slack_push_normal():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_normal(msg)
        assert {
                   "text": f"{premsg}{msg}",
                   "color": slack_log.get_color(logging.INFO)
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_slack_push_debug():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_debug(msg)
        assert {
                   "text": f"{premsg}{msg}",
                   "color": slack_log.get_color(logging.DEBUG)
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_slack_push_msg():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.push_msg(msg, 100)
        assert {
                   "text": f"{premsg}{msg}"
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_push_meta_data():
    slack_log = logger.SlackbotLogger("test-api-token")
    slack_log.push_meta_data("test_field", "test")
    assert not slack_log.empty()
    assert {
               "title": "test_field",
               "value": "test",
               "short": True
           } in slack_log.meta_data["fields"]
    slack_log.clear()
    assert slack_log.empty()


def test_set_title():
    slack_log = logger.SlackbotLogger("test-api-token")
    title = "test_title"
    slack_log.set_title(title)
    assert slack_log.msg["text"] == f"*{title}*"
    assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


def test_log():
    slack_log = logger.SlackbotLogger("test-api-token")
    premsg = "test_prems"
    slack_log.set_premsg_text(premsg)
    for n in range(1, 51):
        msg = f"test_msg {n}"
        slack_log.set_level(n)
        assert slack_log.log_level == n
        slack_log.log(n, msg)
        assert {
                   "text": f"{premsg}{msg}",
                   "color": slack_log.get_color(n)
               } in slack_log.msg["attachments"]
        assert len(slack_log.msg["attachments"]) == n
        assert not slack_log.empty()
    slack_log.clear()
    assert slack_log.empty()


@patch("multilogger.logger.SlackClient.api_call")
def test_send(sc_call_mock):
    sbl = logger.SlackbotLogger("test_token")
    sbl.set_premsg_text("")

    def fill(log_level):
        sbl.push_debug("debug")
        sbl.push_normal("normal")
        sbl.push_okay("okay")
        sbl.push_warning("warning")
        sbl.push_error("error")
        sbl.push_msg("noset", logging.NOTSET)
        sbl.set_level(log_level)
        print(sbl.msg_levels)
        sbl.send(["test_channel"])
        if sc_call_mock.call_args_list:
            args, kwargs = (sc_call_mock.call_args_list[0][0],
                            sc_call_mock.call_args_list[0][1])
            for msg in kwargs["attachments"]:
                assert msg not in sbl.msg["attachments"]
            for msg in sbl.msg["attachments"]:
                assert msg not in kwargs["attachments"]
        else:
            args, kwargs = (None, None)
        return args, kwargs

    args, kwargs = fill(logging.NOTSET)
    print(args, kwargs)
    assert sc_call_mock.called
    assert len(kwargs["attachments"]) == 6
    assert len(sbl.msg["attachments"]) == 0
    assert args == ("chat.postMessage",)
    assert kwargs["channel"] == "test_channel"
    assert kwargs["as_user"] == True
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False
    sbl.clear()
    assert sbl.empty()

    args, kwargs = fill(logging.DEBUG)
    assert sc_call_mock.called
    assert len(kwargs["attachments"]) == 5
    assert len(sbl.msg["attachments"]) == 1
    assert args == ("chat.postMessage",)
    assert kwargs["channel"] == "test_channel"
    assert kwargs["as_user"] == True
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False
    sbl.clear()
    assert sbl.empty()

    args, kwargs = fill(logging.INFO)
    print(args, kwargs)
    assert sc_call_mock.called
    assert len(kwargs["attachments"]) == 4
    assert len(sbl.msg["attachments"]) == 2
    assert args == ("chat.postMessage",)
    assert kwargs["channel"] == "test_channel"
    assert kwargs["as_user"] == True
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False
    sbl.clear()
    assert sbl.empty()

    args, kwargs = fill(logging.WARN)
    print(args, kwargs)
    assert sc_call_mock.called
    assert len(kwargs["attachments"]) == 2
    assert len(sbl.msg["attachments"]) == 4
    assert args == ("chat.postMessage",)
    assert kwargs["channel"] == "test_channel"
    assert kwargs["as_user"] == True
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False
    sbl.clear()
    assert sbl.empty()

    args, kwargs = fill(logging.ERROR)
    print(args, kwargs)
    assert sc_call_mock.called
    assert len(kwargs["attachments"]) == 1
    assert len(sbl.msg["attachments"]) == 5
    assert args == ("chat.postMessage",)
    assert kwargs["channel"] == "test_channel"
    assert kwargs["as_user"] == True
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False
    sbl.clear()
    assert sbl.empty()

    args, kwargs = fill(logging.ERROR + 1)
    print(args, kwargs)
    assert not args and not kwargs
    assert len(sbl.msg["attachments"]) == 6
    assert not sc_call_mock.called
    sc_call_mock.call_args_list = []
    sc_call_mock.called = False