def is_unique_scu(self, scu, Prod):
    scu = str(scu)
    try:
        Prod.objects.get(product_code=scu)
        return False
    except:
        return True

def set_num_scu(self, scu, n):
    scu = str(scu)
    while len(scu) <= int(n):
        scu = '0' + scu
    return scu

def get_max_scu(self, Prod):
    codes = Prod.objects.all()
    max_scu = 0
    for code in codes:
        code = int(code.product_code)
        if code > max_scu:
            max_scu = code
    return max_scu
