file = open('san-diego_california.osm', 'r')
file1 = open("san-diego_sample1.osm","w")

i = 0
for line in file:
    i+=1
    if i < 500000:
        file1.write(line)
file1.write('</osm>')
file1.close()
