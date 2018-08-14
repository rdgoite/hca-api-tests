package ingest.humancellatlas.org.mockuploadservice;

import org.springframework.amqp.core.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import static ingest.humancellatlas.org.mockuploadservice.MessageQueue.*;

@SpringBootApplication
public class MockUploadServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(MockUploadServiceApplication.class, args);
	}

	@Bean
	public DirectExchange validationExchange() {
	    return new DirectExchange(EXCHANGE_FILE_VALIDATION);
    }

    @Bean
    public Queue fileValidationQueue() {
	    return new Queue(ROUTING_KEY_FILE_VALIDATION, false);
    }

    @Bean
    public Binding fileValidationBinding() {
        return BindingBuilder.bind(fileValidationQueue())
                .to(validationExchange())
                .with(ROUTING_KEY_FILE_VALIDATION);
    }

    @Bean
    public FanoutExchange fileStagedExchange() {
        return new FanoutExchange(EXCHANGE_FILE_STAGED);
    }

    @Bean
    public Queue fileStagedQueue() {
        return new Queue(ROUTING_KEY_FILE_STAGED, false);
    }

    @Bean
    public Binding fileStagedBinding() {
        return BindingBuilder.bind(fileStagedQueue()).to(fileStagedExchange());
    }

}
