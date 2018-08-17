package ingest.humancellatlas.org.mockuploadservice;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown=true)
public class FileMetadata {

    private final String fileName;
    private final String contentType;

    @JsonCreator
    public FileMetadata(@JsonProperty("fileName") String fileName,
            @JsonProperty("contentType") String contentType) {
        this.fileName = fileName;
        this.contentType = contentType;
    }

    public String getFileName() {
        return fileName;
    }

    public String getContentType() {
        return contentType;
    }

}
