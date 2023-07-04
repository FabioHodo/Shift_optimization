import numpy as np
import pandas as pd
import pulp

# Generate variables which represent each members attends or not.
days = 28
employees = 6

var_AM = pulp.LpVariable.dicts("Morning", (range(days), range(employees)), 0, 1, "Binary")
var_PM = pulp.LpVariable.dicts("Night", (range(days), range(employees)), 0, 1, "Binary")
var_Off = pulp.LpVariable.dicts("Leave", (range(days), range(employees)), 0, 1, "Binary")

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
    weekend = [4,5,11,12,18,19,25,26] #tuesday is when the week starts
    if i in weekend:
        problem += c == 2 # on weekends only 2 shiftee needed
    else:
        problem += c == 3
    problem += d == 2  # 2 n turn naten

# balance out morning/night shifts worked and leave
for j in range(employees):
    c = None
    d = None
    for i in range(days):
        c += var_Off[i][j]
        d += var_PM[i][j]
    problem += c >= 6 # 6 min days off every cycle
    problem += c <= 8  # 7 max days off
    problem += d >= 9 # 9 nights min
    problem += d <= 11  # 10 nights max


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

# Each employee should work at most 5 consecutive days.
max_consecutive_days = 6
for j in range(employees):
    for i in range(0, days-2-max_consecutive_days):
        c = None
        for w in range(0,max_consecutive_days):
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
df[['Time', 'Day', 'Employee']] = df['index'].str.split('_', expand=True)
df = df.drop('index', axis=1)
print(df.sort_values(by="Day"))
# Reshape the dataframe using pivot
df = df.pivot(index=['Day','Time'], columns=['Employee'], values=[0])

# Reset the column index
df.columns = df.columns.droplevel()
df = df.reset_index()

df = df.sort_values("Day")

# Create a pivot table to reshape the data
df.rename(columns={"Day": "Day", "Time": "Time", "0":"Employee_0", "1":"Employee_1","2":"Employee_2","3":"Employee_3","4":"Employee_4","5":"Employee_5"}, inplace=True)

print("Status", pulp.LpStatus[status])
print(df.groupby('Time').sum())

file_path = r"C:\Users\fabio\Downloads\dic.csv" # enter your local path
# Save the dataframe to Excel
df.to_csv(file_path, index=False)


######################################################
import matplotlib.pyplot as plt
import seaborn as sns

# Filter the DataFrame for a specific employee (e.g., Employee_0)
for i in range(6):
    # Create a new subfigure
    plt.subplot(3, 2, i+1)  # 2 rows, 3 columns, i+1 represents the position of the subfigure

    employee = 'Employee_' + str(i)
    df_employee = df[['Day', 'Time', employee]].copy()

    # Remove the "Night" time slot from the DataFrame
    df_employee = df_employee[df_employee['Time'] != 'Leave']


    # Create a pivot table to reshape the data
    pivot_table = df_employee.pivot(index='Time', columns='Day', values=employee)

    sns.heatmap(pivot_table, cmap='Blues', cbar=False, linewidths=0.5, linecolor='lightgray')
    plt.title(f'{employee}')
    plt.xlabel('Time')
    plt.ylabel('Day')
    plt.yticks(rotation=0)
    plt.xticks(rotation=0)


plt.subplots_adjust(hspace=0.5, wspace=0.5)  # Increase the values for more spacing
plt.show()
