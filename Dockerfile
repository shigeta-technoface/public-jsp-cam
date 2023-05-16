FROM python:3.11

# add vim
RUN apt-get update \
    && apt-get install -y --no-install-recommends vim \
    && rm -rf /var/lib/apt/lists/*
# create user
ARG USER_ID
ARG USER_NAME
ARG GROUP_ID
ARG GROUP_NAME
RUN groupadd -g ${GROUP_ID} ${GROUP_NAME} \
    && useradd -m -s /bin/bash -u ${USER_ID} -g ${GROUP_ID} ${USER_NAME}
USER ${USER_ID}:${GROUP_ID}
# create package
COPY . /home/${USER_NAME}/public-jsp-cam/
RUN pip install --disable-pip-version-check --no-cache-dir -r /home/${USER_NAME}/public-jsp-cam/requirements.txt
