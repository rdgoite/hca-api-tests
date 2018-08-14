package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.util.UUID;

import static java.lang.String.format;

@RestController
@RequestMapping("area")
public class AreaController {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private MessageQueue messageQueue;

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
        messageQueue.sendValidationStatus(response.deepCopy());
        return ResponseEntity.ok().body(response);
    }

}
