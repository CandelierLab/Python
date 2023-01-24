from AE.NN.ANN import ANN

Net = ANN()

Net.add_node(3, IN=True)
Net.add_node(2)
Net.add_node(1, OUT=True)

Net.add_edge(0,3)
Net.add_edge(1,3)
Net.add_edge(2,3)

# Net.add_edge(0,4)
Net.add_edge(1,4)
Net.add_edge(2,4)

Net.add_edge(3,5)
Net.add_edge(4,5)

Net.show(isolate_output=True)