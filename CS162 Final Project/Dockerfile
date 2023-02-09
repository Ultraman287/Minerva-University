###
FROM python:3.8

# Set the working directory to /web
WORKDIR /web

# Copy the current directory contents into the container at /web
COPY requirements.txt requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

#Get all relevant directories into the container directory
COPY . .

#Here we make the open port an environment variable, with a default development value of 5000
ENV PORT 5000

#We also make the host an environment variable so we can change from localhost to an ip address
#Default to localhost
ENV HOST 0.0.0.0

# Make port 5000 available to the world outside this container
EXPOSE $PORT

# Run app.py when the container launches
CMD python3 -m flask run --host $HOST