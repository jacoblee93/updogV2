import os

def populate():
    u1=add_user('lloyd69', 'lloyd', 'lee', 'entourage', 'lloyd@princeton.edu')
    u2=add_user('sskoular', 'sonia', 'skoularikis', 'summer14', 'sskoular@princeton.edu')
    u3=add_user('tank', 'franklyn', 'darnis', 'lift', 'fdarnis@princeton.edu')
    u4=add_user('poushy', 'alex', 'pouschine', 'cloister', 'apouschine@princeton.edu')

    ud1=add_updoguser(u1, 1)
    ud2=add_updoguser(u2, 2)
    ud3=add_updoguser(u3, 3)
    ud4=add_updoguser(u4, 4)

    add_updogfriend(ud1, u3)
    add_updogfriend(ud3, u1)
    add_updogfriend(ud3, u4)
    add_updogfriend(ud4, u3)


    add_pack('cos333', [ud1, ud2, ud3, ud4])


def add_user(username, firstname, lastname, password, email):

    user = User.objects.create_user(username=username, first_name=firstname, last_name=lastname, password=password, email=email)
    user.save()
    return user

def add_updoguser(user, fbID):
    
    udUser = UpDogUser.objects.get_or_create(user=user, fbID=fbID)[0]
    return udUser

def add_updogfriend(friend, person):

    udFriend = UpDogFriend.objects.get_or_create(friend=friend, person=person)[0]
    return udFriend

def add_pack(name, udUsers):

    pack = Pack.objects.get_or_create(name=name)[0]
    for user in udUsers:
        pack.updoguser_set.add(user)

    return pack

def add_downtime(user, startTime, endTime, seeingFriends):
    downtime = Downtime.objects.get_or_create(user = user, startTime = startTime, endTime = endTime)[0]
    for friend in seeingFriends:
        downtime.updoguser_set.add(friend)

    return downtime

def add_event(startTime, endTime, participants):
    event = Event.objects.get_or_create(startTime=startTime, endTime=endTime)[0]
    for individual in participants:
        event.updoguser_set.add(individual)
    return event

if __name__ == '__main__':
    print "Starting UpDog population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'updog.settings')

    from django.contrib.auth.models import User
    from udCalendar.models import UpDogUser, UpDogFriend, Pack, Downtime, Event

    populate()
