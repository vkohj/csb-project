from ..models import *
from .general import *

from django.contrib.auth.models import User

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
        return {user, acc}
    except:
        return {False, False}

def localGetAccountByNumber(num):
    try:
        return Account.objects.get(num=num)
    except:
        return None
    
def localIsValidAmount(acc:Account, amount:str):
    try:
        amount = int(amount)
    except:
        return "NOT VALID"
    
    if amount <= 0: return "NOT VALID"
    if acc.balance < amount: return "NOT ENOUGH"
    return "C"

def localTransaction(sender:Account, receiver:Account, amount:int, message:str):
    if sender is None or receiver is None: return False
    if sender == receiver: return False
    if message is None: message = ""
    
    if localIsValidAmount(sender, amount) != "C": return False

    sender.balance -= amount
    receiver.balance += amount

    Log.objects.create(type="transaction", acc1=sender, acc2=receiver, name="Gift", ldetail=message, sdetail1=amount, hidden=False)

    sender.save()
    receiver.save()
    return True

def localLog(request, type, hidden, name=None, ldetail=None, sdetail1=None, sdetail2=None, acc1=None, acc2=None):
    if request is None: return
    Log.objects.create(type=type, hidden=hidden, name=ldetail, ldetail=ldetail, sdetail1=sdetail1, sdetail2=sdetail2, acc1=acc1, acc2=acc2, ip=localGetAddress(request))


def localGenerateAccNumber():
    while True:
        n1 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(2))
        n2 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        n3 = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))

        num = '-'.join([n1, n2, n3])
        if localGetAccountByNumber(num) is None:
            return num