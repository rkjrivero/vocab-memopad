# **VOCAB-MEMOPAD**
##### Video Demo:  https://www.youtube.com/watch?v=3mcsAHAYv0A
##### Application URL: https://vocab-memopad.herokuapp.com/
###### Last Updated: 2021/8/04

## Summary:
Vocab-Memopad is a simple web app designed to quickly look up and save the translations of words/phrases and review them online, just like a small memopad to jot down vocabulary entries when studying a language. The application primarily uses Google Translation API (via the googletrans python library) and supports translations across 15 different languages, and is hosted on the heroku platform. Inspired by the Finance problem set, this application primarily uses a database to store word/phrase entries and their corresponding translations, which can be edited and sorted through for review later.


## Ideation:
When an idea for the final project was being sought after, initial exploration was into creating software with applications in either network engineering or project management, as those comprised the other professional fields developing personal specialization in. However, while iterating through different possibilities and going through prior problem set submissions to gauge personal learning capability and plan an appropriate project timeframe, the idea of making a more practical tool reminiscent of the CS50 problem set *Finance* came to mind to mitigate the prerequisite learning curve. Soon after, the inspiration to make an application that stores vocabulary notes reminiscent of my personal notebooks while learning another language came to mind, and thus the initial outline of Vocab-Memopad was drafted out.


## Actuation:
As aforementioned, the core principle of Vocab-Memopad builds entirely upon the application design of the CS50 problem set *Finance*, wherein a web application utilizing the Flask framework is used to receive, recall, and revise data entries within an attached SQL database. In addition, a translation API (namely the *googletrans* python library) is utilized to provide the core translation feature. This is then brought together by an appropriate user interface to get the job done, which is all hosted on an appropriate platform.

### *Heroku Platform Integration*
Heroku was chosen as the platform for the sheer simple reason that a walkthrough to host the CS50 problem set *Finance* was already available *in the form of *https://cs50.readthedocs.io/heroku/* ), and having a known point to spring off from was much needed in the early phase of development, as a personal complete unfamiliarity with general development platforms and practices was proving to become an ever-growing hurdle that was sapping momentum and threatening to stall project progress indefinitely. As such, once a heroku-hosted version of the prior-completed problem set with an attached PostgreSQL database was brought online, the experience was used to create a separate application that would then take apart and redesign the prior problem set components to fulfill the application goals.

### *Imported Libraries*
A majority of the imported libraries are virtually identical from the foundational problem set, only dropping unnecessary libraries such as tempfile’s mkdtemp (which is incompatible with heroku’s ephemeral file system) and helpers.py functions specific to the problem set. New libraries that were imported include googletrans (for google translate API usage) and pytz (for accurate time-stamped data which is later converted to the local time zone of the client).

Initially, there were plans to both utilize SQLAlchemy in lieu of CS50.SQL as well as use a session management method that relies on the database, but over time these were descoped from the project as the timeline got significantly derailed due to a variety of real life incidents that significantly affected available research and development time and energies. Thus, a decision was made to instead stick to CS50.SQL’s library to execute SQL queries, eliminating the learning curve that would have been required to implement the SQLAlchemy engine. Similarly, session management utilizing Flask’s session cookies was retained to do away with the complexity of implementing a database-dependent session management method that was beyond the necessary level of complexity for the project scope.

### *PostgreSQL Database*
A total of three tables are used within the attached PostgreSQL database, the *user* table, the *vocab* table, and the *shadow* table.

The *user* table records user information. Specifically, it records a serially-generated *userid*, a *username* string, a *hash* string for the password, and more application-specific columns, namely strings (*tgtlang*, *orglang*), boolean (*autotrans*), and integers (*pincount*, *wordcount*, *indexpinned*, indexunpinned*, *recallall*, *recallpinned*).

The *vocab* table records user entries. It is comprised of a serially-generated *wordid*, a foreign key *userlink* column, and more application-specific columns such as strings (*strinput*, *strtrans*, *langinput*, *langtrans*), a timestamptz column *time*, an integer column *rating*, and boolean columns *pin* and *edit*.

