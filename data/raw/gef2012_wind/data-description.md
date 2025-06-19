## Dataset Description
"train.csv" contains the training data:

- the first column ("date") is a timestamp giving date and time of the hourly wind power measurements in following columns. For instance "2009070812" is for the 8th of July 2009 at 12:00;

- the following 7 columns ("wp1" to "wp7") gather the normalized wind power measurements for the 7 wind farms. They are normalized so as to take values between 0 and 1 in order for the wind farms not to be recognizable.

In parallel, files with explanatory variables (wind forecasts) are also provided for those who may want to use them. For example, the file "windforecasts_wf1.csv" contains the wind forecasts for the wind farm 1. In these files:

- the first column ("date") is a timestamp giving date and time at which the forecasts are issued. For instance "2009070812" is for the 8th of July 2009 at 12:00;

- the second column ("hors") is for the lead time of the forecast. For instance if "date" = 2009070812 and "hors" = 1, the forecast is for the 8th of July 2009 at 13:00

- the following 4 columns ("u", "v", "ws" and "wd") are the forecasts themselves, the first two being the zonal and meridional wind components, while the following two are corresponding wind speed and direction.

Finally, the file "benchmark.csv" provide example forecast results from the persistence forecast method ("what you see is what you get"). This file also gives a template for submission of results that should be strictly followed.
