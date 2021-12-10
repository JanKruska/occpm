<hr style="border:2px solid gray"> </hr>

# Installation  
<hr style="border:2px solid gray"> </hr>
<br />

### Using Docker
<hr style="border:1px solid gray"> </hr>

The code comes with a Dockerfile to build and run the application inside a [docker](https://www.docker.com/) container
To build the container run
```
docker build --rm -t occpm:latest .
```
After the container is build the webapp can be run using
```
docker run -p 8000:8000 occpm
```
### Manual Install
<hr style="border:1px solid gray"> </hr>

#### Environment

When using conda you can create an environment from the provided `environment.yml` by:

```
$ conda env create -f environment.yml
$ conda activate occpm
```

If any dependency is missing please add it and only it to `environment.yml` without specifying a version number and please **do not** use `conda env export > environment.yml` since one should avoid hard references to specific package versions unless explicitly necessary.

##### Static environment

If the environment created from `environment.yml` does not work you can try using `environment_static.yml` (which was created using `conda env export > environment_static.yml`) to obtain an environment with the exact versions used during development, however this is not guaranteed to work across OS's and if possible one should not use out-of-date versions of packages.

#### Running the server

To run the application execute:

```
$ python manage.py runserver
```
<br />
<hr style="border:2px solid gray"> </hr>

# Introduction
<hr style="border:2px solid gray"> </hr>
<br />
The aim of the project is to deliver an easy-to-use graphical Interface for comparative process mining with respect to object-centric event logs. As such it is assumed that users of the product are familiar with the main tenets of process mining, as well as understanding the different challenges in object centric process mining. However, the product should be usable without major programming experience or experience with the process mining library used (pm4py).

The main pipeline of the application works in the following way:

1. After the installation is complete and the server starts successfully, the user can click on the URL to open the application in their browser window. It opens by default onto the "Upload" page.

2. The user first browses for an object-centric event log from their local machine and uploads it to the media directory on the upload page. The log once uploaded, can be downloaded and deleted at any point during the process of the application.

3. The user then “sets” the selected log for first-level log filtering by choosing the respective event and object attributes whose trends they want to examine from the log. Overview statistics are available for all attributes of the log where applicable.

4. We now obtain a filtered event log containing chosen attributes and can progress to the second-level filtering page. The categorical attributes of the log can be selected with approach as “Existence” to 

The project uses existing algorithms for process discovery in the pm4py-mdl package for discovering petri nets and directly-follows graphs as visualizations of the process cube cells. 

<br />
<hr style="border:2px solid gray"> </hr>

# Basic layout of the application  
<hr style="border:2px solid gray"> </hr>
<br />

## Navigation bar
<hr style="border:1px solid gray"> </hr>

Right at the top of the webpage is the navigation bar as a header along with the official logo of the application. It is also visible throughout the workflow and can be used to navigate back-and-forth using these tabs to any part of the project; however some pages are only workable after selection (using "Set") and uploading of an event log from the upload page. 

The functionalities of the various tabs are briefly summarized below:-

#### Upload Tab
<hr style="border:1px solid gray" width="25%"> </hr>

This is the default page that the application opens up to once launched. It contains buttons to upload, set, delete and download event logs. It also displays the uploaded log names in a scrollable field on the webpage that gets updated as the user interacts with the application. 

#### Filtering Tab
<hr style="border:1px solid gray" width="25%"> </hr>

This tab also contains a dropdown for the two levels of filtering in the log navigating to separate webpages:

##### Column Filtering
Refers to the first level of attribute filtering on the log. Gives the user the ability to select and choose from the available event/object type attributes of the log and create a process cube ("Create cubes" button) for the filtered log. This log is then added to the database.

##### Row Filtering
Refers to the second level of attribute value filtering on the log. Here, the user can explicitly specify the Materialization approach, then the column/row whose specific values he wants to select and consequntly filter on their combinations through a "checkbox-table". Process cells are created for analysis. 

#### Visualization Tab
<hr style="border:1px solid gray" width="25%"> </hr>

Displays sliders with parameter adjustments to apply on the selected log and then display a petri net/ directly follows graph based on that.

#### Comparative Tab
<hr style="border:1px solid gray" width="25%"> </hr>

This directs to the page for parallel comparison of two different processes from the log (filtered on different attributes, values etc.) with display of two side-by-side windows for eachof the processes showing their DFGs/ Petri nets.

#### User Manual Tab
<hr style="border:1px solid gray" width="25%"> </hr>

The last tab that displays this user manual for increasing explainability of the whole application workflow to the user. 

<br />
<hr style="border:2px solid gray"> </hr>

# Uploading an event log and other log functionalities
<hr style="border:2px solid gray"> </hr>
<br />
This is the first page the user sees when opening the application. The different components of the page are explained in detail below:

## Upload functionality
<hr style="border:1px solid gray"> </hr>

This constitutes the top section of the upload page. Here, the user can "Browse" for an event log file from their local machine and then click on "Upload" to upload it to the database of the application. Once uploaded, a hyperlink to the file is also displayed below the upload button showing the path to the file. 

## Event log file functionalities 
<hr style="border:1px solid gray"> </hr>

The second half of the upload page contains a box element displaying names of all uploaded logs in the database of the application. Below that, some buttons are provided to interact with the log file:

#### Set button
<hr style="border:1px solid gray" width="25%"> </hr>

the set button sets the event log as "selected" in the application. Once it is set, then only the log can be used with other pages for filtering and visualization etc. 

#### Delete button
<hr style="border:1px solid gray" width="25%"> </hr>

Selecting the log from the list and then clicking on "Delete" removes the log file from the list as well as the database. This has been added to make the log list less crowded as each filtered log in every step of filtering is added to the database. 

#### Download button
<hr style="border:1px solid gray" width="25%"> </hr>

The "Download" button is there to be able to select and download the displayed logs at any point of time according to the user's choice.

*Note: The uploaded log must conform to being of the OCEL standard log and can have the extension of .json or .xml.*

<br />
<hr style="border:2px solid gray"> </hr>

# Filtering of Object-centric Logs
<hr style="border:2px solid gray"> </hr>
<br />

This section describes the filtering functionalities that have been implemented in the application for obejct-centric event logs. Such logs contain (usually) both event-level attributes and certain "object types" as different attributes/columns of the log. The application goes one step further in also allowing the user to select specific values of (categorical) attributes and their combinations for a more detailed and specific analysis of process variants in the log. 

## Selection of first filtering layer with log’s attributes and creating a process cube cell
<hr style="border:1px solid gray"> </hr>

The first filtering describes the "Column filtering" of the log based on event and object type attributes of the OCEL log. The starting text on the page tells you about the number of events and objects contained in the originally selected log. (Remember that this can also be a filtered log, as all original logs and processed ones are collected in the database which the user can access at any time from the upload page).

#### Attributes List
<hr style="border:1px solid gray" width="30%"> </hr>

Next, we have a table showing all event-level attributes of the selected log. The listing starts with event attributes and ends with object types. The user can now select which of these attributes from the list they want to filter on. 

#### Filtering on Object Types
<hr style="border:1px solid gray" width="30%"> </hr>

For the object types, on selecting the checkbox the table for that particular object type is shown containing its attributes that the log can be filtered on which the user can also select. (Notice the dynamic response of the webpage where these "extra" tables disappear once the checkbox is unselected.) 

#### Creating the cubes
<hr style="border:1px solid gray" width="30%"> </hr>

Finally, once the user is happy with his choice of columns, they can name the filtered log to be generated and then click on "Create Cubes" to create the process cube of the filtered log for further analysis.

## Selection of second filtering layer with values of event-level and object-level attributes for detailed analysis
<hr style="border:1px solid gray"> </hr>

On clicking the "Create Cubes" button from the previous section, the user is redirected to the second filtering page; or "Row filtering":

#### Pre-filtered Log Statistics
<hr style="border:1px solid gray" width="40%"> </hr>

In the starting, there is some basic information about the filtered log including the number of its events, objects as well as the list of attributes it was filtered on (so all those that are currently present in the filtered log).

#### Selecting second-level filters
<hr style="border:1px solid gray" width="40%"> </hr>

Here, you find more options of filtering based on the materialization approach (Existence) and also to further sub-divide the cube into a process cell for analysis. You can set the column and row variables (currently available for categorical attributes), displaying each value for those attributes and making it available for selection with a checkbox table. 


<!---
> ### Being able to see a statistical overview of the log’s attributes (filtered/unfiltered)

Upon clicking 
-->

<br />
<hr style="border:2px solid gray"> </hr>

# Visualization of logs as Petri Nets/DFGs with adjustable slider parameters
<hr style="border:2px solid gray"> </hr>
<br />

This section explains the visualization tab view from the application after creating the process cube cells. The visualization basically consists of the following three components:

## (Filtered) Log Information
<hr style="border:1px solid gray"> </hr>

First few lines on the page give details on number of events contained in the log selected for visualization and also tells us what filters were chosen for creating the process cube cell (combinations ofthe "row" and "column" values from the second-layered filtering page table).

## Attribute Tables
<hr style="border:1px solid gray"> </hr>

Display the chosen attributes in tables similar to the ones seen on the first-level "Column" filtering page.

## Visualization diagrams
<hr style="border:1px solid gray"> </hr>

This section contains two sliders for adjusting the **Minimum Edge Frequency** and also the **Minimum Activity Frequency**. The user then has the choice to display the corresponding DFG or Petri Net on the page by clicking on the "Display Frequency DFG" and "Display Performance DFG" buttons for the DFG and "Display Petri Net" button for the petri net.

<br />
<hr style="border:2px solid gray"> </hr>

# Parallel comparison of 2 process cells with visualizations (Petri Nets, DFGs)
<hr style="border:2px solid gray"> </hr>
<br />

Here, 2 different process cells can be created and analysed in parallel with their respective visualizations. Both halves of the webpage work according to the workflow described in the above sections with the same interface.

<br />
<hr style="border:2px solid gray"> </hr>

# Additional Functionalities for Enhanced User Experience
<hr style="border:2px solid gray"> </hr>
<br />

## Attribute Histograms
<hr style="border:1px solid gray"> </hr>

Each of the attributes displayed in the tables are clickable and can be selected to display a histogram representing the trend of that particular feature of the log. This has been added as an additional functionality to increase the interpretability/ explainability of the log and also for enhancing user experience with the interface.

## Bootstrap
<hr style="border:1px solid gray"> </hr>

Instead of just using HTML for the front-end development, webpages have been styled using css stylesheets and bootstrap functionalities for a more attractive user interface.

## Dynamic response on Webpages
<hr style="border:1px solid gray"> </hr>

Some extra highlights and coloured buttons that are highlighted on hover/ selection are present on some webpages that is more user-friendly and interactive. On the filtering page, one can also see that tables appear and disappear on checking certain checkboxes displayed on the page. 