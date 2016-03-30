import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import re
import datetime
import pylab
import statistics
from tabulate import tabulate
from sklearn import preprocessing

# -------------------------------------------------------------------------- #
# Constants
# -------------------------------------------------------------------------- #
TASK = 'task'
TIME_BISON = 'time_bison'
TIME_PROTO = 'time_proto'
CLICKS_BISON = 'clicks_bison'
CLICKS_PROTO = 'clicks_proto'
BISON = 'bison'
PROTO = 'prototype'
FILE_NAME = 'a7.csv'
SUS_FILE = 'sus.csv'
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
    rects1 = ax.bar(ind, data_bar1, width, color='#006a96') #, yerr=menStd)
    rects2 = ax.bar(ind + width, data_bar2, width, color='#3C3838') #, yerr=womenStd)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ind + width)
    ax.set_xticklabels(xlabels)
    ax.legend((rects1[0], rects2[0]), legends)
    plt.show()


def box_plot (data, title):
    fig, ax = plt.subplots()
    ax.boxplot(data)
   # ax.set_title(title)
    ax.set_xticklabels(['BISON', 'Prototype'])
    plt.show()


def format(dec):
    return '{0:.5f}'.format(dec)

def qqplot(data, title):
    stats.probplot(data, dist="norm", plot=pylab)
    pylab.title(title)
    pylab.show()

# -------------------------------------------------------------------------- #
# Data - Fetching & Cleaning
# -------------------------------------------------------------------------- #
# Data - Fetching
data = pd.read_csv(FILE_NAME, sep=',', na_values= NA_VALUE)
sus_data = pd.read_csv(SUS_FILE, sep=',', na_values= NA_VALUE)
#Data - Cleaning: Converting mm:ss to seconds
data[TIME_BISON] = data[TIME_BISON].apply(to_seconds)
data[TIME_PROTO] = data[TIME_PROTO].apply(to_seconds)
# df = pd.DataFrame(data)
# df.to_csv("a7_time.csv", delimiter=",")

# #normilize
# data = pd.read_csv("a7_time.csv", sep=',', na_values= NA_VALUE)
# data = preprocessing.normalize(data)
# np.savetxt("a7_normalized.csv", data, delimiter=",")
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
tasks_stattest_dict = {}
tasks_time_stattest_dict = []
tasks_clicks_stattest_dict = []
# Group data by tasks

data = data[data['expertise'] == 'Expert']
grouped_by_task = data.groupby(TASK)

# For each task:
# -------------
# (1) Boxplot time/clicks,   Shapiro, QQplots
# (2) Get the means of clicks, time,
# (3) Calculate the t-test paired sample
for task, value in grouped_by_task:
    # (1) Box plots
    box_plot([value[TIME_BISON], value[TIME_PROTO]],
            'Task' + str(task) + ' Time')
    box_plot([value[CLICKS_BISON], value[CLICKS_PROTO]],
            'Task' + str(task) + ' Clicks')

    # Draw qqplot for normalization visualisation
    qqplot(value[TIME_BISON], 'Task' + str(task) + ' Bison Time')
    qqplot(value[TIME_PROTO], 'Task' + str(task) + ' Proto Time')
    qqplot(value[CLICKS_BISON], 'Task' + str(task) + ' Bison Clicks')
    qqplot(value[CLICKS_PROTO], 'Task' + str(task) + ' Proto Clicks')

    # Shapiro normalized test
    print 'Time proto', task
    stat, p = stats.shapiro(value[TIME_PROTO])
    print stat, p
    print 'Time bison', task
    stat, p = stats.shapiro(value[TIME_BISON])
    print stat, p
    print 'Clicks proto', task
    stat, p = stats.shapiro(value[CLICKS_PROTO])
    print stat, p
    print 'Clicks bison', task
    stat, p = stats.shapiro(value[CLICKS_BISON])
    print stat, p
    print '-------------------------------------------------'

    # (2) Save the means
    time_bison.insert(task, value[TIME_BISON].mean())
    time_proto.insert(task, value[TIME_PROTO].mean())
    clicks_bison.insert(task, value[CLICKS_BISON].mean())
    clicks_proto.insert(task, value[CLICKS_PROTO].mean())

    means = [
        task, value[CLICKS_PROTO].mean(),
        value[CLICKS_BISON].mean(),
        value[TIME_PROTO].mean(),
        value[TIME_BISON].mean()
    ]
    tasks_means.append(means)

    # (3) Calculate the Wilcoxon
    #ttest_stat, p_value = stats.ttest_rel(value[TIME_BISON], value[TIME_PROTO] )
    ttest_stat, p_value = stats.wilcoxon(value[TIME_BISON], value[TIME_PROTO])
    p_value = p_value/2  # one tailed
    tasks_stattest_dict['TIME_' + str(task)] = {'t':ttest_stat, 'p_value':p_value}

    tasks_time_stattest_dict.insert(task, p_value)
    # ttest_stat, p_value  = stats.ttest_rel(value[CLICKS_BISON], value[CLICKS_PROTO] )
    ttest_stat, p_value  = stats.wilcoxon(value[CLICKS_BISON], value[CLICKS_PROTO] )
    p_value = p_value/2 # one tailed
    tasks_stattest_dict['CLICKS_' + str(task)] = {'t': ttest_stat, 'p_value':p_value}
    tasks_clicks_stattest_dict.insert(task, p_value)

