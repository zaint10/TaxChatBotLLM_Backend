# Dockerfile
FROM python:3.9


# this ensures that the Python interpreter doesn’t generate .pyc files, we don't need them
ENV PYTHONDONTWRITEBYTECODE 1
# this will send python output straight to the terminal(standard output) without being buffered
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /app

# create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

# set python path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        poppler-utils

# copy requirments file
COPY ./requirements.txt .

# install project dependencies
RUN pip install pip --upgrade && \ 
    pip install --no-cache-dir -r requirements.txt

# copy whole project
COPY . .

# set app port
ENV APP_PORT=8000

# Make scripts executable
RUN chmod +x migrate.sh entrypoint.sh

# expose host
EXPOSE $APP_PORT

CMD ["sh", "-c", "./migrate.sh && ./entrypoint.sh "]