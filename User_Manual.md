> ## Introduction

The aim of the project is to deliver an easy-to-use graphical Interface for comparative process mining with respect to object-centric event logs. As such it is assumed that users of the product are familiar with the main tenets of process mining, as well as understanding the different challenges in object centric process mining. However, the product should be usable without major programming experience or experience with the process mining library used (pm4py).

The main pipeline of the application works in the following way:

1. The user first browses for an object-centric event log from their local machine and uploads it to the media directory. The log once uploaded, can be downloaded and deleted at any point during the process of the application.

2. The user then “sets” the selected log for first-level log filtering by choosing the respective event and object attributes whose trends they want to examine from the log. Overview statistics are available for all attributes of the log where applicable.

3. We now obtain a filtered event log containing chosen attributes and can progress to the second-level filtering page. The categorical attributes of the log can be selected with approach as “Existence” to 

The project uses existing algorithms for process discovery in the pm4py-mdl package for discovering petri nets and directly-follows graphs as visualizations of the process cube cells. 

> ### Uploading an event log and its other functionalities

This is by default the oprning page of the web application. The different components of the page are explained in detail below:

1. Right at the top of the screen is the visible navigation bar along with the official logo of the application. The user can navigate back-and-forth using these tabs to any part of the project; however some pages are only workable after selection (using "Set") and uploading of an event log from the upload page. 

2. First section of the page gives a browse functionality to the user to select and upload an event log from their local machine. Once uploaded, a hyperlink to the file is also displayed below the upload button showing the path to the file. 

3. The uploaded logs are added one-by-one to the rectangular field displayed where they can be selected to further "Set" for filtering ahead, or for "Delete" to remove them from the server storage. The "Download" button also exists to be able to select and download the displayed logs at any point of time according to the user's choice.

*Note: The uploaded log must conform to being of the OCEL standard log and can have the xtension of .json or .xml.*

> ### Selection of first filtering layer with log’s attributes and creating a process cube cell

The first filtering describes the "Column filtering" of the log based on event and object type attributes of the OCEL log:

1. The first line on the page tells you about the number of events and objects contained in the originally selected log. (Remember that this can also be a filtered log, as all original logs and processed ones are collected in the database which the user can access at any time from the upload page).

2. Next, we have  atbale showing all event-level attributes of the selected log. The listing starts with event attributes and ends with object types. The user can now select which of these attributes from the list they want to filter on. 

3. For the object types, on selecting the checkbox the table for that particular object type is shown containing its attributes that the log can be filtered on which the user can also select. (Notice the dynamic response of the webpage where these "extra" tables disappear once the checkbox is unselected.) 

4. Each of the attributes displayed in the tables are clickable and can be selected to display a histogram representing the trend of that particular feature of the log. This has been added as an additional functionality to increase the interpretability/explainability of the log and also for enhancing user experience with the interface.

5. Finally, once the user is happy with his choice of columns, they can name the filtered log to be generated and then click on "Create Cubes" to create the process cube of the filtered log for further analysis.

<!---
> ### Being able to see a statistical overview of the log’s attributes (filtered/unfiltered)

Upon clicking 
-->

> ### Selection of second filtering layer with values of event-level and object-level attributes for detailed analysis

On clicking the "Create Cubes" button from the previous section, the user is redirected to the second filtering page; or "Row filtering":

1. In the starting, there is some basic information about the filtered log including the number of its events, objects as well as the list of attributes it was filtered on (so all those that are currently present in the filtered log).

2. Here, you find more options of filtering based on the materialization approach (Existence) and also to further sub-divide the cube into a process cell for analysis. You can set the column and row variables (currently available for categorical attributes), displaying each value for those attributes and making it available for selection with a checkbox table. 

> ### Visualization of logs as Petri Nets/DFGs with adjustable slider parameters (frequency,)

> ### Parallel comparison of 2 process cells with visualizations (Petri Nets, DFGs)


