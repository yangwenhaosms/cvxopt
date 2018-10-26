from gurobipy import *
import numpy as np
def main(m, n, cost, mu, nu, solveparam=None):
    model = Model()
    # Add variables
    var = model.addVars(m, n, lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS)
    # var = []
    # for i in range(m * n):
    #     var.append(model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS))
    # Add constriants
    for j in range(m):
        expr = var.sum(j, '*')
        model.addLConstr(expr, GRB.EQUAL, mu[j])
    for i in range(n):
        expr = var.sum('*', i)
        model.addLConstr(expr, GRB.EQUAL, nu[i])
    # Construct objective, cost should be a dict as cost[i,j]=coef
    obj = var.prod(cost)
    model.setObjective(obj, GRB.MINIMIZE)
    if solveparam == 'intpnt':
        model.setParam('Method', 2)
    elif solveparam == 'simplex':
        model.setParam('Method', 0)
    model.optimize()
    from IPython import embed; embed()

if __name__ == "__main__":
    m = 10
    n = 10
    cost = dict()
    for i in range(m):
        for j in range(n):
            cost[i,j] = (i-j)*(i-j)
    mu = np.random.rand(m)
    mu = mu/sum(mu)
    mu = mu.tolist()
    nu = np.random.rand(n)
    nu = nu/sum(nu)
    nu = nu.tolist()
    solveparam = 'intpnt'
    main(m, n, cost, mu, nu, solveparam)
