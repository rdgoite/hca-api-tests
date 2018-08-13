package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("area")
public class AreaController {

    @Autowired
    private ObjectMapper objectMapper;

    @PostMapping(value="/{uuid}", produces=MediaType.APPLICATION_JSON_VALUE)
    public JsonNode createUploadArea(String uuid) {
        ObjectNode response = objectMapper.createObjectNode();
        response.put("uri",
                "s3://org-humancellatlas-upload-dev/c56ce5ad-0b63-4d3d-b51e-0fcb2b68d661/");
        return response;
    }

}
