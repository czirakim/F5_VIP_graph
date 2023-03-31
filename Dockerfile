# Use an official ubuntu image as the base image
FROM ubuntu:latest

# set up bash shell
SHELL ["/bin/bash", "-c"]

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
ENV MY_IP=$MY_IP 
ENV MY_AUTH=$MY_AUTH

# Add the environment variable to .bashrc
RUN echo "export IP_ADDRESS=$MY_IP" >> ~/.bashrc
RUN echo "export Authorization_string=$MY_AUTH" >> ~/.bashrc
RUN source ~/.bashrc

# Run a app when the container is started
CMD ["python3", "app.py"]