from AE.NN.ANN import ANN


Net = ANN()

Net.add_node(3, IN=True)
Net.add_node(2)
Net.add_node(1, OUT=True)

Net.add_link(0,3)
Net.add_link(1,3)
Net.add_link(2,3)

Net.add_link(1,4)
Net.add_link(2,4)

Net.add_link(3,5)
Net.add_link(4,5)

print(Net)