The *shadow* table is a virtually identical copy of the *vocab* table, with table column names only having a *sha-* name prefix to distinguish them. This table is used as a placeholder table in certain application routes, and is routinely purged in most application routes to keep it empty.

### *Application Routes*
As development of the application progressed, old application routes from the foundational problem set were either modified and repurposed to fulfill new requirements, or dropped altogether with new routes to fulfill desired functionalities created with prior routes serving as a template. Many of these routes have had their functionalities evolve as new features were designed and iterated on throughout the application’s development, and will be expounded on in the succeeding sections.

An application-specific *all_languages[]* dictionary is defined prior to the application routes, and contains the supported languages using the 2-letter keys recognized by googletrans and is referenced regularly in multiple html pages for a dropdown of available languages.

While all applications have functionality-specific actions, a significant number of them share an overlap in three to four basic route actions that the majority of routes do: a) updating the session dictionary’s *current_time* variable for time-keeping purposes (done by all routes aside from /register and /logout which have the session[] dictionary cleared); b) updating the session dictionary’s *last_page* variable that is used by certain “Cancel Action”/”Return” page buttons for contextual return (done specifically by the /login, /index, /recallpin, /recallall, and /profile routes); c) purging the *shadow* table entries for the user on routes that do not use it (only /review and /preview utilize the shadow table); and d) rendering the relevant page html via the “GET” method for the user to interact with the route’s functionality itself. 

### *Register/Login/Logout*
The /register, /login, and /logout routes are heavily based on the foundational code’s routes of the same name, with significant modifications to match the desired functionality.

The /register route, as with the original code, first validates if all the requisite information have been submitted by the user to guard against html form manipulation, checking against application-specific variables. Once all are confirmed and no duplicate username is found, the entries are saved to the *user* table in the database. This is done with a heavily modified *register.html* as the UI, and cannot be accessed via GET while logged in.

The /login route, while working on the same principle as the original code, has several application-specific functionalities such as purging the *shadow* table entries for the user, and establishing a wider range of session[] variables. This is done with a modified *login.html* as the UI, and cannot be accessed via GET while logged in.

The /logout route simply clears the session[] object as well as purging the *shadow* database table. This *shadow* table entries for the user has to be routinely purged in almost every route with a few exemptions to prevent interference with certain application functionalities.

### *Profile/Change Password/Change Default Settings*
The /profile, /changepw, and /changedefault routes are routes that facilitate the manipulation the *user* table of the database.

While the /profile route itself only does all the previously described four basic route actions, the html page serves two main functions - displaying a table that lists relevant user settings, and displaying buttons that link to three separate functionalities: a change default settings function, a change password function, and a function to clear user records.

The /changepw route serves a page that has forms which allow the user to change their password, which is then validated by the application against the *user* table records, then updates that record.

The /changedefault route serves a page that first displays a table of all relevant user settings, has forms and dropdowns for relevant settings, and javascript that first sets said user inputs to user defaults. Once the user has made the relevant changes and clicks on the *Change Default Settings* button, the form and dropdown values are then used to update the relevant *user* table entries and session[] values.

### *Clear Records/Delete Entries/Delete Account*	
The /clearrecords route, which is accessed via the /profile route, itself provides access to the /deleteentries and /deleteaccount actions.

The /clearrecords route, similar to the /profile route that precedes it, renders an html page that displays relevant user settings as well user entry count numbers as tables. Unlike the /profile route however, the corresponding actions, /deleteentries and /deleteaccount, trigger a confirmation modal that pops up which lists relevant numbers as a table as well as a password form for the user to verify their password first before they can proceed with the action.

The /deleteentries route serves to validate the submitted password first, and once confirmed clears all the *vocab* table entries with a foreign key linked to the active user, as well as setting relevant user counters to 0 and redirecting the user to the index/homepage. Attempting to reach this route via GET redirects to /clearrecords instead.

The /deleteaccount route also first validates the submitted password, and once confirmed deletes all user entries from the *vocab* table as well as the user’s account entry on the *user* table, before clearing session[] variables and redirecting to the /login route. Attempting to reach this route via GET redirects to /clearrecords instead.

