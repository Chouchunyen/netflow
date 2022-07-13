from gurobipy import *

lacks = ["add"]#增補 or 搬移
nodes = ["Incentive","Artificial","i1","i2","i3"]

arcs, capacity = multidict({
    ("Incentive","i1"): 10000,
    ("Incentive","i2"): 10000,
    ("Incentive","i3"): 10000,
    ("Artificial","i1"): 10000,
    ("Artificial","i2"): 10000,
    ("Artificial","i3"): 10000
})
#arcs = tuplelist(arcs)
print("this is arcs")
print(arcs)

'''
cost = {
    ("add","Incentive","i1"): 6,
    ("add","Incentive","i2"): 6,
    ("add","Incentive","i3"): 6,
    ("add","Artificial","i1"): 7,
    ("add","Artificial","i2"): 7,
    ("add","Artificial","i3"): 7,
}
'''
inflow = {
    ("add","Artificial"): 8190,
    ("add","Incentive"): 8189,
    ("add","i1"): -5206,
    ("add","i2"): -6889,
    ("add","i3"): -4284,
}

m = Model('netflow')
m.params.NonConvex = 2

#搬運數量
flow = {}
for h in lacks:
    for i,j in arcs:
        flow[h,i,j] = m.addVar(lb=0,ub=capacity[i,j], name='flow_%s_%s_%s' % (h, i, j))

#搬運成本等級
cost = {}
for h in lacks:
    for i,j in arcs:
        cost[h,i,j] =  m.addVar(lb=8, ub=10, vtype=GRB.INTEGER, name='cost_%s_%s_%s' % (h, i, j))

m.update()


#m.setObjective(flow['add',"Incentive","i1"]*cost['add',"Incentive","i1"]+flow['add',"Incentive","i2"]*cost['add',"Incentive","i2"]+flow['add',"Incentive","i3"]*cost['add',"Incentive","i3"]+flow['add',"Artificial","i1"]*cost['add',"Artificial","i1"]+flow['add',"Artificial","i2"]*cost['add',"Artificial","i2"]+flow['add',"Artificial","i3"]*cost['add',"Artificial","i3"], GRB.MINIMIZE)
obj = quicksum(quicksum(flow[h,i,j]*cost[h,i,j] for i,j in arcs)for h in lacks)
m.setObjective(obj,GRB.MINIMIZE)

for i,j in arcs:
    m.addConstr(quicksum(flow[h,i,j] for h in lacks) <= capacity[i,j],
                'cap_%s_%s' % (i, j))


for h in lacks:
    for j in nodes:
        m.addConstr(
          quicksum(flow[h,i,j] for i,j in arcs.select('*',j)) +
              inflow[h,j] ==
          quicksum(flow[h,j,k] for j,k in arcs.select(j,'*')),
                   'node_%s_%s' % (h, j))

for h in lacks:
    for i,j in arcs:
        m.addGenConstrPWL(flow[h,i,j], cost[h,i,j], [0, 4000,  4001,10000], [10, 10, 8, 8])

m.optimize()

# Print solution
print('obj:%d'%m.objVal)
for v in m.getVars():
    print('%s:%d'%(v.varName,v.x))
    