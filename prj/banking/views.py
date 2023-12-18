from django.shortcuts import render
from django.http import *
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import *
from .forms import *

from .local.model import *
from .local.general import *


# 「INDEX」
# Move user to either /user/hello/ or /login/
def vIndex(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("user/" + request.user.username + "/hello")
    return HttpResponseRedirect("login")


# 「INIT」
# Used for testing (not considered part of the site)
def vInit(request):
    User.objects.all().delete() 
    u = User.objects.create_user(username="admin")
    u.set_password("admin")
    u.save()

    a = Account.objects.create(user=u, balance=100, num="55-0080-0810")
    return HttpResponse("Initialization complete. Not part of the project.")


# 「login.html」（GET & POST）
# The log-in page
def vLogin(request):

    # 「GET」
    if request.method =='GET':
        return render(request, "login.html", {"form":LoginForm(), "err":localGetErr(request), "anonymous":True, "header":True})


    # 「POST」
    name = request.POST["username"]
    user = authenticate(request, username=name, password=request.POST["password"])

    # If invalid, exit
    if user is None:
        localLog(request, "login", True, name="LOGIN FAIL", sdetail1=name)
        return HttpResponseRedirect("?t=l_invalid")

    # Complete log-in process
    login(request, user)
    localLog(request, "login", True, name="LOGIN OK", sdetail1=name)
        
    if "next" in request.GET: return HttpResponseRedirect(request.GET["next"])
    return HttpResponseRedirect("/")


# 「LOGOUT」
# Attempts to log-out the user.
def vLogout(request):
    logout(request)
    return HttpResponseRedirect("/")
        

# 「create.html」（GET & POST）
# Create a new account.
def vCreate(request):

    # 「GET」
    if request.method =='GET':
        return render(request, "create.html", {"anonymous":True, "state":localGetErr(request)})
    

    # 「PUSH」
    if "username" not in request.POST: 
        return HttpResponse("Invalid!")
    
    username = request.POST["username"]
    pswd = localGeneratePassword()
    blc = 0
    num = localGenerateAccNumber()

    # Username, generated password check
    if len(username) < 4 or len(username) > 32 or not localCheckNoSpecials(username): return HttpResponseRedirect("?t=c_username")
    if not localCheckPassword(pswd): return HttpResponseRedirect("?t=password")

    # CHECK IF EXISTS
    try:
       User.objects.get(username=username)
       return HttpResponseRedirect("?t=c_exists")
    except User.DoesNotExist: pass

    user = User.objects.create(username=username)
    user.set_password(pswd)
    user.save()

    acc = Account.objects.create(user=user, balance=blc, num=num)

    return render(request, "create_finish.html", {"acc":acc, "pswd":pswd})


# 「index.html」
# See the /user/<username>/hello page
@login_required
def vHello(request, username):
    user,acc = localGetAgent(username)
    if acc is None: return HttpResponse("404!")

    return render(request, "index.html", {"acc":acc})


# 「send.html」
@login_required
def vSend(request, username):
    user,acc = localGetAgent(username)
    if acc is None: return HttpResponse("404!")

    # 「GET」
    if request.method == "GET":
        return render(request, "send.html", {"num":acc.num})
    

    # 「POST」
    if "receiver" not in request.POST or "amount" not in request.POST or "message" not in request.POST:
        return HttpResponse("Invalid!")
    
    sender = acc.num
    receiver = request.POST["receiver"]
    amount = request.POST["amount"]
    message = request.POST["message"]

    # Save to session
    request.session["s_receiver"] = receiver
    request.session["s_amount"] = amount
    request.session["s_message"] = message

    # Textbox defaults
    err_receiver = True
    txt_receiver = "NOT FOUND"
    err_amount = True
    txt_amount = localIsValidAmount(acc, amount)

    # Check for errors and load confirm page
    acc2 = localGetAccountByNumber(receiver)
    if acc2 is not None:
        txt_receiver = f"{acc2.user.username} ({receiver})"
        err_receiver = False
    
    if txt_amount == "C":
        txt_amount = amount
        err_amount = False

    return render(request, "send_confirm.html", {"sender":sender, "receiver":txt_receiver, "message":message.split("\n"), "amount":txt_amount, "receiver_err":err_receiver, "amount_err":err_amount, "not_err":not(err_receiver or err_amount) })


# SEND PROCESS
# Gift has been confirmed by the sender, so deduct the points and send them
def vSendConfirm(request, username):
    # Get accounts, no need to check if exists.
    user, acc = localGetAgent(username)
    receiver = localGetAccountByNumber(request.session["s_receiver"])
    amount = int(request.session["s_amount"])
    message = request.session["s_message"]

    # Create transaction, return "Illegal" if something goes wrong
    if not localTransaction(acc, receiver, amount, message):
        return HttpResponse("Illegal!")

    return HttpResponseRedirect("./?t=s_sent")


# 「history.html」
# See the transaction history
def vTransactions(request, username):
    user, acc = localGetAgent(username)
    if acc is None: return HttpResponse("404!")

    transactions = list(Log.objects.filter((Q(acc1=acc) | Q(acc2=acc)) & Q(type="transaction") & Q(hidden=False)).order_by("-id"))
    amounts = []

    # Check if the transaction was done by the user, or received by the user
    for t in transactions:
        s = ""
        try:
            if t.acc1 != acc: s = "+" + t.sdetail1 + "℗"
            else: s = "-" + t.sdetail1 + "℗"
        except:
            s = "ERR"
        amounts.append(s)
    
    # Conbine the transactions and amounts
    data = zip(transactions, amounts)

    return render(request, "history.html", {"l":data})



# ADMIN
def vAdmin(request):
    if (request.user.is_authenticated):
        template = loader.get_template("admin.html")
        return HttpResponse(template.render({}, request))
    
    return HttpResponseRedirect("/login/?next=/admin/")

def vAdminCreate(request):
    if request.method =='GET':
        state = ""
        if "t" in request.GET:
            t = request.GET["t"]
            if t == "a_exists": state = "Account number is already in use!"
            elif t == "u_exists": state = "Username is already in use!"
            elif t == "password": state = "Password must be 6 letters or more."
            elif t == "username": state = "Username must be between 4 and 32 letters. Username cannot include special characters."
            elif t == "balance": state = "Balance must be positive."
            elif t == "num": state = "Account number must be of format XX-XXXX-XXXX."
            elif t == "created": state = "Account created."

        pswd = localGeneratePassword()
        request.session["c_pswd"] = pswd

        template = loader.get_template("admin_create.html")
        return HttpResponse(template.render({"pass":pswd, "state":state}, request))
    
    user = request.POST["username"]
    blc = request.POST["balance"]
    num = request.POST["num"]

    #pswd = request.POST["password"]
    if "c_pswd" not in request.session: return HttpResponseRedirect("?t=password")
    pswd = request.session["c_pswd"]

    if len(user) < 4 or len(user) > 32 or not localCheckNoSpecials(user): return HttpResponseRedirect("?t=username")
    if int(blc) < 0: return HttpResponseRedirect("?t=balance")
    if len(num) != 12 or num[2] != "-" or num[7] != "-": return HttpResponseRedirect("?t=num")

    if not localCheckPassword(pswd): return HttpResponseRedirect("?t=password")

    # CHECK IF EXISTS
    try:
       User.objects.get(username=user)
       return HttpResponseRedirect("?t=u_exists")
    except User.DoesNotExist:
        pass

    try:
       Account.objects.get(num=num)
       return HttpResponseRedirect("?t=a_exists")
    except Account.DoesNotExist:
        pass

    u = User.objects.create(username=user)
    u.set_password(pswd)
    u.save()

    a = Account.objects.create(user=u, balance=blc, num=num)

    return HttpResponseRedirect("?t=created")

def vAdminManage(request):
    template = loader.get_template("admin_manage.html")

    accounts = Account.objects.all()
    return HttpResponse(template.render({"accounts":accounts}, request))

def vAdminManageBalance(request, username):
    user = localGetUser(username)
    if user is None: return HttpResponse("404")
        
    acc = localGetAccount(user)
    if acc is None: return HttpResponse("404")
    
    if request.method =='GET':
        template = loader.get_template("admin_manage_acc.html")
        return HttpResponse(template.render({"acc":acc, "form":ModifyBalance, "type":"balance"}, request))
    
    if "balance" not in request.POST: return HttpResponse("443")
    balance = request.POST["balance"]
    if not balance.isnumeric() and int(balance) < 0: return HttpResponseRedirect("?t=balance")

    acc.balance = int(balance)
    acc.save()

    return HttpResponseRedirect("?t=ok")


def vAdminManagePassword(request, username):
    user = localGetUser(username)
    if user is None: return HttpResponse("404")

    acc = localGetAccount(user)
    if acc is None: return HttpResponse("404")
    
    if request.method =='GET':
        template = loader.get_template("admin_manage_acc.html")
        return HttpResponse(template.render({"acc":acc, "form":ModifyPassword, "type":"password"}, request))

    if "password" not in request.POST or "password_confirm" not in request.POST: return HttpResponse("443")
    pswd = request.POST["password"]
    if pswd != request.POST["password_confirm"]: return HttpResponseRedirect("?t=password")
    
    if not localCheckPassword(pswd): return HttpResponseRedirect("?t=password")

    user.set_password(pswd)
    user.save()

    return HttpResponseRedirect("?t=ok")

def vAdminLogs(request):
    logs = Log.objects.all().order_by("-id")

    template = loader.get_template("admin_logs.html")
    return HttpResponse(template.render({"logs":logs}, request))

