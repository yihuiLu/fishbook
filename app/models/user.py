# -*- coding: utf-8 -*-
# @Time    : 2018/11/21 14:30
# @Author  : YH
# @Site    : 
# @File    : user.py
# @Software: PyCharm

from sqlalchemy import Column, Integer, Boolean, Float, String
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login_manager
from app.libs.helper import is_isbn_or_key
from app.models.base import Base
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook


class User(UserMixin, Base):
    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    _password = Column('password', String(128), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))

    @property
    def password(self):  # geter
        return self._password

    @password.setter
    def password(self, raw):  # seter
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self._password, raw)

    # def get_id(self):
    #     """
    #     login_user要求定义此函数，用来返回用户id，如果不继承UserMixin则必须定义此函数，前提是你的用户id命名必须是‘id’
    #     :return: userID
    #     """
    #     return self.id

    def can_save_to_list(self, isbn):
        if is_isbn_or_key(isbn) != 'isbn':
            return False
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)
        if not yushu_book.first:
            return False

        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn,
                                       launched=False).first()
        wishing = Wish.query.filter_by(uid=self.id, isbn=isbn,
                                       launched=False).first()

        if not gifting and not wishing:
            return True
        else:
            return False


@login_manager.user_loader
def get_user(uid):  # *1.1
    return User.query.get(int(uid))
