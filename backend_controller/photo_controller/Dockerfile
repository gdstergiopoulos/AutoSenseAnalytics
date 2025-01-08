FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#EXPOSE 4943
EXPOSE 4943

# Run photoController.py when the container launches
CMD ["python", "photoController.py"]    

