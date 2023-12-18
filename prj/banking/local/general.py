import string
import random

def localCheckNoSpecials(str):
    for c in str:
        if c in string.ascii_letters: continue
        if c in string.digits: continue
        return False
    return True

def localCheckPassword(pswd):
    if len(pswd) < 5: return False
    if " " in pswd: return False
    return True

def localGetNumberStr(num : str):
    rev = ' '.join(string[i:i+len(num)] for i in range(0,len(string),len(num)))
    return rev

def localGeneratePassword():    
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(6))

def localGetErr(request):
    if "t" not in request.GET: return ""
    t = request.GET["t"]

    if   t == "l_invalid":  return "Invalid login credentials, please try again."
    elif t == "c_exists":   return "Username is already in use!"
    elif t == "c_username": return "Username must be between 4 and 32 letters. Username cannot include special characters."
    elif t == "err": return "Unknown error has occured."



def localGetAddress(request):
    forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward:
        return forward.split(',')[0]
    
    return request.META.get('REMOTE_ADDR')
