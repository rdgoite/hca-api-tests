package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.websocket.server.PathParam;
import java.net.URI;
import java.util.UUID;

import static java.lang.String.format;
import static org.springframework.http.MediaType.APPLICATION_JSON_VALUE;

@RestController
@RequestMapping("area")
public class AreaController {

    private static final Logger LOGGER = LoggerFactory.getLogger(AreaController.class);

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private MessageQueue messageQueue;

    @PostMapping(value="/{uuid}", produces=APPLICATION_JSON_VALUE)
    public ResponseEntity<ObjectNode> createUploadArea(
            @PathVariable("uuid") String submissionUuid) {
        LOGGER.info(format("Upload Area creation requested for [%s]...", submissionUuid));
        ObjectNode response = objectMapper.createObjectNode();
        String uploadAreaUuid = UUID.randomUUID().toString();
        String uploadAreaUri = format("s3://org-humancellatlas-upload-dev/%s/", uploadAreaUuid);
        response.put("uri", uploadAreaUri);
        return ResponseEntity.created(URI.create(uploadAreaUri)).body(response);
    }

    @PutMapping("/{areaUuid}/{fileName}/validate")
    public ResponseEntity validateFile(@PathVariable("areaUuid") String areaUuid,
            @PathVariable("fileName") String fileName) {
        LOGGER.info(format("File validation requested for [%s in %s]...", fileName, areaUuid));
        String validationId = UUID.randomUUID().toString();
        ObjectNode response = objectMapper.createObjectNode();
        response.put("validation_id", validationId);
        messageQueue.sendValidationStatus(response.deepCopy());
        return ResponseEntity.ok().body(response);
    }

    @PutMapping(value="/{areaUuid}/files", consumes=APPLICATION_JSON_VALUE)
    public void uploadFile(@PathVariable("areaUuid") String areaUuid,
            @RequestBody FileMetadata file) {
        ObjectNode fileStagedEvent = objectMapper.createObjectNode();
        fileStagedEvent
                .put("url", format("s3://sample-bucket/%s/%s", areaUuid, file.getFileName()))
                .put("name", file.getFileName())
                .put("upload_area_id", areaUuid)
                .put("content_type", file.getContentType());
        messageQueue.sendFileStagedNotification(fileStagedEvent);
    }

}
