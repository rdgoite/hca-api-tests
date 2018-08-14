package ingest.humancellatlas.org.mockuploadservice;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import static ingest.humancellatlas.org.mockuploadservice.MessageQueue.EXCHANGE_VALIDATION;
import static ingest.humancellatlas.org.mockuploadservice.MessageQueue.ROUTING_KEY_VALIDATION;

@SpringBootApplication
public class MockUploadServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(MockUploadServiceApplication.class, args);
	}

	@Bean
	public DirectExchange validationExchange() {
	    return new DirectExchange(EXCHANGE_VALIDATION);
    }

    @Bean
    public Queue fileValidationQueue() {
	    return new Queue(ROUTING_KEY_VALIDATION, false);
    }

    @Bean
    public Binding fileValidationBinding() {
        return BindingBuilder.bind(fileValidationQueue())
                .to(validationExchange())
                .with(ROUTING_KEY_VALIDATION);
    }

}
