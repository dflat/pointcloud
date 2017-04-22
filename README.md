## execute in shell to set up virtual environment with dependencies ##
```
virtualenv --no-site-packages --distribute .env
source .env/bin/activate 
pip install -r requirements.txt
source flask.env
```

-this will put app in debug mode

-edit db login credentials in *init_db.py*


## to run ##
`flask run --host=0.0.0.0 --port=7000` 

## directory map ##
```
Pointcloud/             : project root
    __init__.py         : contains routing logic

    init_db.py          : teardown and setup mock tables for testing
                        : also contains Models for peewee

    requirements.txt    : dependencies for pip to install
    flask.env           : sets environment variables for flask server

     static/
        /js
            three.js      : local copy of three.js library
            jsonpoints.js : main js code to query database
       
         /css    
            main.css      : basic css stylesheet
   
     templates/
         points.html       : main (and only) html page
```
