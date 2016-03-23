import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import re
import datetime
from tabulate import tabulate

# -------------------------------------------------------------------------- #
# Constants
# -------------------------------------------------------------------------- #
TASK = 'task'
TIME_BISON = 'time_bison'
TIME_PROTO = 'time_proto'
CLICKS_BISON = 'clicks_bison'
CLICKS_PROTO = 'clicks_proto'
FILE_NAME = 'a7.csv'
NA_VALUE = '0'


# -------------------------------------------------------------------------- #
# Helpers
# -------------------------------------------------------------------------- #
def to_seconds(t):
    m,s = re.split(':',t)
    seconds = int(datetime.timedelta(minutes=int(m),seconds=int(s))
                  .total_seconds())
    return seconds


def plot_bar_chart(n, data_bar1, data_bar2, ylabel, title, xlabels, legends):
    ind = np.arange(n)
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, data_bar1, width, color='b') #, yerr=menStd)
    rects2 = ax.bar(ind + width, data_bar2, width, color='y') #, yerr=womenStd)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ind + width)
    ax.set_xticklabels(xlabels)
    ax.legend((rects1[0], rects2[0]), legends)
    plt.show()


def box_plot (data, title):
    fig, ax = plt.subplots()
    ax.boxplot(data)
    ax.set_title(title)
    plt.show()


def format(dec):
    return '{0:.5f}'.format(dec)
# -------------------------------------------------------------------------- #
# Data - Fetching & Cleaning
# -------------------------------------------------------------------------- #
# Data - Fetching
data = pd.read_csv(FILE_NAME, sep=',', na_values= NA_VALUE)
# Data - Cleaning: Converting mm:ss to seconds
data[TIME_BISON] = data[TIME_BISON].apply(to_seconds)
data[TIME_PROTO] = data[TIME_PROTO].apply(to_seconds)

# -------------------------------------------------------------------------- #
# Data - Processing
# -------------------------------------------------------------------------- #

# PART 1 - Task Analysis:
# -----------------------

# Vars
tasks_means = []
time_bison = []
time_proto = []
clicks_bison = []
clicks_proto = []
tasks_ttest_dict = {}
tasks_time_ttest_dict = []
tasks_clicks_ttest_dict = []
# Group data by tasks
### data = data[data['expertise'] == 'novice']
grouped_by_task = data.groupby(TASK)

# For each task:
# -------------
# (1) Boxplot time/clicks,
# (2) Get the means of clicks, time,
# (3) Calculate the t-test paired sample
for task, value in grouped_by_task:
    # (1) Box plots
    box_plot([value[TIME_BISON], value[TIME_PROTO]],
            'Task' + str(task) + ' Time')
    box_plot([value[CLICKS_BISON], value[CLICKS_PROTO]],
            'Task' + str(task) + ' Clicks')

    # (2) Save the means
    time_bison.append(value[TIME_BISON].mean())
    time_proto.append(value[TIME_PROTO].mean())
    clicks_bison.append(value[CLICKS_BISON].mean())
    clicks_proto.append(value[CLICKS_PROTO].mean())

    means = [
        task, value[CLICKS_PROTO].mean(),
        value[CLICKS_BISON].mean(),
        value[TIME_PROTO].mean(),
        value[TIME_BISON].mean()
    ]
    tasks_means.append(means)

    # (3) Calculate the t-test paired sample
    ttest_stat, p_value = stats.ttest_rel(value[TIME_BISON], value[TIME_PROTO] )
    p_value = p_value/2  # one tailed
    #tasks_ttest_dict['TIME_' + str(task)] = {'ttest_stat':ttest_stat, 'p_value':p_value}

    tasks_time_ttest_dict.insert(task, p_value)
    ttest_stat, p_value  = stats.ttest_rel(value[CLICKS_BISON], value[CLICKS_PROTO] )
    p_value = p_value/2 # one tailed
    #tasks_ttest_dict['CLICKS_' + str(task)] = {'ttest_stat': ttest_stat, 'p_value':p_value}
    tasks_clicks_ttest_dict.insert(task, p_value)

tasks_ttest_dict['TIME'] = tasks_time_ttest_dict
tasks_ttest_dict['CLICKS'] = tasks_clicks_ttest_dict

