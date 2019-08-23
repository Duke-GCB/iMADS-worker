FROM python:3.7
LABEL maintainer="dan.leehr@duke.edu"

RUN apt-get update && apt-get install -y \
  git \
  r-base

### Step 1: Install the worker and its dependencies
ADD requirements.txt /opt/tf-predictions-worker/
WORKDIR /opt/tf-predictions-worker
RUN pip3 install -r requirements.txt

ADD . /opt/tf-predictions-worker/
ENV PATH /opt/tf-predictions-worker/:$PATH

### Step 3: Install Predict-TF-Binding from GitHub
WORKDIR /opt/
RUN git clone https://github.com/Duke-GCB/Predict-TF-Binding.git predict-tf-binding
RUN pip3 install -r /opt/predict-tf-binding/requirements.txt
ENV PATH /opt/predict-tf-binding/:$PATH

### Step 4: Install Predict-TF-Preference from GitHub
WORKDIR /opt/
RUN git clone https://github.com/Duke-GCB/Predict-TF-Preference.git predict-tf-preference
ENV PATH /opt/predict-tf-preference/:$PATH

# Switch to non-root user
RUN useradd -m worker
USER worker

CMD client.py
