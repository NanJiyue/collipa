# coding: utf-8

import logging
import tornado.web
import tornado.websocket
import tornado.escape

import config
from ._base import BaseHandler
from pony.orm import db_session

from models import User
from extensions import rd

config = config.rec()


class WebSocketHandler(BaseHandler, tornado.websocket.WebSocketHandler):
    users = set()
    online = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    @db_session
    def open(self):
        if self not in WebSocketHandler.users:
            self.user_id = 0
            if self.current_user:
                self.user_id = self.current_user.id
                WebSocketHandler.online.add(self.current_user.id)
                rd.sadd("online", self.current_user.id)
            WebSocketHandler.users.add(self)
            logging.info("%s online" % self.user_id)
            logging.info("ip is %s" % self.request.remote_ip)
            WebSocketHandler.send_online()

    def on_close(self):
        if self in WebSocketHandler.users:
            if self.current_user:
                try:
                    WebSocketHandler.online.remove(self.user_id)
                except:
                    pass
                rd.srem("online", self.user_id)
            WebSocketHandler.users.remove(self)
            logging.info("%s offline" % self.user_id)
            WebSocketHandler.send_online()

    @classmethod
    def send_online(cls):
        online = rd.smembers("online")
        logging.info("Online user count is " + unicode(len(online)))
        for user in cls.users:
            try:
                user.write_message({
                    "type": "online",
                    "count": unicode(len(online))
                })
            except Exception as e:
                logging.error("Error sending online user count", exc_info=True)
                if type(e).__name__ == "AttributeError":
                    try:
                        WebSocketHandler.users.remove(user)
                        rd.srem("online", user.user_id)
                        WebSocketHandler.online.remove(user.user_id)
                    except:
                        pass

    @classmethod
    @db_session
    def send_message(cls, user_id, message):
        logging.info("Message send")
        for this in cls.users:
            if this.user_id == user_id:
                try:
                    user = User[user_id]
                    this.write_message({
                        "type": "message",
                        "count": user.unread_message_box_count,
                        "content": message.content,
                        "created": message.created,
                        "id": message.id,
                        "avatar": message.sender.get_avatar(size=48),
                        "sender_id": message.sender.id,
                        "url": message.sender.url,
                        "nickname": message.sender.nickname,
                        "message_box_id": message.message_box2_id
                    })
                except Exception, e:
                    print e
                    logging.error("Error sending message", exc_info=True)

    @classmethod
    @db_session
    def send_notification(cls, user_id):
        logging.info("Notification send")
        for this in cls.users:
            if this.user_id == user_id:
                try:
                    user = User[user_id]
                    this.write_message({"type": "notification",
                                        "count": user.unread_notification_count})
                except Exception, e:
                    print e
                    logging.error("Error sending notification", exc_info=True)

    def on_message(self, message):
        logging.info(message)


class GetUserNameHandler(BaseHandler):
    @db_session
    def get(self):
        users = User.select()
        user_json = []
        for user in users:
            user_json.append({"value": user.name, "label": user.nickname})
        return self.write(user_json)


class MentionHandler(BaseHandler):
    @db_session
    def get(self):
        word = self.get_argument('word', None)
        if not word:
            return self.write({
                'status': 'error',
                'message': '没有关键字'
            })
        user_list = User.mention(word)
        user_json = []
        for user in user_list:
            user_json.append({
                'id': user.id,
                'name': user.name,
                'nickname': user.nickname,
                'url': user.url,
                'avatar': user.get_avatar()
            })
        return self.write({
            'status': 'success',
            'user_list': user_json
        })
