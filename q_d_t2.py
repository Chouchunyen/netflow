from gurobipy import *

lacks = ["add","cut"]#增補 or 搬移
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

inc_arcs = [
    ("Incentive","i1"),
    ("Incentive","i2"),
    ("Incentive","i3")]



art_arcs = [
    ("Artificial","i1"),
    ("Artificial","i2"),
    ("Artificial","i3")]

inc_cost = {
    ("add","Incentive","i1"): 8,
    ("add","Incentive","i2"): 8,
    ("add","Incentive","i3"): 8,
    ("cut","Incentive","i1"): 8,
    ("cut","Incentive","i2"): 8,
    ("cut","Incentive","i3"): 8,
}



inflow = {
    ("add","Artificial"): 8190,
    ("add","Incentive"): 8189,
    ("cut","Artificial"): 156,
    ("cut","Incentive"): 156,
    ("add","i1"): -5206,
    ("add","i2"): -6889,
    ("add","i3"): -4284,
    ("cut","i1"): -91,
    ("cut","i2"): -66,
    ("cut","i3"): -155
}

m = Model('netflow')
m.params.NonConvex = 2

#搬運數量
flow = {}
for h in lacks:
    for i,j in arcs:
        flow[h,i,j] = m.addVar(lb=0,ub=capacity[i,j], name='flow_%s_%s_%s' % (h, i, j))

#搬運成本等級
art_cost = {}
for h in lacks:
    for i,j in art_arcs:
        art_cost[h,i,j] =  m.addVar(lb=8, ub=10, vtype=GRB.INTEGER, name='art_cost_%s_%s_%s' % (h, i, j))

m.update()


#m.setObjective(flow['add',"Incentive","i1"]*cost['add',"Incentive","i1"]+flow['add',"Incentive","i2"]*cost['add',"Incentive","i2"]+flow['add',"Incentive","i3"]*cost['add',"Incentive","i3"]+flow['add',"Artificial","i1"]*cost['add',"Artificial","i1"]+flow['add',"Artificial","i2"]*cost['add',"Artificial","i2"]+flow['add',"Artificial","i3"]*cost['add',"Artificial","i3"], GRB.MINIMIZE)
obj = (quicksum(quicksum(flow[h,i,j]*art_cost[h,i,j] for i,j in art_arcs)for h in lacks) + quicksum(quicksum(flow[h,i,j]*inc_cost[h,i,j] for i,j in inc_arcs)for h in lacks))
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
    for i,j in art_arcs:
        m.addGenConstrPWL(flow[h,i,j], art_cost[h,i,j], [0, 6000,  6001,10000], [10, 10, 8, 8])

m.optimize()

# Print solution
print('obj:%d'%m.objVal)
for v in m.getVars():
    print('%s:%d'%(v.varName,v.x))
    