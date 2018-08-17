FROM openjdk:10

WORKDIR /java/src/
COPY . .
RUN ./gradlew clean build

FROM openjdk:10-slim

WORKDIR /opt/mock-upload-service/
COPY --from=0 /java/src/build/libs/mock-upload-service-0.0.1-SNAPSHOT.jar ./mock-upload-service.jar
ENV API_VERSION=/v1
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672
CMD java -jar mock-upload-service.jar \
    --server.servlet.context-path=$API_VERSION \
    --spring.rabbitmq.host=$RABBITMQ_HOST \
    --spring.rabbitmq.port=$RABBITMQ_PORT