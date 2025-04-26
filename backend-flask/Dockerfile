FROM python:3.10-slim-bullseye

# Inside the container.
# make a new folder inside the container.
WORKDIR /backend-flask

# Outside container --> Inside container
# this contains the libraries want to install to run the app
COPY requirements.txt requirements.txt

# Inside the container
# Install the python libraries.
RUN pip install -r requirements.txt

# Outside the container  --> Inside Container
# . means everything in the current directory
# first period . - /backend-flask (outside container)
# second period . - /backend-flask (inside container)
COPY . .

# Set Enivironment variables (ENV VARS)
# Inside container and will remain set when container is running
ENV FLASK_ENV=development
ENV FLASK_APP=app.py


EXPOSE ${PORT}

# CMD (Command)
# python3 -m flask run --host=0.0.0.0 --port=4527
# -m stand for module
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=4567"]