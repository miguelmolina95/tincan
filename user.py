import logging
import datetime
from google.appengine.ext import ndb

DEVEOPING = True

class User(ndb.Model):
    # max number of users to query for
    MAX_QUERY = 100

    name = ndb.StringProperty(default="Psuedoscience", required=True)
    # TODO: create a phone number class for validation
    # https://cloud.google.com/appengine/docs/standard/python/ndb/subclassprop
    phonenumber = ndb.StringProperty(required=True)
    in_queue = ndb.BooleanProperty(default=False)
    # queue_place = ndb.IntegerProperty(default=-1)
    # this property is updated automatically when the entity is updated
    queue_join_date = ndb.DateTimeProperty(auto_now=True)

    # creates a user, saves to database, and returns the user
    @staticmethod
    def create_user(name, phonenumber, in_queue=False):
        user = User(
            name=name,
            phonenumber=phonenumber, # TODO: needs validation
            in_queue=in_queue
        )
        user.put()
        return user

    # TODO: DRY up with toggle_user_queue(self, user)
    # add user to the queue, returns the user
    @staticmethod
    def add_to_queue(user):
        logging.log(logging.INFO, "add_to_queue, user=" + user.name)
        if user.in_queue:
            return user
        user.in_queue = True
        user.put()
        return user

    # removes a user from the queue, returns the user
    # TODO: DRY up with toggle_user_queue(self, user)
    @staticmethod
    def remove_from_queue(user):
        logging.log(logging.INFO, "remove_from_queue, user=" + user.name)
        if not user.in_queue:
            return user
        user.in_queue = False
        user.put()
        return user

    # get current users in queue, returns a list of Users
    @staticmethod
    def get_queue():
        logging.log(logging.INFO, "get_queue")
        # get all users that are in_queue, ordered in ascending by date
        query = User.query(User.in_queue == True).order(User.queue_join_date)
        users = query.fetch(User.MAX_QUERY)
        # create dummy users
        if DEVEOPING and not users:
            grr = User.create_user("Grrr", "+15101234567", True)
            zim = User.create_user("Zim", "+15101114444", True)
            users = [grr, zim]
            ndb.put_multi(users)
        logging.log(logging.INFO, "get_queue: query returned " + str(len(users)))
        return users
    
    # get user by phonenumber, returns user
    @staticmethod
    def get_user(phonenumber):
        logging.log(logging.INFO, "get_queue, phonenumber=" + str(phonenumber))
        query = User.query(User.phonenumber==phonenumber)
        users = query.fetch(1)
        if not users:
            return False
        return users[0]
