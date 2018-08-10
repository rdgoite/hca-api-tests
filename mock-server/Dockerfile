FROM alpine:3.8

RUN apk update && \
    apk add netcat-openbsd

RUN mkdir server
COPY init.sh server/init.sh
RUN chmod +x server/init.sh

ENV RESPONSE_HEADER="HTTP/1.1 200 OK\nContent-type: application/json"
ENV RESPONSE_BODY="{}"

EXPOSE 8888

ENTRYPOINT ["/server/init.sh", "8888"]
