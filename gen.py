#! /usr/bin/python3

from sys import argv

N = int(argv[1]) if len(argv) >= 2 else 3

def capitalize(word):
    """
    return the word with first letter as capital letter
    """
    return word[0].upper() + word[1:]

def gen_processus(nb_process):
    """
    generate Processus automaton
    """
    processus = "Processus = [%s, critic, end]\n{\n" % ", ".join([
        "setQ%i, setTURN%i, wait%i" % (i, i, i) for i in range(1, nb_process)
    ])
    processus += INDENTATION + "etat = %i;\n" % (3 * (nb_process -1) + 2)
    processus += INDENTATION + "init = 0;\n\n"

    for_statement = ["setQ%i", "setTURN%i", "wait%i"]
    states = []
    for i in range(1, nb_process):
        for statement in for_statement:
            states.append(statement % i)

    states.append("critic")
    states.append("end")
    for i in range(len(states)):
        processus += INDENTATION + "%i = %s;\n" % (i, states[i])
    processus += "\n"

    for i in range(len(states) -2):
        processus += INDENTATION + "%i -> %i [go%s];\n" % (i, i +1,
                                                           capitalize(
                                                               states[i+1]))

    processus += INDENTATION + "%i -> %i [go%s];\n" % (len(states) -2, 0,
                                                       capitalize(states[0]))
    processus += INDENTATION + "%i -> %i [go%s];\n" % (0, len(states) -1,
                                                       capitalize(states[-1]))

    processus += "};;"
    return processus

INDENTATION = " " * 3

def gen_system_header(nb_process):
    """
    generate system = <Processus P1, ..., VarQ Q1, .., VarTURN TURN1, ..>
    """
    system = "system = <"
    for i in range(1, nb_process +1):
        system += "Processus P%i, " % i

    for i in range(1, nb_process +1):
        system += "VarQ Q%i, " % i

    for i in range(1, nb_process):
        system += "VarTURN TURN%i, " % i

    system = system[:-2] + ">\n"
    return system

def gen_go_end(nb_process):
    """
    generate `<goEnd, _, ...> -> p%i_end;` step
    """
    system = ""
    for i in range(nb_process):
        system += INDENTATION + "<"
        tab = ["_"] * nb_process
        tab[i] = "goEnd"
        system += ", ".join(tab)
        system += ", "
        system += ", ".join(["_"] * (nb_process + nb_process -1))
        system += "> -> p%i_end;\n" % (i +1)
    return system

