# CS50 Baby Tracker
#### Video Demo:  <URL HERE>
#### Description:

My project is a python flask app that allows a user to track data for one or more babies. This includes, sleeps, feeds, nappy changes and user defined milestones. This data is stored in a sqlite3 database from which a history page for each baby's various event types can be viewed. On each history page a figure is produced using pandas and plotly express to better visualise the data, there is also a table below the figure from which entries can be viewed and deleted. 

This project utilised and built upon some of the code provided in the CS50x week 9 problem set 'Finance'.

## Main Files

### app.py
This is the main file for the Flask application. 

### helpers.py
This file contains some function definitions that are then imported for use in app.py. 

### /templates
This is the directory for the html files utilised by the Flask app. Jinja is utilised across the files to extend the layout.html file and also to show data passed from the flask app routes.

#### layout.html
This template is the base for all the html files, it utilises Jinja syntax by having blocks that the other html templates can then extend. It contains the head information including the charset, the the links to the stylesheet, icon and bootstrap styles and also the page title. 

The body then contains the bootstrap script, the nav bar which has a Jinja if statement to display different menu items depending if a user is logged in or not. Another Jinja if statement to display Flask flashed messages. The main block and finally a footer.

#### register.html & login.html

#### index.html

#### account.html

#### delete_baby.html & delete_user.html

#### feed.html, sleep.html, nappy.html & milestone.html

#### feed_history.html, sleep_history.html, nappy_history.html & milestone_history.html

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


