# open file and add 695044 csv data

# id, name

file = open("data.csv", "w")
file.write("id,name\n")
for i in range(695044):
    i = str(i+1)
    file.write(f"{i},name{i}\n")
file.close()