#! /usr/bin/python3

N = 3

def genProcessus(N):
    return """Processus = [setQ, setTURN, wait, critic, end]
{
    etat = 5;
    init = 0;

    0 = setQ;
    1 = setTURN;
    2 = wait;
    3 = critic;
    4 = end;

    0 -> 1 [goSetTURN];
    0 -> 4 [goEnd];
    1 -> 2 [goWait];
    2 -> 3 [goCritic];
    2 -> 0 [goSetQ];
    3 -> 0 [goSetQ];
};;

"""
# print(genProcessus(N))

INDENTATION = " " * 3
def genSystem(N):
    system = "system = <"
    for i in range(1, N+1):
        system += "Processus P%i, " % i

    for i in range(1, N+1):
        system += "VarQ Q%i, " % i

    for i in range(1, N):
        if i != N -1:
            system += "VarTURN TURN%i, " % i
        else:
            system += "VarTURN TURN%i>\n" % i

    system += "{\n"

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
            system += "_, " * (N -i)
            for k in range(1, N):
                if k != (N -1):
                    system += "_, "
                else:
                    system += "_"
            system += "> -> p%i_set_Q%i_%i;\n" % (i, i, j)
        system += "\n"

        # TURN[j] := i
        for i in range(1, N+1):
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goWait, "
            system += "_, " * (N - i + N)
            system += "_," * (j -1)
            system += "set%i" % i
            system += ", _" * (N -j -1)
            system += "> -> p%i_set_TURN%i_%i;\n" % (i, j, i)
        system += "\n"

        # wait until (Vk != i => Q[k] < j) or TURN[j] != i
        for i in range(1, N+1):
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goCritic, " if j == N -1 else "goSetQ, "
            system += "_, " * (N - i + N)
            system += "_," * (j -1)
            system += "isNe%i" % i
            system += ", _" * (N -j -1)            
            system += "> -> p%i_unlock_iteration_%i;\n" % (i, j)
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goCritic, " if j == N -1 else "goSetQ, "
            system += "_, " * (N - i)
            lt = ["isLt%i" % j] * N
            lt[i -1] = "_"
            system += ", ".join(lt) + ", "
            for k in range(1, N):
                if k != (N -1):
                    system += "_, "
                else:
                    system += "_"
            system += "> -> p%i_unlock_iteration_%i;\n" % (i, j)
        system += "\n"

    # Q[i] := 0
    for i in range(1, N+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goSetQ, "
        system += "_, " * (N - i)
        system += "_, " * (i -1)
        system += "set0, "
        system += "_, " * (N - i + N -2)
        system += "_> -> p%i_set_Q%i_0;\n" % (i, i)

    system += "};;\n"
    return system
    
# print(genSystem(N))

def genVarQ(N):
    variable = "VarQ = ["
    variable += ", ".join(["e%i" % i for i in range(N)])
    variable += "]\n{\n"
    variable += INDENTATION + "etat = %i;\n" % (N)
    variable += INDENTATION + "init = 0;\n\n"
    for i in range(N):
        variable += INDENTATION + "%i = e%i;\n" % (i, i)
    variable += "\n"
    for i in range(N):
        for j in range(N):
            transition = "set%i" % j
            if i == j:
                transition += ", is%i" % i
                for k in range(N):
                    if i < k:
                        transition += ", isLt%i" % k
            variable += INDENTATION + "%i -> %i [%s];\n" % (i, j, transition)
    variable += "};;\n"
    return variable
#print(genVarQ(N))

def genVarTURN(N):
    variable = "VarTURN = ["
    variable += ", ".join(["e%i" % i for i in range(1, N+1)])
    variable += "]\n{\n"
    variable += INDENTATION + "etat = %i;\n" % N
    variable += INDENTATION + "init = 0;\n\n"
    for i in range(1, N+1):
        variable += INDENTATION + "%i = e%i;\n" % (i -1, i)
    variable += "\n"
    for i in range(1, N+1):
        for j in range(1, N+1):
            transition = "set%i" % j
            if i == j:
                for k in range(1, N+1):
                    if k != i:
                        transition += ", isNe%i" % k
            variable += INDENTATION + "%i -> %i [%s];\n" % (i -1, j -1, transition)
    variable += "};;\n"
    return variable
# print(genVarTURN(N))

prog = "%s\n%s\n%s\n%s" % (genVarQ(N), genVarTURN(N),
                           genProcessus(N), genSystem(N))
print(prog)

with open("sys.mso", "w") as f:
    f.write(prog)
