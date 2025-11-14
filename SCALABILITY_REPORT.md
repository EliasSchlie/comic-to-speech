# Task 6 - Scaling (up) Your System
## Distributed Architecture Implementation Report

### System Architecture

The comic-to-speech processing system has been distributed across three logical server types:

1. **Interface Server** (Server 1) - Handles user requests and coordinates task distribution
2. **Redis Orchestrator** (Server 2) - Manages task queuing and distribution
3. **AI Worker Servers** (Server 3+) - Process OCR and TTS tasks in parallel

Each component runs in isolated Docker containers with dedicated network addresses, simulating deployment across separate physical servers.

---

## Distribution Implementation

### 1. Interface Server
**Location**: `interface_server.py`
**Network**: `172.25.0.20:5001`
**Container**: `Dockerfile.interface`

The interface server receives user requests and submits tasks to Redis queues. It does not perform any AI processing directly.

**Key Features**:
- Accepts comic file uploads via REST API
- Validates file format and size
- Enqueues tasks to Redis without blocking
- Returns task IDs for status tracking
- Retrieves results from Redis when processing completes

**Code Reference**: `interface_server.py:47-89` (upload endpoint), `interface_server.py:125-148` (status endpoint)

### 2. Redis Queue Orchestrator
**Network**: `172.25.0.10:6379`
**Implementation**: Redis 7 with RQ (Redis Queue)

Redis acts as the central message broker, distributing tasks across multiple workers.

**Queue Structure**:
- `ocr` queue - Text extraction tasks
- `tts` queue - Text-to-speech conversion tasks
- `default` queue - General processing tasks

**Configuration**: `config.py:7-10`

### 3. AI Worker Servers
**Workers**: 3 independent instances
**Networks**: `172.25.0.30`, `172.25.0.31`, `172.25.0.32`
**Container**: `Dockerfile.worker`

Each worker connects to Redis and processes tasks independently. Workers can be scaled horizontally by adding more instances.

**Implementation**: `start_worker.py`, `tasks.py`

**Task Processing**:
- `process_comic_ocr()` - Extracts text from comic panels using Google Vision API
- `process_text_to_speech()` - Converts text to audio using Google Text-to-Speech API

Workers listen to all queues and pick up tasks as they become available, enabling automatic load balancing.

---

## Interfacing Between Components

### Communication Architecture

All communication between components uses Redis as a centralized message broker:

**Flow**:
1. Interface Server → Redis (task submission)
2. Redis → Workers (task distribution)
3. Workers → Redis (result storage)
4. Interface Server ← Redis (result retrieval)

**Benefits**:
- Components are loosely coupled
- Workers can be added/removed without interface changes
- Tasks persist in Redis if workers restart
- Automatic retry on failure

### API Design

**Endpoints** (`interface_server.py`):
- `POST /upload` - Submit comic for processing
- `GET /status/<task_id>` - Check processing status
- `GET /result/<task_id>` - Retrieve completed results

**Task State Management**:
```python
# Task submission (interface_server.py:66-70)
job = queue.enqueue('tasks.process_comic_ocr', ...)

# Result retrieval (interface_server.py:134-145)
job = Job.fetch(task_id, connection=redis_conn)
if job.is_finished:
    return job.result
```

### Network Configuration

Docker Compose defines isolated network with static IPs:
```yaml
networks:
  comic_network:
    subnet: 172.25.0.0/16
```

Each service connects using environment variables:
```python
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
```

This configuration allows deployment across physical servers by changing environment variables.

---

## Deployment Configuration

### Docker Implementation

**Files**:
- `docker-compose.yml` - Multi-container orchestration
- `Dockerfile.interface` - Interface server image
- `Dockerfile.worker` - Worker server image

**Key Configuration**:
```yaml
interface:
  networks:
    ipv4_address: 172.25.0.20
  environment:
    - REDIS_HOST=172.25.0.10

worker1:
  networks:
    ipv4_address: 172.25.0.30
  environment:
    - REDIS_HOST=172.25.0.10
```

### Scalability Verification

**Current Deployment**: 1 interface server, 1 Redis instance, 3 AI workers

**Tested Scenarios**:
- Multiple workers processing tasks concurrently
- Worker failure and recovery
- Task queue persistence

**Horizontal Scaling**:
Additional workers can be added by:
```bash
docker-compose up -d --scale worker=5
```

Or by deploying on separate machines with identical worker configuration.

---

## Build and Deployment Issues Resolved

### APT Repository Fixes
Updated Dockerfiles to handle package installation reliably:
```dockerfile
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1
```

### Volume Mounts
Configured shared storage for audio files and temporary images:
```yaml
volumes:
  - ./audio_files:/app/audio_files
  - ./temp_images:/app/temp_images
```

---

## Testing Results

**Status**: All containers running successfully

**Verification**:
```bash
$ docker-compose ps
NAME                     STATUS
comic_interface_server   Up (port 5001)
comic_redis_orchestrator Up (healthy, port 6379)
comic_ai_worker_1        Up
comic_ai_worker_2        Up
comic_ai_worker_3        Up
```

**Worker Logs Confirm**:
- Redis connection established
- Listening on queues: default, ocr, tts
- Ready to process tasks

**Interface Server**: Running at http://localhost:5001

---

## Implementation Notes

### Local vs Cloud Deployment

The current implementation runs on a single machine using Docker containers with separate network addresses. This architecture can be deployed to cloud infrastructure (AWS, GCP, Azure) by:

1. Deploying Redis on dedicated server/managed service
2. Deploying interface server with Redis connection string
3. Deploying worker instances (can scale independently)
4. Updating `REDIS_HOST` environment variable on each server

No code changes required - only configuration updates.

### Production Considerations

For production deployment:
- Use managed Redis service (AWS ElastiCache, Google Memorystore)
- Deploy interface server behind load balancer
- Use container orchestration (Kubernetes, ECS)
- Implement monitoring and logging
- Add authentication and rate limiting

---

## Conclusion

The system successfully implements a distributed architecture with clear separation between interface, orchestration, and processing components. Communication is handled through Redis queues with API-based result retrieval. The architecture supports horizontal scaling by adding worker instances without modifying existing components.

All components are containerized and can be deployed independently on separate servers by updating network configuration.
