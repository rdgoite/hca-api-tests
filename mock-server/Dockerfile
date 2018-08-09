FROM alpine:3.8

RUN apk update && \
    apk add netcat-openbsd

RUN mkdir server
COPY init.sh server/init.sh
COPY response_header.txt server/response_header.txt

RUN chmod +x server/init.sh

ENV RESPONSE_BODY="{}"

EXPOSE 8888

ENTRYPOINT ["/server/init.sh", "8888"]
