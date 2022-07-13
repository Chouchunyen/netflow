import gurobipy as gp
from gurobipy import GRB

m = gp.Model("test")

quantity = m.addVar(lb=0, ub=100, vtype=GRB.INTEGER, name="quantity")
cost = m.addVar(lb=0, ub=2, vtype=GRB.INTEGER, name="cost")

m.update()

obj = quantity*cost
m.setObjective(obj, GRB.MINIMIZE)

m.addGenConstrPWL(quantity, cost, [5, 9, 10, 100], [2, 2, 1, 1])

m.optimize()

print('obj:%d'%m.objVal)
for v in m.getVars():
    print('%s:%d'%(v.varName,v.x))