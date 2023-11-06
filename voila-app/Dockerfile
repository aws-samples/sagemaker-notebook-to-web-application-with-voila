FROM python:3.11
EXPOSE 8501
WORKDIR .
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY notebook.ipynb .
CMD  "voila" \
     "notebook.ipynb" \
     "--Voila.ip=0.0.0.0" \
     "--port=8501"\
     "--debug"\
     "--ExecutePreprocessor.timeout=180"
