# anthropic-context-sessions-complete-retry.py

from anthropic import Anthropic, APIError, InternalServerError, APITimeoutError
import json
import os
from datetime import datetime
import uuid
import time
import logging
import random
from typing import Optional, Dict, Any, List
import dotenv

dotenv.load_dotenv()

api_key = os.getenv('api-key')
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnthropicError(Exception):
    """Custom exception class for Anthropic-specific errors."""
    pass


class RetryConfig:
    """Configuration class for API retry mechanism.

    Args:
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Initial delay between retries in seconds
        max_delay (float): Maximum delay between retries in seconds
        exponential_base (float): Base for exponential backoff calculation
        jitter (bool): Whether to add randomization to delay times
    """

    def __init__(self,
                 max_retries: int = 5,
                 base_delay: float = 1.0,
                 max_delay: float = 30.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay time for current retry attempt.

        Args:
            attempt (int): Current retry attempt number

        Returns:
            float: Delay time in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        if self.jitter:
            delay = delay * (0.5 + random.random())
        return delay


class ContextualChatbot:
    """A chatbot that maintains conversation context and handles API communication with Anthropic.

    This class provides functionality to:
    - Create and manage conversation contexts
    - Store and retrieve conversation history
    - Handle API communication with retry mechanism
    - Maintain system prompts and knowledge base

    Args:
        api_key (str): Anthropic API key
        context_file (str): Path to file for storing contexts
        retry_config (RetryConfig, optional): Configuration for retry mechanism
    """

    def __init__(self,
                 api_key: str,
                 context_file: str = "contexts.json",
                 retry_config: Optional[RetryConfig] = None):
        self.client = Anthropic(api_key=api_key)
        self.context_file = context_file
        self.system_prompt = ""
        self.messages = []
        self.context_id = None
        self.retry_config = retry_config or RetryConfig()

    def _load_all_contexts(self) -> Dict[str, Any]:
        """Load all saved contexts from the context file.

        Returns:
            dict: Dictionary of all saved contexts
        """
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading contexts: {str(e)}")
            return {}

    def _save_context(self, context_data: Dict[str, Any]):
        """Save context data to the context file.

        Args:
            context_data (dict): Context data to save
        """
        try:
            contexts = self._load_all_contexts()
            contexts[self.context_id] = context_data
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(contexts, f, ensure_ascii=False, indent=2)
            logger.info(f"Context successfully saved: {self.context_id}")
        except Exception as e:
            logger.error(f"Error saving context: {str(e)}")
            raise

    def _update_current_context(self):
        """Update current context in the context file."""
        if self.context_id:
            context_data = {
                "id": self.context_id,
                "name": f"Context-{self.context_id[:8]}",
                "created_at": datetime.now().isoformat(),
                "system_prompt": self.system_prompt,
                "messages": self.messages
            }
            self._save_context(context_data)

    def _make_api_request(self, func, *args, **kwargs):
        """Make API request with retry mechanism.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Response from the API

        Raises:
            AnthropicError: If all retry attempts fail
        """
        attempt = 0
        last_error = None

        while attempt < self.retry_config.max_retries:
            try:
                return func(*args, **kwargs)
            except (InternalServerError, APITimeoutError) as e:
                attempt += 1
                last_error = e

                if attempt == self.retry_config.max_retries:
                    logger.error(f"Maximum retry attempts reached ({self.retry_config.max_retries})")
                    break

                delay = self.retry_config.get_delay(attempt)
                logger.warning(
                    f"API error (attempt {attempt}/{self.retry_config.max_retries}): {str(e)}. "
                    f"Waiting {delay:.2f}s before next attempt"
                )
                time.sleep(delay)
            except APIError as e:
                logger.error(f"Non-retryable API error: {str(e)}")
                raise AnthropicError(f"API error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

        raise AnthropicError(f"All retry attempts failed. Last error: {str(last_error)}")

    def create_new_context(self, name: Optional[str] = None) -> str:
        """Create a new conversation context.

        Args:
            name (str, optional): Name for the context

        Returns:
            str: ID of the created context
        """
        try:
            self.context_id = str(uuid.uuid4())
            self.messages = []
            self.system_prompt = ""

            context_data = {
                "id": self.context_id,
                "name": name or f"Context-{self.context_id[:8]}",
                "created_at": datetime.now().isoformat(),
                "system_prompt": self.system_prompt,
                "messages": self.messages
            }

            self._save_context(context_data)
            logger.info(f"New context created: {self.context_id}")
            return self.context_id
        except Exception as e:
            logger.error(f"Error creating context: {str(e)}")
            raise

    def load_context(self, context_id: str) -> bool:
        """Load an existing context by ID.

        Args:
            context_id (str): ID of the context to load

        Returns:
            bool: True if context was loaded successfully, False otherwise
        """
        try:
            contexts = self._load_all_contexts()
            if context_id in contexts:
                context_data = contexts[context_id]
                self.context_id = context_id
                self.system_prompt = context_data["system_prompt"]
                self.messages = context_data["messages"]
                logger.info(f"Context loaded successfully: {context_id}")
                return True
            logger.warning(f"Context not found: {context_id}")
            return False
        except Exception as e:
            logger.error(f"Error loading context: {str(e)}")
            raise

    def set_system_prompt(self, prompt: str):
        """Set the system prompt for the current context.

        Args:
            prompt (str): System prompt to set
        """
        try:
            self.system_prompt = prompt
            self._update_current_context()
            logger.info("System prompt set successfully")
        except Exception as e:
            logger.error(f"Error setting system prompt: {str(e)}")
            raise

    def add_knowledge(self, knowledge: str):
        """Add knowledge to the current context.

        Args:
            knowledge (str): Knowledge to add to the context
        """
        try:
            assistant_message = {
                "role": "assistant",
                "content": f"I will remember the following information: {knowledge}"
            }
            self.messages.append(assistant_message)
            self._update_current_context()
            logger.info("Knowledge added successfully")
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            raise

    def ask_question(self, question: str) -> str:
        """Ask a question using the current context.

        Args:
            question (str): Question to ask

        Returns:
            str: Response from the assistant

        Raises:
            ValueError: If no context is loaded
            AnthropicError: If API request fails
        """
        if not self.context_id:
            raise ValueError("Must create or load a context first")

        def _make_request():
            return self.client.messages.create(
                model="claude-3-opus-20240229",
                system=self.system_prompt,
                messages=self.messages + [{"role": "user", "content": question}],
                max_tokens=1000,
                timeout=30
            )

        try:
            response = self._make_api_request(_make_request)

            self.messages.append({"role": "user", "content": question})
            self.messages.append({"role": "assistant", "content": response.content[0].text})

            self._update_current_context()
            return response.content[0].text

        except AnthropicError as e:
            logger.error(f"Error asking question: {str(e)}")
            raise

    def list_contexts(self) -> List[Dict[str, str]]:
        """List all saved contexts.

        Returns:
            list: List of dictionaries containing context information
        """
        try:
            contexts = self._load_all_contexts()
            return [{
                "id": k,
                "name": v["name"],
                "created_at": v["created_at"]
            } for k, v in contexts.items()]
        except Exception as e:
            logger.error(f"Error listing contexts: {str(e)}")
            return []

    def delete_context(self, context_id: str) -> bool:
        """Delete a context by ID.

        Args:
            context_id (str): ID of the context to delete

        Returns:
            bool: True if context was deleted, False if not found
        """
        try:
            contexts = self._load_all_contexts()
            if context_id in contexts:
                del contexts[context_id]
                with open(self.context_file, 'w', encoding='utf-8') as f:
                    json.dump(contexts, f, ensure_ascii=False, indent=2)
                logger.info(f"Context deleted successfully: {context_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting context: {str(e)}")
            return False


def get_transports_by_supplier(supplier_id, transports):
    return [transport for transport in transports if transport['supplierId'] == supplier_id]


def main():
    """Example usage of the ContextualChatbot class."""

    with open('../../suppliers.json', 'r') as file:
        suppliers = json.load(file)

    with open('../../transport_history.json', 'r') as file:
        history = json.load(file)

    suppliers_parts = []
    suppliers_string = """"""

    for idx, supplier in enumerate(suppliers):
        id_supplier = supplier['id']
        transports: list[dict] = get_transports_by_supplier(id_supplier, history)

        suppliers_string += f"""Partner, id={supplier['id']}, name={supplier['name']}, city={supplier['address']['city']}, country={supplier['address']['country']}, language={supplier['language']},transports={transports}\n"""
        if idx % 5 == 0:
            suppliers_parts.append(suppliers_string)
            suppliers_string = """"""

    try:
        # Create custom retry configuration
        retry_config = RetryConfig(
            max_retries=5,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True
        )

        # Initialize chatbot
        chatbot = ContextualChatbot(
            api_key=api_key,
            retry_config=retry_config
        )

        # Create new context
        context_id = chatbot.create_new_context("")
        print(f"Created context: {context_id}")

        # Set system prompt
        chatbot.set_system_prompt("""
        You are a chat bot for transport logistics,
        You discuss the price with partners,
        You close a deals.
        """)

        import time
        for supplier_part in suppliers_parts:
            chatbot.add_knowledge(
                suppliers_parts
            )
            time.sleep(1)

        # Ask a question
        try:
            response = chatbot.ask_question("Best partner for Barcelona-Belgrade route and what is average price of this transport route?")
            print(f"Response: {response}")
        except AnthropicError as e:
            print(f"Failed after all attempts: {e}")

        # List all contexts
        print("\nAll contexts:")
        for ctx in chatbot.list_contexts():
            print(f"ID: {ctx['id']}, Name: {ctx['name']}, Created: {ctx['created_at']}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
