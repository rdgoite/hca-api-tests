package ingest.humancellatlas.org.mockuploadservice;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class MockUploadServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(MockUploadServiceApplication.class, args);
	}

	@Bean
	public DirectExchange validationExchange() {
	    return new DirectExchange("ingest.validation.exchange");
    }

    @Bean
    public Queue fileValidationQueue() {
	    return new Queue("ingest.file.validation.queue", false);
    }

    @Bean
    public Binding fileValidationBinding() {
        return BindingBuilder.bind(fileValidationQueue())
                .to(validationExchange())
                .with("ingest.file.validation.queue");
    }

}
