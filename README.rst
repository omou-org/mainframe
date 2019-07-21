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

After cloning this repo, install Docker_ for your appropriate operating system and start it up.

If you have Mac, run ``make virtualenv`` to set up virtualenv packages necessary for development. Then run
``make setup`` from this repo to set up everything else!

Don't forget to ``workon mainframe`` before doing anything with the backend. ``deactivate`` will take you out of the virtualenv.
To start the server, run ``python manage.py runserver`` and navigate to ``localhost:8000``.

.. _Docker: https://docs.docker.com/v17.12/install/
