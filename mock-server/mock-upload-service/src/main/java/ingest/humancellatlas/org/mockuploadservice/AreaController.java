package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

import static java.lang.String.format;

@RestController
@RequestMapping("area")
public class AreaController {

    @Autowired
    private ObjectMapper objectMapper;

    @PostMapping(value="/{uuid}", produces=MediaType.APPLICATION_JSON_VALUE)
    public JsonNode createUploadArea(String submissionUuid) {
        ObjectNode response = objectMapper.createObjectNode();
        String uploadAreaUuid = UUID.randomUUID().toString();
        response.put("uri", format("s3://org-humancellatlas-upload-dev/%s/", uploadAreaUuid));
        //TODO set to return 201 created response
        return response;
    }

    @PutMapping("/{uploadAreaUuid}/{fileName}/validate")
    public ResponseEntity validateFile(String uploadAreaUuid, String fileName) {
        String validationId = UUID.randomUUID().toString();
        ObjectNode response = objectMapper.createObjectNode();
        response.put("validation_id", validationId);
        return ResponseEntity.ok().body(response);
    }

}
