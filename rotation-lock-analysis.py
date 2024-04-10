"""
File: rotation-lock-analysis.py
Author: Chuncheng Zhang
Date: 2024-04-10
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Analysis the results of the rotation-lock experiment

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-10 ------------------------
# Requirements and constants
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path


# %% ---- 2024-04-10 ------------------------
# Function and class


# %% ---- 2024-04-10 ------------------------
# Play ground
if __name__ == '__main__':
    df = pd.read_csv(Path('./rotation-lock.csv'), index_col=0)

    fig, axs = plt.subplots(2, 1)

    ax = axs[0]
    ax.grid()
    sns.boxplot(df, y='passed', hue='use_contextlib', ax=ax)

    ax = axs[1]
    ax.grid()
    sns.boxplot(df, y='buffer_size', hue='use_contextlib', ax=ax)
    fig.tight_layout()
    plt.show()

    group = df.groupby('use_contextlib')
    print('--------------------')
    print(group['passed'].mean())
    print('--------------------')
    print(group['buffer_size'].mean())

    # print(df)


# %% ---- 2024-04-10 ------------------------
# Pending


# %% ---- 2024-04-10 ------------------------
# Pending
