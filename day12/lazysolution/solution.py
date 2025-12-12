parts = open("input.txt").read().split("\n\n")
shapes = [p.count("#") for p in parts[:6]]
ratios = [sum(int(c)*s for c,s in zip(line.split(": ")[1].split(), shapes)) /
          eval(line.split(":")[0].replace("x","*")) for line in parts[6].strip().split("\n")]
print(sum(r < (sum(ratios)/len(ratios)) for r in ratios))
