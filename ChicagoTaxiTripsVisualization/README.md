# Chicago taxi trips visualization

### Summary
The data used for this visualization is a dataset which random samples 10,000 trips from the Chicago Taxi Trip data in the first week of year 2017 (more informaton can be found at https://github.com/wzding/Chicago_taxi_trips). The goal of this visualization is to display the trip volume distribution at different hours of a day during the time of interest. It is obvious that trip distribution has a distinct pattern each day.The overall trip volume drops a large amount from Sunday("01/01") to Monday("01/02"), and increases from Monday to Friday("01/06"), but drops again from Friday to Saturday("01/07").

### Design
* Line plot is selected as one of the chart types because it is useful to show overall changes and patterns, expecially we are dealing with equally spaced intervals of time - different hour of a day. I chose to add scatter plot to line plot to hightlight the values of trip volume at different times. 
* Different time of a day is encoded visually along the x axis, and trip volume is encoded visually along the y axis. Different days are shown as bars on the right of the main chart, with the length of a bar demonstrate the total trip volume of that day and the color of the bar indicate whether a particular day is selected. 
* The layout of this visualization used an online example (shown in the resources section) for reference. 
* Legend is shown on top of the main graph.

After collecting comments from others, I made several changes to the visualization:
* Enlarged the size of the main chart
* Legend seems redundant in this case so I deleted the legend to keep the chart clean and add more readibility.
* Changed the color of the scatter plot as well as the color of the selected date. Using red circles in the scatter plot can draw more attention to them.
* Added the day (weekday or weekend) for each date on the bars.
* Used white and grey rather than blue and orange of the selected date to avoid too many colors of the visualization as well as differentiate the colors of the main chart.
* There are people who felt confused of the length of the bars on the right, but they thought it make sense after I explained it to them. I kept using this visual encoding and added tooltips to make it clearer for the final visualization.
* Placed key findings of the graph below the title.
 
### Feedback
Some feedbacks are collected from four people after they saw the initial visualization:
* The main chart size is too small
* Remove the date on top of the main chart
* The "All" legend is confusing and not necessary
* Better to change the color of the circle to distinguish with the line
* Fix the range of y axis to increase readability
* why the bars on the right have different length? Could you make it clear in the graph?
* add your analysis to the graphic so that it stands alone as an explanatory graphic

### Resources
http://dimplejs.org/advanced_examples_viewer.html?id=advanced_storyboard_control
