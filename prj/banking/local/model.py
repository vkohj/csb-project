from ..models import *
from .general import *

from django.contrib.auth.models import User
from django.db import transaction

def localGetUser(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None

def localGetAccount(user):
    try:
        return Account.objects.get(user=user)
    except Account.DoesNotExist:
        return None

def localGetAgent(username) -> list:
    try:
        user = User.objects.get(username=username)
        acc = Account.objects.get(user=user)
        return [user, acc]
    except:
        return [False, False]

def localGetAccountByNumber(num):
    try:
        return Account.objects.get(num=num)
    except:
        return None
    
def localGetLogByID(id):
    try:
        return Log.objects.get(id=id)
    except:
        return None
    
def localIsValidAmount(acc:Account, amount:str, allowNegative = False):
    try:
        amount = int(amount)
    except:
        return "NOT VALID"
    
    if amount <= 0: return "NOT VALID"
    if acc.balance < amount and not allowNegative: return "NOT ENOUGH"
    return "C"

def localTransaction(request, sender:Account, receiver:Account, amount:int, message:str, type="transaction", name="Gift", allowNegative=False):
    if sender is None or receiver is None: return False
    if sender == receiver: return False
    if message is None: message = ""
    
    if localIsValidAmount(sender, amount, allowNegative=allowNegative) != "C": return False

    sender.balance -= amount
    receiver.balance += amount

    localLog(request, type=type, acc1=sender, acc2=receiver, name=name, ldetail=message, sdetail1=amount, hidden=False)

    sender.save()
    receiver.save()
    return True

@transaction.atomic
def localLog(request, type, hidden, name=None, ldetail=None, sdetail1=None, sdetail2=None, acc1=None, acc2=None):
    Log.objects.create(type=type, hidden=hidden, name=name, ldetail=ldetail, sdetail1=sdetail1, sdetail2=sdetail2, acc1=acc1, acc2=acc2, ip=localGetAddress(request))


@transaction.atomic
def localReportLoginFail(request, username):
    LoginAttempts.objects.create(username=username, ip=localGetAddress(request))

def localFilterOldAttempts(attempts : list):
    to_return = []
    for attempt in attempts:
        if not attempt.pastExpiry():
            to_return.append(attempt)
            continue

        # Remove
        attempt.delete()

    return to_return

def localGetLoginAttemptsByName(username):
    return localFilterOldAttempts(list(LoginAttempts.objects.filter(username=username)))

def localGetLoginAttemptsByRequest(request):
    ip=localGetAddress(request)
    if ip == "": return []
    return localFilterOldAttempts(list(LoginAttempts.objects.filter(ip=ip)))


def localGenerateAccNumber():
    while True:
        n1 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(2))
        n2 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        n3 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))

        num = '-'.join([n1, n2, n3])
        if localGetAccountByNumber(num) is None:
            return num

def localMustBeAdmin(user):
    try:
        if Admin.objects.get(user=user) is not None:
            return True
    except: pass

    return False