# PART 2 - Novice VS. Experts:
# ----------------------------
# ttest independent : Novice VS. Expert
expertise_ttest_ind_dict = {}
novice_data = data[data['expertise'] == 'novice']
experts_data = data[data['expertise'] == 'Expert']
box_plot([experts_data[TIME_BISON], novice_data[TIME_BISON]], 'novice and experts')
box_plot([experts_data[CLICKS_BISON], novice_data[CLICKS_BISON]], 'novice and experts')
t, p = stats.ttest_ind(novice_data[TIME_BISON], experts_data[TIME_BISON],equal_var=False )
expertise_ttest_ind_dict['NOVICE_EXPERT_TIME'] = {'ttest_stat': t, 'p_value':p/2}
t, p = stats.ttest_ind(novice_data[CLICKS_BISON], experts_data[CLICKS_BISON],equal_var=False )
expertise_ttest_ind_dict['NOVICE_EXPERT_CLICKS'] = {'ttest_stat': t, 'p_value':p/2}

# -------------------------------------------------------------------------- #
# Show Results
# -------------------------------------------------------------------------- #
# show results of means - Table
print tabulate(tasks_means,
               headers=['Task', 'Prototype Clicks', 'Bison Clicks', 'Prototype Time', 'Bison Time'],
               tablefmt='orgtbl')

# show results - Bar chart of means
plot_bar_chart(4, time_bison, time_proto,
               'Time (sec.)',
               'The mean of time taken for each task',
               ('Task 1', 'Task 2', 'Task 3', 'Task 4'),
               ('BISON', 'Prototype')
               )

plot_bar_chart(4, clicks_bison, clicks_proto,
               '# of clicks',
               'The mean of number of clicks for each task',
               ('Task 1', 'Task 2', 'Task 3', 'Task 4'),
               ('BISON', 'Prototype')
               )

# ttest pairs
print tasks_ttest_dict
## Output
#{'TIME_4': {'p_value': 0.0019461150331658817, 'ttest_stat': array(3.4516015577315913)}, 'TIME_1': {'p_value': 0.00026443859375419097, 'ttest_stat': array(4.469844450734681)}, 'TIME_2': {'p_value': 0.044775090508509405, 'ttest_stat': array(1.8241009901323422)}, 'TIME_3': {'p_value': 0.0035975052158679363, 'ttest_stat': array(3.1427193137481666)}, 'CLICKS_2': {'p_value': 0.0080660592945765754, 'ttest_stat': array(2.734377913310204)}, 'CLICKS_3': {'p_value': 0.0069484412872638486, 'ttest_stat': array(2.8102560762812057)}, 'CLICKS_1': {'p_value': 0.00015596136320071178, 'ttest_stat': array(4.747490811377417)}, 'CLICKS_4': {'p_value': 0.00017550130544991013, 'ttest_stat': array(4.685015164181178)}}
#only novice --> {'TIME_4': {'p_value': 0.0037246973859562816, 'ttest_stat': array(3.960276708308093)}, 'TIME_1': {'p_value': 0.010471343359195169, 'ttest_stat': array(3.106477773709748)}, 'TIME_2': {'p_value': 0.039875843139679963, 'ttest_stat': array(2.1065549393871805)}, 'TIME_3': {'p_value': 0.028586241188708603, 'ttest_stat': array(2.3485392923120467)}, 'CLICKS_2': {'p_value': 0.013389759087523075, 'ttest_stat': array(2.9157373664724853)}, 'CLICKS_3': {'p_value': 0.046185931838798627, 'ttest_stat': array(2.0004252604768453)}, 'CLICKS_1': {'p_value': 0.010656353778825157, 'ttest_stat': array(3.0927549724742005)}, 'CLICKS_4': {'p_value': 0.0059660784104922831, 'ttest_stat': array(3.5596528070971436)}}

# ttest independent (experts vs. novice)
print expertise_ttest_ind_dict
#{'NOVICE_EXPERT_CLICKS': {'p_value': 0.020290647369952619, 'ttest_stat': array(2.126975542413645)}, 'NOVICE_EXPERT_TIME': {'p_value': 0.0071760661115828081, 'ttest_stat': array(2.582157230208339)}}




print "{:<8} {:<10} {:<10} {:<10} {:<10} {:<25}".format('', 'Task 1','Task 2','Task 3', 'Task 4', 'Experts VS. Novice')
for k, v in tasks_ttest_dict.iteritems():
    print "{:<8} {:<10} {:<10} {:<10} {:<10}".format(k, format(v[0]), format(v[1]),format(v[2]),format(v[3]))