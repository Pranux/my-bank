import difflib

#Name - writen name; Username - real name
def check_name(name, username):
    seq = difflib.SequenceMatcher(None,name,username)
    d = seq.ratio()*100
    return d