def gen_qi_set(nb_process, j):
    """
    generate Q[i] := j; statement
    """
    system = ""
    for i in range(1, nb_process+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goSetTURN%i, " % j
        system += "_, " * (nb_process - i)
        system += "_, " * (i -1)
        system += "set%i, " % j
        system += "_, " * (nb_process -i)
        for _ in range(1, nb_process):
            system += "_, "
        system = system[:-2]
        system += "> -> p%i_set_Q%i_%i;\n" % (i, i, j)
    return system

def gen_turnj_set(nb_process, j):
    """
    generate TURN[j] := i; statement
    """
    system = ""
    for i in range(1, nb_process+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goWait%i, " % j
        system += "_, " * (nb_process - i + nb_process)
        system += "_, " * (j -1)
        system += "set%i" % i
        system += ", _" * (nb_process -j -1)
        system += "> -> p%i_set_TURN%i_%i;\n" % (i, j, i)
    return system

def gen_system(nb_process):
    """
    generate :
    for j from 1 to n-1:
        Q[i] := j;
        TURN[j] := i;
        wait until (Vk != i => Q[k] < j) or TURN[j] != i
    Critic
    Q[i] := 0
    """
    system = gen_system_header(nb_process)
    system += "{\n"
    system += gen_go_end(nb_process)
    system += "\n"

    # for j from 1 to n-1:
    for j in range(1, nb_process):
        # Q[i] := j
        system += gen_qi_set(nb_process, j)
        system += "\n"

        # TURN[j] := i
        system += gen_turnj_set(nb_process, j)
        system += "\n"

        # wait until (Vk != i => Q[k] < j) or TURN[j] != i

        for i in range(1, N+1):
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goCritic, " if j == N -1 else "goSetQ%i, " % (j +1)
            system += "_, " * (N - i)
            var_q = ["_"] * N
            # var_q[i -1] = "is%i" % j
            system += ", ".join(var_q) + ", "
            system += "_, " * (j -1)
            system += "isNe%i" % i
            system += ", _" * (N -j -1)
            system += "> -> p%i_unlock_iteration_%i;\n" % (i, j)
            system += INDENTATION + "<"
            system += "_, " * (i -1)
            system += "goCritic, " if j == N -1 else "goSetQ%i, " % (j +1)
            system += "_, " * (N - i)
            lower_than = ["isLt%i" % j] * N
            lower_than[i -1] = "_"
            system += ", ".join(lower_than) + ", "
            for _ in range(1, N):
                system += "_, "
            system = system[:-2]
            system += "> -> p%i_unlock_iteration_%i;\n" % (i, j)
        system += "\n"

    # Q[i] := 0
    for i in range(1, nb_process+1):
        system += INDENTATION + "<"
        system += "_, " * (i -1)
        system += "goSetQ1, "
        system += "_, " * (nb_process - i)
        system += "_, " * (i -1)
        system += "set0, "
        system += "_, " * (nb_process - i + nb_process -1)
        system = system[:-2]
        system += "> -> p%i_set_Q%i_0;\n" % (i, i)

    system += "};;\n"
    return system

def gen_var_j(nb_process):
    """
    generate VarJ automaton
    """
    variable = "VarJ = ["
    variable += ", ".join(["e%i" % i for i in range(1, nb_process)])
    variable += "]\n{\n"
    variable += INDENTATION + "etat = %i;\n" % (nb_process -1)
    variable += INDENTATION + "init = 0;\n\n"
    for i in range(1, nb_process):
        variable += INDENTATION + "%i = e%i;\n" % (i -1, i)
    variable += "\n"
    for i in range(1, nb_process):
        variable += INDENTATION + "%i -> %i [is%i];\n" % (i -1, i -1, i)
        if i < nb_process -1:
            variable += INDENTATION + "%i -> %i [set%i];\n" % (i -1, i, i +1)
        else:
            variable += INDENTATION + "%i -> %i [set%i];\n" % (i -1, 0, 0)
    variable += "};;\n"
    return variable

def gen_var_q(nb_process):
    """
    generate VarQ automaton
    """
    variable = "VarQ = ["
    variable += ", ".join(["e%i" % i for i in range(nb_process)])
    variable += "]\n{\n"
    variable += INDENTATION + "etat = %i;\n" % (nb_process)
    variable += INDENTATION + "init = 0;\n\n"
    for i in range(nb_process):
        variable += INDENTATION + "%i = e%i;\n" % (i, i)
    variable += "\n"
    for i in range(nb_process):
        for j in range(nb_process):
            transition = "set%i" % j
            if i == j:
                transition += ", is%i" % i
                for k in range(nb_process):
                    if i < k:
                        transition += ", isLt%i" % k
            variable += INDENTATION + "%i -> %i [%s];\n" % (i, j, transition)
    variable += "};;\n"
    return variable

def gen_var_turn(nb_process):
    """
    generate VarTURN automaton
    """
    variable = "VarTURN = ["
    variable += ", ".join(["e%i" % i for i in range(1, nb_process+1)])
    variable += "]\n{\n"
    variable += INDENTATION + "etat = %i;\n" % nb_process
    variable += INDENTATION + "init = 0;\n\n"
    for i in range(1, nb_process+1):
        variable += INDENTATION + "%i = e%i;\n" % (i -1, i)
    variable += "\n"
    for i in range(1, nb_process+1):
        for j in range(1, nb_process+1):
            transition = "set%i" % j
            if i == j:
                for k in range(1, nb_process+1):
                    if k != i:
                        transition += ", isNe%i" % k
            variable += INDENTATION + "%i -> %i [%s];\n" % (i -1, j -1,
                                                            transition)
    variable += "};;\n"
    return variable

def gen_bug_verif(nb_process):
    """
    generate CTL bug path
    """
    bugs = "bug1 = system -> AX(false) && (%s);;\n" % " || ".join([
        "P%i.wait%i" % (i, nb_process -1) for i in range(1, nb_process+1)])

    critics = []
    for i in range(1, nb_process):
        for j in range(i +1, nb_process+1):
            critics.append("(P%i.critic && P%i.critic)" % (i, j))
    bugs += "bug2 = system -> %s;;\n" % " || ".join(critics)
    bugs += """\ntodot dot/nprocess_bug1.dot bug1;;
todot dot/nprocess_bug2.dot bug2;;"""
    return bugs

def gen_ltl(nb_process):
    """
    generate ltl automaton
    """
    ltl = "load ltl_sys.mso;;\n"
    ltl += "S = automaton system;;\n\n"

    critics = []
    for i in range(1, nb_process):
        for j in range(i +1, nb_process+1):
            critics.append("(P%i.critic && P%i.critic)" % (i, j))

    ltl += "em = S && exclusion_mutuelle[p <- %s];;\n" % " || ".join(critics)
    ltl += "exmut = reduce em;;\n\n"

    ltl += "ef = S && equite_forte[a <- P1.wait%i, b <- P1.critic];;\n" % (
        nb_process -1)
    ltl += "eqfort = reduce ef;;\n\n"

    ltl += """todot dot/nprocess_ltl_eqfort.dot eqfort;;
todot dot/nprocess_ltl_exmut.dot exmut;;"""

    return ltl

PROG = "%s\n%s\n%s\n%s\n%s\n%s\n" % (gen_var_q(N), gen_var_turn(N),
                                     gen_processus(N), gen_system(N),
                                     gen_bug_verif(N), gen_ltl(N))
print(PROG)

with open("sys.mso", "w") as f:
    f.write(PROG)