### *Index/Show Pinned/Show All*
These three route serve to display user-linked entries from the *vocab* table in three different variations. All three routes retrieve user-linked entries that fit each page’s respective categories, which are then rendered through an html page which presents them within separate interactive tables using the DataTables javascript plugin. Each table lists columns for the Input Word/Phrase, the Input Language, the Translated Word/Phrase, the Translation Language, the Date/Time Saved, the Difficulty Rating, the Entry Pinned? column for the /recallall route specifically, as well as the special columns PIN/UNPIN, EDIT, and DELETE which allow the user to do said actions for each entry respectively. The pin/unpin and delete actions bring up a modal for confirmation, which then calls up the /pinentry, /unpinentry, and /deletion routes respectively, while the edit action calls up the /editentry route directly.

The /index route, which also acts the as homepage for the application and borrows elements from the foundational code, first retrieves user information from the *user* table and all user-linked data from the *vocab* table. This route then updates the session[] variables as relevant, creates empty lists *pinvocabtable[]* and *notpinvocabtable[]* and , which are then populated by the first 10 dictionary entries and top 25 dictionary entries from the *vocab* table whose column data for “pin” are tagged as True and False respectively. 

The /recallpin route is almost completely identical in functionality to the /index route, with the sole difference being that all *vocab* table entries for the user whose column data for “pin” tagged True are rendered in a  separate html page that is built in a similar layout. Ditto for the /recallall route, which for its case presents all *vocab* table entries for the user, regardless if it is pinned or unpinned.

### *Input/Review*
These two routes are used in tandem to allow the user to add new entries to the *vocab* table, thus fulfilling the main goal of the application.

The /input route first renders a page that includes a form for the input word/phrase, two dropdowns for the input and translation language which are automatically set to user defaults, a button that allows input and translation language dropdown values to be swapped, a toggle button to select whether to translate the input or not which is also automatically set to user default, and buttons to either submit the selected values or to cancel the search and return to the prior page by redirecting to the value of session[“*last_page*”]. If input is accepted, then the form values are processed by the application.

There is a known rare issue where, despite input being submitted, an Internal Server Error is triggered because a *NoneType* object is being fed to the rest of the input function, but replication has proved tricky, and a flash message to prompt the user to repeat input entry has been set in place as a stopgap.

Assuming the error wasn’t triggered, the values in the page, specifically the input string and selected input and translation languages, are used as input to googletrans’s translator() function, and the output of which are encoded to an empty dictionary. If the option to not translate was selected instead, then an “n/a (not translated)”  entry is inserted instead of a translation. The values of this dictionary are then copied into the *shadow* table in the appropriate format, as well as passed to the /review route. The *shadow* table is designed to act as a volatile memory-analogue, and should ideally only hold one entry for each user at a given time, which is why the entry linked to the user is designed to be deleted during other routes to prevent multiple entries linked to the same user.

The /review route meanwhile first renders a page that shows the entry as it would appear in the database. The user could opt to return to the /input route to insert a new entry instead, or accept the entry. Once accepted, the current entry that is in the *shadow* table that is linked to the user is then cloned into the *user* table itself and the *shadow* table entry for the user purged. Finally, *user* table and session[] variables relating to pincount and wordcount are then updated as appropriate.

There is a known rare issue where the user index for the route list, where the *shadow* table entry is temporarily copied, triggers an out of range error, suspected to be caused by an out-of-order operation when the shadow table entry for the user is purged by another route before the /review route could retrieve it. A flash message to prompt the user to repeat input entry has been set in place as a stopgap, although in the long term a better redesign of the *shadow* table utilization in such a way that the table does not have to be purged in every other route should be considered.

### *Edit Entry/Preview Edit/Revision*
The /editentry and /previewedit routes are modelled after the /input and /review routes, and as such function mostly identical to said routes, with a few relevant modifications. The /revision route, on the other hand, implements the user-specified changes to the *vocab* table data for the selected entry.

