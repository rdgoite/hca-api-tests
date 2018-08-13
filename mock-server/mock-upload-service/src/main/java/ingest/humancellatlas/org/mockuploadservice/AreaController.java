package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.PostConstruct;
import java.net.URI;
import java.util.UUID;

import static java.lang.String.format;

@RestController
@RequestMapping("area")
public class AreaController {

    private static final String EXCHANGE_VALIDATION = "ingest.validation.exchange";
    private static final String ROUTING_KEY_VALIDATION = "ingest.file.validation.queue";

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private ConnectionFactory connectionFactory;

    private RabbitTemplate rabbitTemplate;

    @PostConstruct
    public void setup() {
        rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(new Jackson2JsonMessageConverter());
    }

    @PostMapping(value="/{uuid}", produces=MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ObjectNode> createUploadArea(String submissionUuid) {
        ObjectNode response = objectMapper.createObjectNode();
        String uploadAreaUuid = UUID.randomUUID().toString();
        String uploadAreaUri = format("s3://org-humancellatlas-upload-dev/%s/", uploadAreaUuid);
        response.put("uri", uploadAreaUri);
        return ResponseEntity.created(URI.create(uploadAreaUri)).body(response);
    }

    @PutMapping("/{uploadAreaUuid}/{fileName}/validate")
    public ResponseEntity validateFile(String uploadAreaUuid, String fileName) {
        String validationId = UUID.randomUUID().toString();
        ObjectNode response = objectMapper.createObjectNode();
        response.put("validation_id", validationId);
        sendValidationStatus(response.deepCopy());
        return ResponseEntity.ok().body(response);
    }

    private void sendValidationStatus(ObjectNode validationResult) {
        validationResult.putObject("stdout").putArray("validationErrors");
        rabbitTemplate.convertAndSend(EXCHANGE_VALIDATION, ROUTING_KEY_VALIDATION,
                validationResult);
    }

}
