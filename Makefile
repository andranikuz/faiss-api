# Docker image configuration
DOCKER_USERNAME = andranikuz
IMAGE_NAME = faiss-api
IMAGE_TAG = latest
FULL_IMAGE_NAME = $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)

# Build the Docker image
.PHONY: build
build:
	@echo "Building Docker image: $(FULL_IMAGE_NAME)"
	docker build -t $(FULL_IMAGE_NAME) .
	@echo "✅ Build complete"

# Push image to Docker Hub
.PHONY: push
push: build
	@echo "Pushing image to Docker Hub..."
	docker push $(FULL_IMAGE_NAME)
	@echo "✅ Push complete: $(FULL_IMAGE_NAME)"

# Build and push with version tag
.PHONY: release
release: build
	@echo "Enter version tag (e.g., 1.0.0): "; \
	read VERSION; \
	docker tag $(FULL_IMAGE_NAME) $(DOCKER_USERNAME)/$(IMAGE_NAME):$$VERSION; \
	docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$$VERSION; \
	docker push $(FULL_IMAGE_NAME); \
	echo "✅ Released: $(DOCKER_USERNAME)/$(IMAGE_NAME):$$VERSION and :latest"

# Run locally for testing
.PHONY: run
run:
	docker run -p 8000:8000 \
		-e OPENAI_API_KEY="$${OPENAI_API_KEY}" \
		-e API_TOKEN="$${API_TOKEN}" \
		-e STORAGE_DIR="/app/storage" \
		-v $$(pwd)/storage:/app/storage \
		$(FULL_IMAGE_NAME)

# Login to Docker Hub
.PHONY: login
login:
	docker login

# Clean up local images
.PHONY: clean
clean:
	docker rmi $(FULL_IMAGE_NAME) || true
	@echo "✅ Cleaned local images"

# Build for multiple platforms (ARM64 and AMD64)
.PHONY: buildx
buildx:
	docker buildx create --use --name multiarch || true
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t $(FULL_IMAGE_NAME) \
		--push .
	@echo "✅ Multi-platform build and push complete"

# Help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker image locally"
	@echo "  make push     - Build and push image to Docker Hub"
	@echo "  make release  - Build and push with version tag"
	@echo "  make buildx   - Build for multiple platforms and push"
	@echo "  make run      - Run container locally"
	@echo "  make login    - Login to Docker Hub"
	@echo "  make clean    - Remove local images"
	@echo "  make help     - Show this help message"