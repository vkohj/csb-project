import string
import random

def localCheckNoSpecials(str):
    for c in str:
        if c in string.ascii_letters: continue
        if c in string.digits: continue
        return False
    return True

def localCheckPassword(pswd):
    # FAULT: A04:2021-Insecure Design (Password is automatically generated, 
    #        and only 6 letters long)

    # REMOVE:
    if len(pswd) < 5: return False
    # FIX:
    # if len(pswd) < 10: return False
    
    # Check if all characters in string are allowed
    for c in str:
        if c in string.ascii_letters: continue
        if c in string.digits: continue
        if c in string.punctuation: continue
        return False

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
    elif t == "c_username": return "Username must be between 6 and 32 letters. Username cannot include special characters."
    elif t == "c_password": return "Password not acceptable. It may be too short or contain illegal characters. Characters allowed include ASCII characters, numbers and punctuation."
    elif t == "c_nomatch": return "The passwords entered do not match."
    elif t == "l_toomany_n": return "Too many attempts. Please wait a few minutes."
    elif t == "l_toomany_r": return "Too many attempts. Please wait a few minutes."
    elif t == "err": return "Unknown error has occured."



def localGetAddress(request):
    if request is None: return ""
    forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward:
        return forward.split(',')[0]
    
    return request.META.get('REMOTE_ADDR')
