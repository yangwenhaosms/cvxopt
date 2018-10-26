import sys
import mosek
import numpy as np

inf = 0.0

def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def main(m, n, cost, mu, nu, asub, aval, solveparam='intpnt'):
    with mosek.Env() as env:
        with env.Task() as task:
            task.set_Stream(mosek.streamtype.log, streamprinter)
            # Bounds on variables
            bkx = [mosek.boundkey.lo for i in range(m * n)]
            blx = [0.0 for i in range(m * n)]
            bux = [+inf for i in range(m * n)]
            # Bounds on Constraints
            bkc = [mosek.boundkey.fx for i in range(m + n)]
            blc = mu + nu
            buc = mu + nu
            # Objective construction
            c = cost
            numvar = m * n
            numcon = m + n
            # Append num of var and cons
            task.appendcons(numcon)
            task.appendvars(numvar)
            
            # Construct obj
            for j in range(numvar):
                task.putcj(j, c[j])

                task.putvarbound(j, bkx[j], blx[j], bux[j])

                task.putacol(j, asub[j], aval[j])
            
            # Construct constraint
            for i in range(numcon):
                task.putconbound(i, bkc[i], blc[i], buc[i])

            # Max or Min
            task.putobjsense(mosek.objsense.minimize)

            # Optimizer
            if solveparam == 'intpnt':
                task.putintparam(mosek.iparam.optimizer, mosek.optimizertype.intpnt)
            elif solveparam == 'simplex':
                task.putintparam(mosek.iparam.optimizer, mosek.optimizertype.free_simplex)
            task.optimize()

            # Task print
            task.solutionsummary(mosek.streamtype.msg)

            # Solution status
            solsta = task.getsolsta(mosek.soltype.bas)

            if (solsta == mosek.solsta.optimal or 
                solsta == mosek.solsta.near_optimal):
                xx = [0.] * numvar
                task.getxx(mosek.soltype.bas, xx)
                print("Optimal solution: ")
                for i in range(numvar):
                    print("x[" + str(i) + "]=" + str(xx[i]))
            elif (solsta == mosek.solsta.dual_infeas_cer or
                  solsta == mosek.solsta.prim_infeas_cer or
                  solsta == mosek.solsta.near_dual_infeas_cer or
                  solsta == mosek.solsta.near_prim_infeas_cer):
                print("Primal or dual infeasibility certificate found.\n")
            elif solsta == mosek.solsta.unknown:
                print("Unknown solution status")
            else:
                print("Other solution status")

if __name__ == '__main__':
    m = 10
    n = 10
    cost = []
    asub = []
    aval = []
    for i in range(m):
        for j in range(n):
            asub.append([i, m+j])
            aval.append([1.0, 1.0])
            cost.append((i-j)*(i-j))
    mu = np.random.rand(m)
    mu = mu/sum(mu)
    mu = mu.tolist()
    nu = np.random.rand(n)
    nu = nu/sum(nu)
    nu = nu.tolist()
    solveparam = 'intpnt'

    try:
        main(m, n, cost, mu, nu, asub, aval, solveparam)
    except mosek.Error as e:
        print("ERROR: %s" % str(e.errno))
        if e.msg is not None:
            print("\t%s" % e.msg)
            sys.exit(1)

    except:
        import traceback
        traceback.print_exc()
        sys.exit(1)
