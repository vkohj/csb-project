from django.shortcuts import render
from django.http import *
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.db import transaction

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
@transaction.atomic
def vInit(request):
    User.objects.all().delete() 
    u = User.objects.create_user(username="admin")
    u.set_password("ks0prUxWDwPJv96")
    u.save()

    admin = Admin.objects.create(user=u)

    a = Account.objects.create(user=u, balance=1000, num="55-0080-0810")
    return HttpResponse("Initialization complete. Not part of the project.")


# 「login.html」（GET & POST）
# The log-in page
def vLogin(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    # 「GET」
    if request.method =='GET':
        return render(request, "login.html", {"err":localGetErr(request), "anonymous":True, "header":True})


    # 「POST」
    name = request.POST["username"]

    # FAULT: A07:2021-Identification and Authentication Failures (Bruteforcing possible)
    # FIX:
    #if len(localGetLoginAttemptsByName(name)) >= 3:
    #    return HttpResponseRedirect("?t=l_toomany_n")
    
    #if len(localGetLoginAttemptsByRequest(request)) >= 5:
    #    return HttpResponseRedirect("?t=l_toomany_r")
    

    # Authenticate, if invalid, exit
    user = authenticate(request, username=name, password=request.POST["password"])
    if user is None:
        # FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
        # FIX: 
        # localLog(request, "login", True, name="LOGIN FAIL", sdetail1=name)

        # FAULT: A07:2021-Identification and Authentication Failures (Bruteforcing is not reported)
        # FIX:
        # localReportLoginFail(request, name)

        return HttpResponseRedirect("?t=l_invalid")

    # Complete log-in process
    login(request, user)
    
    # FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
    # FIX: 
    # localLog(request, "login", True, name="LOGIN OK", sdetail1=name)
        
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
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    # 「GET」
    if request.method =='GET':
        return render(request, "create.html", {"anonymous":True, "state":localGetErr(request)})
    

    # 「PUSH」
    if "username" not in request.POST: 
        return HttpResponse("Invalid!")
    
    username = request.POST["username"]
    
    # FAULT: A04:2021-Insecure Design (Password is automatically generated, 
    #        and only 6 letters long)
    # REMOVE:
    pswd = localGeneratePassword()
    
    # FIX:
    #if "pswd" not in request.POST or "pswd2" not in request.POST:
    #    return HttpResponseRedirect("?t=err")
    #
    #if request.POST["pswd"] != request.POST["pswd2"]:
    #    return HttpResponseRedirect("?t=c_nomatch")
    #
    #pswd = request.POST["pswd"]
    
    
    blc = 0
    num = localGenerateAccNumber()

    # Username, generated password check
    if len(username) < 6 or len(username) > 32 or not localCheckNoSpecials(username): return HttpResponseRedirect("?t=c_username")
    if not localCheckPassword(pswd): return HttpResponseRedirect("?t=c_password")

    # CHECK IF EXISTS
    try:
       User.objects.get(username=username)
       return HttpResponseRedirect("?t=c_exists")
    except User.DoesNotExist: pass

    print(username)

    user = User.objects.create(username=username)
    user.set_password(pswd)
    user.save()

    acc = Account.objects.create(user=user, balance=blc, num=num)
    acc.save()

    return render(request, "create_finish.html", {"acc":acc, "pswd":pswd})


# 「index.html」
# See the /user/<username>/hello page
@login_required
def vHello(request, username):
    # FAULT: A01:2021-Broken Access Control (IF logged in, user can access any user's data)
    # REMOVE:
    user,acc = localGetAgent(username)
    # FIX:
    #user, acc = localGetAgent(request.user.username)


    if acc is None: return HttpResponse("404!")

    return render(request, "index.html", {"acc":acc})


# 「send.html」
@login_required
def vSend(request, username):
    # FAULT: A01:2021-Broken Access Control (IF logged in, user can access any user's data)
    # REMOVE:
    user,acc = localGetAgent(username)
    # FIX:
    #user, acc = localGetAgent(request.user.username)

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
@login_required
def vSendConfirm(request, username):
    # FAULT: A01:2021-Broken Access Control (IF logged in, user can access any user's data)
    # REMOVE:
    user,acc = localGetAgent(username)
    # FIX:
    #user, acc = localGetAgent(request.user.username)

    receiver = localGetAccountByNumber(request.session["s_receiver"])
    amount = int(request.session["s_amount"])
    message = request.session["s_message"]

    # Create transaction, return "Illegal" if something goes wrong
    if not localTransaction(request, acc, receiver, amount, message):
        return HttpResponse("Illegal!")

    return HttpResponseRedirect("./?t=s_sent")


# 「history.html」
# See the transaction history
@login_required
def vTransactions(request, username):
    # FAULT: A01:2021-Broken Access Control (IF logged in, user can access any user's data)
    # REMOVE:
    user,acc = localGetAgent(username)
    # FIX:
    #user, acc = localGetAgent(request.user.username)

    if acc is None: return HttpResponse("404!")

    transactions = list(Log.objects.filter((Q(acc1=acc) | Q(acc2=acc)) & Q(type="transaction") & Q(hidden=False)).order_by("-id"))
    amounts = []
    messages = []

    # Check if the transaction was done by the user, or received by the user
    for t in transactions:
        s = ""
        try:
            if t.acc1 != acc: s = "+" + t.sdetail1 + "℗"
            else: s = "-" + t.sdetail1 + "℗"
        except:
            s = "ERR"
        amounts.append(s)
        messages.append(t.ldetail.split("\n"))
    
    # Conbine the transactions and amounts
    data = zip(transactions, amounts, messages)

    return render(request, "history.html", {"l":data})



# ADMIN
@user_passes_test(localMustBeAdmin)
def vAdmin(request):
    if (request.user.is_authenticated):
        template = loader.get_template("admin.html")
        return HttpResponse(template.render({}, request))
    
    return HttpResponseRedirect("/login/?next=/admin/")

@user_passes_test(localMustBeAdmin)
def vAdminManage(request):
    template = loader.get_template("admin_manage.html")

    accounts = Account.objects.all()
    return HttpResponse(template.render({"accounts":accounts}, request))

@user_passes_test(localMustBeAdmin)
@transaction.atomic
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

    # FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
    # FIX: 
    # localLog(request, "balance", False, name="Balance Change", acc1=acc, sdetail1=int(balance), ldetail="Balance was changed by the administrator.")

    return HttpResponseRedirect("?t=ok")

@user_passes_test(localMustBeAdmin)
@transaction.atomic
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

    # FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
    # FIX: 
    # localLog(request, "password", False, name="Password Change", sdetail1=user.username)

    return HttpResponseRedirect("?t=ok")

# FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
# FIX: 
#@user_passes_test(localMustBeAdmin)
#def vAdminLogs(request):    
    logs = Log.objects.all().order_by("-id")

    template = loader.get_template("admin_logs.html")
    return HttpResponse(template.render({"logs":logs}, request))

# FAULT: A09:2021-Security Logging and Monitoring Failures (No logging)
# FIX: 
#@user_passes_test(localMustBeAdmin)
#@transaction.atomic
#def vAdminLogsCancel(request, id:int):
    log = localGetLogByID(id)
    if log is None or log.type != "transaction" or log.hidden == True: return HttpResponse("Invalid!")

    # Hide log
    log.hidden = True
    log.save()

    # Refund
    try:
        b = localTransaction(request, log.acc2, log.acc1, int(log.sdetail1), "", "refund", "REFUND", allowNegative=True)
    except:
        b = False

    # If failed, make log visible again
    if b == False:
        log.hidden = False
        log.save()
        return HttpResponse("Invalid!")

    return HttpResponseRedirect("../")
