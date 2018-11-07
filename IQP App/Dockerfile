# Use Predix Edge base alpine linux image
FROM dtr.predix.io/predix-edge/alpine-amd64 

#install python3 and the latest pip into the base image
RUN apk update && apk add python3 && pip3 install --upgrade pip

# Set the working directory to /app
WORKDIR /src

# Copy the current directory contents into the container at /src
ADD . /src

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME iqp-edge-app


# Run app.py when the container launches
CMD ["python3", "src/app.py"]

