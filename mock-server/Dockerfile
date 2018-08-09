FROM alpine:3.8

RUN apk update && \
    apk add netcat-openbsd

RUN mkdir server
COPY init.sh server/init.sh
COPY default_response.txt server/default_response.txt

RUN chmod +x server/init.sh

EXPOSE 8888

ENTRYPOINT ["/server/init.sh", "8888"]
