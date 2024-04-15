# CS50 Baby Tracker
#### Video Demo:  <URL HERE>
#### Description:

My project is a python flask app that allows a user to track data for one or more babies. This includes, sleeps, feeds, nappy changes and user defined milestones. This data is stored in a sqlite3 database from which a history page for each baby's various event types can be viewed. On each history page a figure is produced using pandas and plotly express to better visualise the data, there is also a table below the figure from which entries can be viewed and deleted. 

This project reused and built upon some of the code provided in the CS50x week 9 problem set 'Finance'.

## Main Files

### app.py
This is the main file for the Flask application. It contains the routes for the various pages in the app as well as the database connection and session configuration as was used in 'Finance'

#### index
This function if called via GET looks up the users registered babies in the database and records them in the session object, it then returns the rendered index.html template which shows a table with the users babies. It also has a POST request method which adds the informaiton provided about a new baby to the database and redirects back to the GET route displaying the table with the new baby entered.

#### login
This function clears any session data then if called via post, checks the submitted form information against users in the database and if the username and password are correct, saves the user_id in the session object and redirects the user to the index page.

#### logout
This function simply clears the session information and redirects the user to index.

#### register
WHen called via get the register.html page is rendered and returned. When called via post, the form contents are checked for validity before the information is then added to the database and the user is then logged in and redirected to the index page.

#### account
When called via get this returns the rendered account.html page. When called via post the submitted form is checked and appropriate action taken. Currently there is only a change password form, but others could be added at a later date, such as change username, add email etc.

#### account_delete, baby_delete
These routes render the corresponding delete html pages which serve as confirmation pages for deleteing the user or baby. When called via post this function deletes the user/baby from the database and logs out if user deleted and then in both cases redirects to index.

#### sleep, feed, nappy, milestone
These functions serve to return the corresponding html file when called via GET and then when called via POST they add the submitted information to their appropriate tables in the database.

#### sleep_history, feed_history, nappy_history, milestone_history
These functions return the corresponding rendered history html pages when called via get. This includes calling the related graph function to pass the json file to be rendered. When called via POST these functions delete the chosen line item from their appropriate table in the database.

### helpers.py
This file contains function definitions that are then imported for use in app.py. 

#### apology
This function is re-used from 'Finance' and is used to produce the image that appears when something has gone wrong such as a bad password entered etc.

#### login_required
Again, this is reused from 'Finance' and is used to decorate routes in the main app.py file to redirect users to the login screen when trying to access pages that require a registered user.

#### baby_required
Similar to login_required. This function also wraps routes in app.py to ensure that a user has a baby registered to their account before accessing the pages that require baby information.

#### sort_babies
This function ensures that the currently selected baby in history pages is shown at the top of the dropdown menu to make it more obvious that the data displayed is relating to that baby.

#### feed/sleep/nappy_fig_px
These three funtions use the data provided from the database and turns it in to a numpy array. This data is then manipulated in order to produce the desired chart. Plotly express is then used to produce said chart and return it as a JSON object. Plotly express was chosen over matplotlib or seaborn as it provides appealing, interactive graphics and was straight forward to produce an object that could be displayed on the desired pages.

### /templates
This is the directory for the html files utilised by the Flask app. Jinja is utilised across the files to extend the layout.html file and also to show data passed from the flask app routes.

#### layout.html
This template is the base for all the html files, it utilises Jinja syntax by having blocks that the other html templates can then extend. It contains the head information including the charset, the the links to the stylesheet, icon and bootstrap styles and also the page title. 

The body then contains the bootstrap script, the nav bar which has a Jinja if statement to display different menu items depending if a user is logged in or not. Another Jinja if statement to display Flask flashed messages. The main block and finally a footer.

#### register.html & login.html
These files are similar and serve to allow the user to login or register themselves in the app. They extend the layout html and are simple form pages.

#### index.html
This page generates a table to show the users registered babies, along with buttons to add or delete them if desired. The table data is generated using a jinja for loop to iterate through the babies passed to the page by the flask route. The delete button directs the user to the delete confirmation page while the add button submits the form data. The date of birth selection is restricted by a javascript script that sets the max value to be the current date while also formatting the submitted date to the ISO format.

