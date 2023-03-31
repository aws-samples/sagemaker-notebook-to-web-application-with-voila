#FROM python:3.9
#EXPOSE 8501
#WORKDIR .
#COPY requirements.txt ./requirements.txt
#RUN pip3 install -r requirements.txt
#COPY test.ipynb .
#CMD  "voila" \
#     "test.ipynb"\
#     "--Voila.ip=0.0.0.0"\
#     "--port=8501"\
#     "--no-browser"
##     "--debug"\
##     "--ExecutePreprocessor.timeout=180"
##voila test.ipynb --port=8501 --debug --no-browser -ExecutePreprocessor.timeout=18
FROM python:3.9
EXPOSE 8501
WORKDIR .
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY test.ipynb .
CMD  "voila" \
     "test.ipynb" \
     "--Voila.ip=0.0.0.0" \
     "--port=8501"\
     "--debug"\
     "--ExecutePreprocessor.timeout=180"
#voila test.ipynb --port=8866 --debug --no-browser -ExecutePreprocessor.timeout=18
#docker run -d -p 8081:8866 testvoila