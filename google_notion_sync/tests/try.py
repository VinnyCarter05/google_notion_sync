lst = [0,1,2]
lst2 = [3,4,5]
lst4 = 4

def as_list (variable):
    if type (variable)!= list:
        variable = [variable]
    return variable

lst3 = as_list(lst2)
print (lst3)