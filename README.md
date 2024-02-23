# Tabkha
#### Video Demo: [Tabkha - Final Project Demonstration](https://youtu.be/1zEDl0r4RaM) 
#### Description: Tabkha, pronounced as "Tahb-khah", is your gateway to a world of recipes. The name "Tabkha" comes from the Arabic word for "food" or "recipe", which reflects the goal to create a place for all cooking lovers where they can share their favorite recipes with the world.

In this application you can:
1. Create recipes
2. Edit recipes
3. View available recipes
4. Delete recipes 

## Dependancies

-Python 3

To install the ```requirments```:
1. In the root directory ```cd /backend``` 
2. Run ``` pip3 install -r requirments.txt```

## Backend
To run the application locally, you need to create a Postgres database, you can do that with the command ```createdb tabkha```.

Then, update the URI in the ```.env``` file
it should look like this:
```
DATABASE_URL="postgresql://<user>:<password>@localhost:5432/tabkha"
```
Note: You need to create the .env file in the root directory. 

To run the application run these commands in the root directory
```bash
cd /backend
export FLASK_DEBUG="true" # This for development (it's optional)
flask run --reload
``` 

Note: You may need to explicitly specify the the app name, if needed run this:
```bash
export FLASK_APP=app
```

If you get an error ```ModuleNotFoundError``` then, instead of running ```flask run --reload``` try running ```python -m flask run``` this can help ensure that Python treats the project_directory as the root directory for imports.

## Project hierarchy
```bash
. # root directory
├── backend
|   ├── app.py
│   ├── database # models.py is here
│   ├── helpers.py # Helping functions
│   ├── migrations
│   │   └── versions
│   ├── uploads # Uploaded images by the user
│   └── requirments.txt
├──frontend
|   ├── static
|   │   └── styles.css
|   └── templates
│       ├── extended.html # Used to as an initial template to create other templates
│       ├── layout.html # Contains all the html file except the body that will be extended by other templates
│       └── ... # More are more templates
└── README.md
```

## Database Models
Here is the database diagram:

![Markdown Logo](/diagram.png)


## Want to fix a bug? Or perhaps, add a feature?
We are always working on enchancing the users' experience and we are always welcoming your improvments.
If you are intrested in contributing into improving our application then please don't hesitate to.

## AI tools used in building this project
- ChatGPT: Mainly used for the database dummy data generation and ideas inspiration.
- GitHub Copilot: Mainly used for repeated code generation and commenting.

## Authors
Sobhi Abu Hammour
