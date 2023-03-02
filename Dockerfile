FROM python

# Create directories
RUN mkdir /watch
RUN mkdir /trash

# Copy files
WORKDIR /app
COPY . /app
RUN mkdir /app/data
RUN ln -s /app/data /data

# Start docker
CMD ["python", "main.py"]
