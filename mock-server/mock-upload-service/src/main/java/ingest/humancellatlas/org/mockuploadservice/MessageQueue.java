package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;

@Component
public class MessageQueue {

    public static final String EXCHANGE_FILE_VALIDATION = "ingest.validation.exchange";
    public static final String ROUTING_KEY_FILE_VALIDATION = "ingest.file.validation.queue";

    public static final String EXCHANGE_FILE_STAGED = "ingest.file.staged.exchange";
    public static final String ROUTING_KEY_FILE_STAGED = "ingest.file.create.staged";


    private static final String DEFAULT_VALIDATION_OUTPUT;
    static {
        StringBuilder outputBuilder = new StringBuilder("{");
        outputBuilder.append("\"validation_errors\": [], \"validation_state\": \"\"");
        outputBuilder.append("}");
        DEFAULT_VALIDATION_OUTPUT = outputBuilder.toString();
    }

    @Autowired
    private ConnectionFactory connectionFactory;

    private RabbitTemplate rabbitTemplate;

    @PostConstruct
    public void setup() {
        rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(new Jackson2JsonMessageConverter());
    }

    public void sendValidationStatus(ObjectNode validationResult) {
        validationResult.put("stdout", DEFAULT_VALIDATION_OUTPUT);
        rabbitTemplate.convertAndSend(EXCHANGE_FILE_VALIDATION, ROUTING_KEY_FILE_VALIDATION,
                validationResult);
    }

    public void sendFileStagedNotification(ObjectNode fileStagedEvent) {
        rabbitTemplate.convertAndSend(EXCHANGE_FILE_STAGED, ROUTING_KEY_FILE_STAGED,
                fileStagedEvent);
    }

}
