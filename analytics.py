def percentage_change(x, y):
    #TODO: this
    
    out = (abs(float(y) - float(x)) /float(x)) *100
    if float(x) > float(y):
        out = out * -1

    return out