# health_proj


## Table of Contents

1. [Installation](#installation)
2. [Project Motivation](#motivation)
3. [File Descriptions](#files)
4. [Results](#results)
5. [Resources](#resources)

## Installation <a name="installation"></a>

The following packages are used:

1. `pandas`
2. `numpy`
3. `sklearn`
4. `matplotlib`
5. `math`
6. `zipfile`
7. `datetime`
8. `os`
9. `glob`
10. `sqlite3`
11. `shutil`
12. `re`
13. `sys`
13. `xml`
14. `collections`
14. `statsmodels`
15. `plotly`
16. `seaborn`

The code should run with no issues using Python versions 3.*.

## Project Motivation<a name="motivation"></a>

For this project, I was interestested in using my own data from Apple Health, MyFitnessPal and StepsApp to answer following questions:

1. How can I combine all my health data into one dataset?
2. How does my health data developed over time?
3. How is the correlation between the amount of burned calories and all other variables?
4. Can you predict the amount of burned calories?

Especially the last question could be useful in practice to give fitness geeks like me a guideline how much they can eat to reduce bodyweight or gain muscles.

## File Descriptions <a name="files"></a>
There are three python scripts (`apple_health_data_parser`, `00_data_collecting`, `01_data_cleaning`) which do the preprocessing part of the project.

There are two notebooks (`02_data_analysis`, `03_machine_learning`) which visualize the data analysis and the results of the prediction. Markdown cells were used to assist in walking through the process and documenting the code.

The files have to be executed in the order of the numbering, starting with `00_data_collecting` and ending with `03_machine_learning`. The `apple_health_data_parser` doesn't need to be excecuted specifically, because it will be executed through `00_data_collecting`.

## Results<a name="results"></a>

The main findings of the code can be found at the post available [here](https://medium.com/@kevinossner/whats-inside-my-health-data-44f7fdbf5715).

## Resources<a name="resources"></a>
https://github.com/markwk/qs_ledger/tree/master/apple_health
