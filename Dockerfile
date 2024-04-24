# Base image
FROM python:3.9.15-alpine

# Install dependencies
RUN apk upgrade
RUN apk --update \
    add gcc \
    make \
    build-base \
    g++ \
    dumb-init

COPY . /db_alert
WORKDIR /db_alert
RUN pip3 install -r requirements.txt
RUN python3 /db_alert/secrets/setup.py build_ext --inplace
RUN rm -rf /db_alert/secrets
RUN rm -rf /db_alert/build
RUN rm -r ~/.cache/pip


# Listen port
# EXPOSE 9453

# Run the application
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["sh", "-c", "python3 app.py"]