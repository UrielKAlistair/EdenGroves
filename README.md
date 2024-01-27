# EdenGroves
An online grocery store built on flask as part of the Modern Application Development 1 Course Project. 

The app lets users buy stuff, and admins to manage the shop. You know, check stocks, sales stats, edit the products available etc. 

To run, just clone the repo, pip -r requirements.txt, and run main.py. Things will just work. 
The page will be hosted at your machines IP and will be accessible from anywhere on the world at that IP:5000, assuming your firewall permits it.

God access credentials for those looking to mess with the app:

Username: Morgan Freeman
Password: ???

Forgotten and Lost to time, so uhm there's actually no easy way I can find it even if I wanted because it's salted and hashed. 
Far easier than making a rainbow table will be to just uncomment and edit some python code in models.py to make yourself god.

This simple app can be analysed with the MVC paradigm, which was central in development ideology as well.

- A SQLite3 Database was used with the Flask-SQLAlchemy python package to make up the model. 
- Flask-RESTful was used to make APIs that furthered the separation of model and controller code. (This was mostly done due to mandates placed by my course project)
- Flask was used to host the webpage, and all pages were templated with Jinja2. CSS was designed with Tailwind classes. This makes up the controller and view code.
