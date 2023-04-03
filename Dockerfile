# Use an official ubuntu image as the base image
FROM ubuntu:latest

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3.10 python3-pip

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the packages listed in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Jenkins on port 8080
EXPOSE 8080

# Set the environment variable
ARG MY_IP
ARG MY_AUTH
ENV IP_ADDRESS=$MY_IP 
ENV Authorization_string=$MY_AUTH

# Run a app when the container is started
CMD ["python3", "app.py"]