#### account.html
This page is a simple form to allow the user to change their password, there is then a button to direct the user to the account deletion page if desired.

#### delete_baby.html & delete_user.html
These pages serve as confirmation pages before deleting the baby/user. They display a warning that the action is irreversible and show a small red confirmation button and a large cancel button that returns them to the homepage.

#### feed.html, sleep.html, nappy.html & milestone.html
These pages are forms to allow the user to submit the corresponding data in to the database. They are structured similarly and include form fields to allow the user to enter the appropriate information depending on which page they are on.

The feed page utilises javascript to dynamically change the style of the fields, hiding or showing the appropriate ones depending on if bottle or breast feed are selected. They all also use javascript to format and limit the possible times that can be submitted.

#### feed_history.html, sleep_history.html, nappy_history.html & milestone_history.html
These pages display a dropdown of the users babies at the top, an event listener javascript is then used to re-render the page if the selection is changed. Below this dropdown the chosen babies data is shown, this includes a chart for (excluding milestone_history) and a table which utlises a jinja for loop to display all the data entries for the selected baby with a form button on each row to allow the user to delete the corresponding entry. This table is given the scrolllable class, this limits the size on the page while allowing all the data to be seen as it can be scrolled through.

### static

#### baby.png
This is the icon image for the website

#### styles.css
This includes additional styling to the bootstrap used for certain elements in some of the pages. Particularly formatting of items on the various history pages, such as making the data tables scrollable and setting the maximum width of the plots.

### schema.sql
This SQL file contains the schema for the app's database. Within it are a number of SQL statements to create the 6 tables that are then queried by the app. The tables are as follows:

#### users
This table has 3 columns to store the login information of the users:
* user_id, an integer which is also the primary key.
* username, a varchar of length 30 which has the not null and unique constraints as it is used by the user to login. If there were 2 entries of the same value they could not be used to identify the user_id and password hash.
* hash, a text column to store the hash value of the user's password.

#### babies
This table stores the primary information about the babies:
* baby_id, an integer primary key for the table.
* baby_name, a varchar of length 30 that is not null.
* birthdate, a date not null object.
* gender, a varchar of length 11 that can be either 'Male', 'Female' or 'Unspecified'.
* user_id, a foreign key linking the baby to a user.

#### sleeps
This table stores information about babies' sleeps:
* sleep_id, an integer primary key.
* baby_id, a foreign key linking the recorded sleep to a baby.
* start_time, a timestamp object that is not null.
* end_time, a timestamp object that is not null.
* duration_minutes, an integer recording the duration in minutes of the sleep/nap.

#### nappy_changes
This table stores information about babies' nappies:
* change_id, an integer primary key.
* baby_id, foreign key linking the nappy to a baby.
* timestamp, a timestamp of the nappy change.
* wet, a boolean type showing if the nappy was wet or not.
* dirty, a boolean type showing if the nappy was dirty/soiled or not.
* nappy_size a varchar of length 1 storing S, M or L to denote if the nappy contents were small, medium or large. If unspecified it defaults to NULL.

#### feeds
This table stores information about babies' feeds:
* feed_id, an integer primary key.
* baby_id, a foreign key linking the feed to a baby.
* timestamp, a timestamp of the feed.
* type, a varchar of length 6 storing eith Bottle or Breast.
* quantity_ml, an integer to store the quantity of milk in a bottle feed.
* duration_minutes, an integer to record the length of time of a breast feed.

#### milestones
This table stores information about babies' milestones:
* milestone_id, an interger primary key.
* baby_id, foreign key to link the milestone to a baby.
* description, a text type to store the user defined milestone.
* timestamp, a timestamp of when the milestone was achieved.

Where there is a foreign key in a table, a condition is specified that if the referenced user/baby is deleted, all entries with that user/baby will also be deleted from the database. For example if a user deletes their account, their babies and any recorded events linked to those babies will also be deleted.


