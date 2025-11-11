import asyncio
import traceback
import redis.asyncio as aioredis
from shopassist_api.domain.models.session_context import SessionContext

async def test_redis_connection(host='localhost', port=6379, password=None, db=0):
    """
    Tests the connection to a Redis server.

    Args:
        host (str): The Redis server hostname or IP address.
        port (int): The Redis server port.
        password (str, optional): The Redis server password. Defaults to None.
        db (int): The database number to connect to. Defaults to 0.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        #r = await aioredis.Redis(host=host, port=port, password=password, db=db)
        r = await aioredis.from_url(
            f"redis://{host}:{port}",
            password=password,
            db=db,
            decode_responses=True
        )
        # The ping() command checks the connection and will raise an exception if invalid.
        response = await r.ping()
        if response:
            print(f"Successfully connected to Redis at {host}:{port}")

            key = "session:1"

            session:SessionContext = SessionContext(**{
                "id": "1",
                "user_id": "user_1",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "messages": [],
                "user_preferences": None,
                "current_intent": None,
                "metadata": {}
            })

            await r.set(key, session.model_dump_json())
            retrieved_value = await r.get(key)
            print(f"Set and retrieved value from Redis: {retrieved_value}")
            
            print("Redis set/get test passed.")

            return True
        else:
            print(f"Failed to connect to Redis at {host}:{port}")
            return False
    except aioredis.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        traceback.print_exc()
        return False
    except aioredis.RedisError as e:
        print(f"Redis error occurred: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Example usage for a local Redis instance without a password
    print("Testing Redis connection...")
    asyncio.run(test_redis_connection())

    # Example usage for a Redis instance with a password (replace with your details)
    # test_redis_connection(host='your_redis_host', port=6379, password='your_redis_password')