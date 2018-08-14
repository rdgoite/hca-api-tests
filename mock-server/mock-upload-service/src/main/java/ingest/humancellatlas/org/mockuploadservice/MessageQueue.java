package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;

@Component
public class MessageQueue {

    public static final String EXCHANGE_VALIDATION = "ingest.validation.exchange";
    public static final String ROUTING_KEY_VALIDATION = "ingest.file.validation.queue";

    @Autowired
    private ConnectionFactory connectionFactory;

    private RabbitTemplate rabbitTemplate;

    @PostConstruct
    public void setup() {
        rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(new Jackson2JsonMessageConverter());
    }

    public void sendValidationStatus(ObjectNode validationResult) {
        validationResult.putObject("stdout").putArray("validationErrors");
        rabbitTemplate.convertAndSend(EXCHANGE_VALIDATION, ROUTING_KEY_VALIDATION,
                validationResult);
    }

}
