#! /usr/bin/python3

N = 2

INDENTATION = " " * 3
system = "system = <"
for i in range(1, N+1):
    system += "Proc P%i, " % i

for i in range(1, N+1):
    system += "Variable Q%i, " % i

for i in range(1, N+1):
    if i != N:
        system += "Variable TURN%i, " % i
    else:
        system += "Variable TURN%i>\n" % i

system += "{\n"

# global Q[n] = 0
# global TURN[n] = 1
system += INDENTATION + "<"
for i in range(1, N+1):
    system += "goSetQ, "
for i in range(1, N+1):
    system += "set0, "
for i in range(1, N+1):
    if i != N:
        system += "set1, "
    else:
        system += "set1>"
system += " -> init;\n"

# for j from 1 to n-1:
for j in range(1, N):
    # Q[i] := j
    for i in range(1, N+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goSetTURN, "
        system += "_, " * (N - i)
        system += "_, " * (i -1)
        system += "set%i, " % j
        system += "_, " * (N - i + N -1)
        system += "_> -> p%i_set_Q%i_%i;\n" % (i, i, j)
    system += "\n"

    # TURN[j] := i
    for i in range(1, N+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goWait, "
        system += "_, " * (N - i + N)
        system += "_," * (j -1)
        system += "set%i, " % i
        for i in range(N -j):
            if i != (N -j -1):
                system += "_, "
            else:
                system += "_"
        system += "> -> p%i_set_TURN%i_%i;\n" % (i, j, i)
    system += "\n"

    # wait until (Vk != i => Q[k] < j) or TURN[j] != i
    for i in range(1, N+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goCritic, " if j == N -1 else "goSetQ, "
        system += "_, " * (N - i + N)
        system += "_," * (j -1)
        system += "isNe%i, " % i
        for it in range(N -j):
            if it != (N -j -1):
                system += "_, "
            else:
                system += "_"
        system += "> -> p%i_unlock_iteration_%i;\n" % (i, j)
        for k in range(1, N):
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goCritic, " if j == N -1 else "goSetQ, "
            system += "_, " * (N - i)
            lt = ["isLt%i" % j] * N
            lt[i -1] = "_"
            system += ", ".join(lt) + ", "
            system += "_, " * (N -1)
            system += "_> -> p%i_unlock_iteration_%i;\n" % (i, j)
    system += "\n"

# Q[i] := 0
for i in range(1, N+1):
    system += INDENTATION + "<"
    system += "_, " * (i -1)
    system += "goSetQ, "
    system += "_, " * (N - i)
    system += "_, " * (i -1)
    system += "set0, "
    system += "_, " * (N - i + N -1)
    system += "_> -> p%i_set_Q%i_0;\n" % (i, i)

system += "};;\n"

print(system)

variable = "Variable = ["
variable += ", ".join(["e%i" % i for i in range(N+1)])
variable += "]\n{\n"
variable += INDENTATION + "etat = %i;\n" % (N+1)
variable += INDENTATION + "init = %s;\n\n" % (", ".join([str(i) for i in range(N+1)]))
for i in range(N+1):
    variable += INDENTATION + "%i = e%i;\n" % (i, i)
variable += "\n"
for i in range(N+1):
    for j in range(N+1):
        transition = "set%i" % j
        if i == j:
            for k in range(N+1):
                if k != i:
                    transition += ", isNe%i" % k
                if k < i:
                    transition += ", isLt%i" % k
        variable += INDENTATION + "%i -> %i [%s];\n" % (i, j, transition)
variable += "};;\n"
print(variable)
