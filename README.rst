===================================================
 Main backend service for Omou Learning Platform
===================================================

:Version: 1.0.0
:Source: https://github.com/jerrylinew/omou-backend

About
=====

This is main backend service for Omou Learning Platform

Installation
============

After cloning this repo, install Docker_ for your appropriate operating system and start it up. Also run ``brew install postgresql`` to install Postgres.

If you have a Mac and don't have virtualenv properly configured on your local machine yet, run ``make virtualenv`` to set up virtualenv packages necessary for development. Then run
``make setup`` from this repo to set up everything else! Open a new terminal window before the next step.

Don't forget to ``workon mainframe`` before doing anything with the backend. ``deactivate`` will take you out of the virtualenv.

WINDOWS SETUP:
Clone the repo and install postgres. Create new database named "mainframe", and a new user called admin, with password "password" (don't include the quotes). Install python3 and pip3. run ``pip install virtualenv``. Outside of the repository, run ``virtualenv env``. Then run ``. env\scripts\activate`` Don't forget the . in the beginning. Cd into the project directory and run ``pip install requirements/default.txt``. Go to 'Edit environment variables' by pressing windows key and searching for environment variables. At bottom right, click environment variables. Create new system variable (bottom window), set variable name to DJANGO_ENV_MODULE and set value to mainframe.settings.local, press Ok and Ok. Exit terminal and create new one, if using your editor's terminal, exit entire IDE and restart it. 

To start the server, run ``python manage.py runserver`` and navigate to ``localhost:8000``.

.. _Docker: https://docs.docker.com/v17.12/install/
