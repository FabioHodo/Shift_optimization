import numpy as np
import pandas as pd
import pulp

# Generate variables which represent each members attends or not.
days = 28
employees = 6

var_AM = pulp.LpVariable.dicts("Morning", (range(days), range(employees)), 0, 1, "Binary")
var_PM = pulp.LpVariable.dicts("Night", (range(days), range(employees)), 0, 1, "Binary")
var_Off = pulp.LpVariable.dicts("Off/Leave", (range(days), range(employees)), 0, 1, "Binary")

#objective to maximize shifts worked
obj = None
for i in range(days):
    for j in range(employees):
        obj += var_AM[i][j] + var_PM[i][j]
problem = pulp.LpProblem("shift", pulp.LpMaximize)
problem += obj

# Each employee should work at most one shift per day.
for i in range(days):
    for j in range(employees):
        c = None
        c += var_AM[i][j] + var_PM[i][j] + var_Off[i][j]
        problem += c == 1

# number of shiftee needed
for i in range(0, days):
    c = None
    d = None
    for j in range(employees):
        c += var_AM[i][j]
        d += var_PM[i][j]
    problem += c == 3 # 3 n turn
    e_shtune = [5,12,19,26] # saturdays
    if i in e_shtune:
        problem += d == 1 # on saturdays only 1 shiftee needed
    else:
        problem += d == 2

# balance out morning/night shifts worked and leave
for j in range(employees):
    c = None
    d = None
    for i in range(days):
        c += var_Off[i][j]
        d += var_PM[i][j]
    problem += c >= 5 # 5 min days off every cycle
    problem += c <= 6  # 6 max days off
    problem += d >= 8 # 8 nights min
    problem += d <= 10  # 10 nights max


# if you worked at night, you cannot work the next day or the day after that
for j in range(employees):
    for i in range(days - 1):
        c = None
        c += var_PM[i][j] + var_AM[i+1][j]
        problem += c <= 1

for j in range(employees):
    for i in range(days - 2):
        c = None
        c += var_PM[i][j] + var_AM[i+2][j]
        problem += c <= 1

# Each employee should work at most 6 days per week.
max_consecutive_days = 6
for j in range(employees):
    for i in range(0, days-6):
        c = None
        for w in range(7):
            c += var_AM[i+w][j] + var_PM[i+w][j]
        problem += c <= max_consecutive_days

# Solve problem. Whole tasks is passes pulp framework!
status = problem.solve()
# If pulp can find optimal values which satisfies conditions, print “Optimal”
print("Status", pulp.LpStatus[status])


dic = {}
for v in problem.variables():
    dic[v.name] = v.varValue

df = pd.DataFrame.from_dict(dic, orient='index')

# Reset the index
df = df.reset_index()

# Split the index column into three columns
df[['Time', 'Day', 'Employee']] = df['index'].str.split('_', expand=True)
df = df.drop('index', axis=1)

# Reshape the dataframe using pivot
df = df.pivot(index=['Day','Time'], columns=['Employee'], values=[0])

# Reset the column index
df.columns = df.columns.droplevel()
df = df.reset_index()
# Rename the columns if needed
df.columns.name = None
# Display the resulting dataframe
print(df)
print("Status", pulp.LpStatus[status])


file_path = r"C:\Users\fabio\Downloads\dic.csv" # enter your local path

# Save the dataframe to Excel
df.to_csv(file_path, index=False)