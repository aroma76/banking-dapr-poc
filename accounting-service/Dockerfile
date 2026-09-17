# =====================================================
# Accounting Service — Multi-stage Dockerfile
# =====================================================
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src

# Build with Maven wrapper or use the installed mvn
RUN apk add --no-cache maven && \
    mvn clean package -DskipTests -q

# -------------------------------------------------------
FROM eclipse-temurin:17-jre-alpine AS runtime
WORKDIR /app

# Non-root user for security
RUN addgroup -S banking && adduser -S banking -G banking
USER banking

COPY --from=builder /app/target/accounting-service-*.jar app.jar

EXPOSE 8082
ENTRYPOINT ["java", "-jar", "app.jar"]
