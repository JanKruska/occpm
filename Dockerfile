# syntax=docker/dockerfile:1
FROM continuumio/miniconda3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY environment.yml /code/
RUN conda env create -f environment.yml
#Installing fix for django-markdown-view
RUN git clone --depth 50 https://github.com/JanKruska/django-markdown-view && \
    cd django-markdown-view && \
    git checkout 80417bb0416cd4cf9b2903e64c881297f12b60e6 && \
    cd .. && \
    conda run -n occpm pip install -I ./django-markdown-view
COPY . /code/
EXPOSE 8000
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "occpm", "python", "manage.py", "runserver", "0.0.0.0:8000"]