The /editentry route, unlike the /input route, is not accessible via GET but instead via POST by clicking on the EDIT column option in the dynamic table entries displayed by the /index, /reviewpinned, and /reviewall routes. This makes a copy of the *vocab* table data linked to that entry, and passes it on to the /previewedit route.

The /previewedit route meanwhile renders a page similar to the /input route’s page, with the same forms, but has default values filled in based on the current entry’s data. If the option to automatically re-translate the input string is activated, then the form which allows the user to edit the database entry is hidden via javascript and the values there are ignored by the route. This option is set by javascript to be either selected or not depending on the user’s default setting preferences. 

Once the relevant changes are encoded, and the input string re-translated in the same manner as the /input route if the option was selected,there is an option to preview the edit, which then passes this data to a page similar to the /review route’s page. This page displays how the edited entry would look. If accepted, this data is then passed on to the /revision route by creating an entry in the *shadow* table route, similar in manner to how the /input route passes data to the /review route.

The /revision route is not accessible via GET and only implements the edits confirmed in the prior /previewedit route via POST. To do so, a copy of the user-linked entry in *shadow* table route is made, which is then used to update the relevant *user* table entry as well as updating the user’s pincount and wordcount in the *user* table and session[] variables as appropriate. 

Just as with the /review route, there is a known rare issue of an out of index error being triggered by out-of-order operations, and identical stopgap measures have been implemented.

### *Delete Check/Deletion*
The /deletecheck and /deletion route previously worked identically to the /previewedit and /revision routes above, but has since been reworked to use a modal pop-up instead akin to the pin/unpin functionality, thus leaving the /deletecheck entry as vestigial. Nonetheless, the application code and html page for /deletecheck route have been retained despite not being called by the DELETE entry column option in entry tables as a backup option that could be utilized/repurposed if necessary.

The /deletion route is now called directly by the pop-up modal that are defined in the html pages for /index, /reviewpinned, and /reviewall routes. This modal shows a table listing the input string, input language, translated string, and translation language. There is an option to cancel the action or to confirm deletion. Choosing the Delete Entry button calls this route, which simply checks the entry if it’s pinned or not, updates the relevant wordcount and pincount variables, and deletes the entry from the *vocab* table, before redirecting to the relevant page as indicated by session[*“last_page”*].

### *Pin Entry/Unpin Entry*
The /pinentry and /unpinentry routes are in all purposes identical to each other, and like the /deletion route are called directly by the pop-up modal that are defined in the html pages for /index, /reviewpinned, and /reviewall routes. They function simply by checking the unique *vocab* table wordid for the relevant entry, updating the pincount as is appropriate, and redirecting the user back to the relevant page as indicated by session[*“last_page”*]. The main differences between the two routes are simply where they redirect and the update to the pincount.

### *About*
The /about route simply brings up the about page, which lists more detailed information about the application. This includes the list of supported languages, known issues and limitations, future plans, disclaimers, the list of utilized technologies, cookie usage and privacy disclaimers, and a link to the application’s github repository.

### *Error Checking/Helpers.py*
The errorhandler code is directly retained from the foundational problem set code, and has been completely untouched.

### *Issues and Limitations*
As discussed in the /review and /preview sections, there is a rare chance for an Internal Server Error to occur while adding a new entry or editing a current entry. This issue is more likely to occur when multiple instances of the application are active and conflicting processes are triggered. Pertinent console logs that show the underlying issue can be found in the application issue tracker in the github repository.

The application UI is currently only designed with desktop browsers in mind, and is not particularly mobile-friendly, primarily due to the current navigation bar and table wrapping setup. Attempts have been made to use a collapsible navigation bar, but prior attempts in getting the bootstrap framework to properly trigger the javascript to do so have so far failed, and the decision to disable the navigation collapse function was done to prevent further deadline slippage. Hopefully, future work on this pet project might figure out the issue.

Translations may not be fully accurate as only the first translation entry returned by the API is currently used, which is an issue for words with multiple valid situational translations. This is especially the case for eastern languages, namely Chinese and Japanese, and specialized translation API’s, such as JishoAPI for Japanese, are being considered as part of future development plans.
