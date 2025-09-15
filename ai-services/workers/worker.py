import pika
import os
import sys
import json
import base64
import numpy as np
import cv2
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from face_processor import FaceProcessor

# Load environment variables from .env file
# Assumes .env is in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- SERVICE CONNECTIONS (for local setup) ---
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DATABASE_HOST', 'localhost')

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# --- DATABASE CONNECTION ---
try:
    db_conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    register_vector(db_conn)
    print("AI Worker: Database connection successful.")
except psycopg2.OperationalError as e:
    print(f"AI Worker: Could not connect to the database: {e}")
    exit(1)

# Initialize the Face Processor (loads all AI models)
print("AI Worker: Initializing FaceProcessor... (This may take a moment)")
face_processor = FaceProcessor()
print("AI Worker: FaceProcessor initialized.")

# --- MAIN WORKER LOGIC ---
def process_task(ch, method, properties, body):
    """Callback function to handle incoming tasks from RabbitMQ."""
    task_id = None
    try:
        task = json.loads(body)
        task_id = task.get('task_id')
        task_type = task.get('type')
        image_b64 = task.get('image')

        if not all([task_id, task_type, image_b64]):
            raise ValueError("Task message is missing required fields.")

        # Decode the image
        img_bytes = base64.b64decode(image_b64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # --- Process based on task type ---
        if task_type == 'enroll':
            handle_enrollment(task, frame)
        elif task_type == 'verify':
            handle_verification(task, frame)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        if task_id:
            result = {'status': 'error', 'message': str(e)}
            redis_client.set(task_id, json.dumps(result), ex=3600) # Store error for 1 hour

    ch.basic_ack(delivery_tag=method.delivery_tag)

def handle_enrollment(task, frame):
    """Processes an enrollment request."""
    employee_id = task.get('employee_id')
    if not employee_id:
        raise ValueError("Enrollment task requires 'employee_id'.")

    results = face_processor.process_frame(frame)
    
    live_faces = [r for r in results if r['is_live'] and r['embedding'] is not None]
    
    if len(live_faces) != 1:
        message = f"Enrollment failed: Expected 1 live face, but found {len(live_faces)}."
        raise ValueError(message)

    embedding = live_faces[0]['embedding']
    
    # Save to PostgreSQL
    with db_conn.cursor() as cursor:
        cursor.execute(
            "UPDATE attendance_api_employee SET face_embedding = %s WHERE employee_id = %s",
            (embedding, employee_id)
        )
        db_conn.commit()

    result = {'status': 'success', 'message': f'Employee {employee_id} enrolled successfully.'}
    redis_client.set(task['task_id'], json.dumps(result), ex=3600)
    print(result['message'])

def handle_verification(task, frame):
    """Processes a verification request."""
    results = face_processor.process_frame(frame)
    live_faces_with_embeddings = [r for r in results if r['is_live'] and r['embedding'] is not None]

    if not live_faces_with_embeddings:
        result = {'status': 'failure', 'message': 'No live face detected.'}
        redis_client.set(task['task_id'], json.dumps(result), ex=3600)
        print(result['message'])
        return

    # For simplicity, we verify the first valid face found.
    embedding_to_verify = live_faces_with_embeddings[0]['embedding']
    
    # Search in PostgreSQL using pgvector
    with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT employee_id, first_name, last_name, 1 - (face_embedding <=> %s) AS similarity FROM attendance_api_employee ORDER BY face_embedding <=> %s LIMIT 1",
            (np.array(embedding_to_verify), np.array(embedding_to_verify))
        )
        match = cursor.fetchone()

    # Define a similarity threshold
    SIMILARITY_THRESHOLD = 0.60 

    if match and match['similarity'] > SIMILARITY_THRESHOLD:
        employee_id = match['employee_id']
        # Log attendance
        with db_conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO attendance_api_attendancelog (employee_id, timestamp) VALUES (%s, NOW())",
                (employee_id,)
            )
            db_conn.commit()
        
        result = {
            'status': 'success', 
            'employee_id': employee_id, 
            'name': f"{match['first_name']} {match['last_name']}",
            'similarity': match['similarity']
        }
        print(f"Verification success: Matched {employee_id} with similarity {match['similarity']:.2f}")
    else:
        result = {'status': 'failure', 'message': 'No matching employee found.'}
        print("Verification failed: No match found.")

    redis_client.set(task['task_id'], json.dumps(result), ex=3600)

# --- RABBITMQ CONNECTION SETUP ---
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] AI Worker is waiting for tasks. To exit press CTRL+C')
    
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue='task_queue', on_message_callback=process_task)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

