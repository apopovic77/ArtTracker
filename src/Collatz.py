



def collatz(n):
    if n % 2 == 0:
        return n/2
    else:
        return n*3+1
    



n=25032423766765767645665665665565555555566777
i = 0
while True:
    i+=1
    n = collatz(n)
    print(n)
    if n == 1:
        break
print("Steps "+str(i))

max_int = pow(2,31)
max_long = pow(2,63)
print("max_int "+str(max_int)+" max_long "+str(max_long))