# sus - Wilcoxon
# ------------------
ttest_stat_sus, p_value_sus  = stats.wilcoxon(sus_data[BISON], sus_data[PROTO] )
p_value_sus = p_value_sus/2 # one tailed
print 'SUS Latest'
print   ttest_stat_sus,   p_value_sus
print 'SUS Bison', stats.shapiro(sus_data[BISON])
qqplot(sus_data[BISON], 'SUS Bison')
print 'SUS Proto', stats.shapiro(sus_data[PROTO])
qqplot(sus_data[PROTO], 'SUS Proto')


# PART 2 - Novice VS. Experts:
# ----------------------------
# Mann WhitneyU : Novice VS. Expert
expertise_mannwhitneyu_dict = {}
novice_data = data[data['expertise'] == 'novice']
experts_data = data[data['expertise'] == 'Expert']

# SHAPIRO Normalisation test
print 'Novice Time', stats.shapiro(novice_data[TIME_BISON])
print 'Expert Time', stats.shapiro(experts_data[TIME_BISON])
print 'Novice Clicks', stats.shapiro(novice_data[CLICKS_BISON])
print 'Expert Clicks', stats.shapiro(experts_data[CLICKS_BISON])

# Box plots
box_plot([experts_data[TIME_BISON], novice_data[TIME_BISON]], 'novice and experts (Time)')
box_plot([experts_data[CLICKS_BISON], novice_data[CLICKS_BISON]], 'novice and experts (Clicks)')

# mann whitney u
t, p = stats.mannwhitneyu(novice_data[TIME_BISON], experts_data[TIME_BISON] )
expertise_mannwhitneyu_dict['NOVICE_EXPERT_TIME'] = {'t': t, 'p_value': p / 2}
t, p = stats.mannwhitneyu(novice_data[CLICKS_BISON], experts_data[CLICKS_BISON])
expertise_mannwhitneyu_dict['NOVICE_EXPERT_CLICKS'] = {'t': t, 'p_value': p / 2}


# -------------------------------------------------------------------------- #
# Show Results
# -------------------------------------------------------------------------- #
# show results of means - Table
print tabulate(tasks_means,
               headers=['Task', 'Prototype Clicks', 'Bison Clicks', 'Prototype Time', 'Bison Time'],
               tablefmt='orgtbl')

# show results - Bar chart of means
print time_bison
print time_proto
plot_bar_chart(4, time_bison, time_proto,
               'Time (sec.)',
               'The Mean Time Taken for Each Task',
               ('Course Search', 'Grades','Exam Search', 'Certificate'),
               ('BISON', 'Prototype')
               )

plot_bar_chart(4, clicks_bison, clicks_proto,
               '# of clicks',
               'The Mean Number of Clicks Taken for Each Task',
               ('Course Search', 'Grades','Exam Search', 'Certificate'),
               ('BISON', 'Prototype')
               )

# ttest pairs
print tasks_stattest_dict

# ttest independent (experts vs. novice)
print expertise_mannwhitneyu_dict

print 'SUS p-value', expertise_mannwhitneyu_dict
print ttest_stat_sus

print 'SUS p-value', format(p_value_sus)
