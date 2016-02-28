from mods import item

myitem = item.item()

def iterations_until_celestial_mahdoton():
	iterations = 0
	while True:
		iterations += 1
		item = myitem.create_item()
		if item["type"] == "Celestial" and item["prefix"] == "Mahdoton":
			print("Got Celestial Mahdoton! Needed " + str(iterations) + " iterations")
			return iterations

def iterations_until_any_mahdoton():
	iterations = 0
	while True:
		iterations += 1
		item = myitem.create_item()
		if item["prefix"] == "Mahdoton":
			print("Got " + item["type"] + " Mahdoton! Needed " + str(iterations) + " iterations")
			return iterations
 
iteration_counts = []
for x in range(1, 100):
	iteration_counts.append(iterations_until_any_mahdoton())

print("Average iteration counts: " + str(sum(iteration_counts) / len(iteration_counts)))