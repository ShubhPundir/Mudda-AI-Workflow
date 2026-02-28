"""
AWS Bedrock LLM Adapter using Claude 3 Sonnet
Supports structured output with JSON schema validation
"""
import os
import json
import logging
from typing import Any, Dict, Type
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, ValidationError

from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class BedrockLLMAdapter(LLMInterface):
    """
    Implementation of LLMInterface using AWS Bedrock with Claude 3 Sonnet.
    Supports structured output with JSON schema validation.
    """

    def __init__(self):
        self.client = None
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self._initialize_bedrock()

    def _initialize_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            # Get AWS credentials from environment
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            
            if not aws_access_key or not aws_secret_key:
                logger.warning(
                    "AWS credentials not set. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. "
                    "LLM features may fail."
                )
                return
            
            # Initialize Bedrock Runtime client
            self.client = boto3.client(
                service_name="bedrock-runtime",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            logger.info(f"Bedrock client initialized with model: {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None

    async def generate_async(self, content: str) -> Any:
        """
        Generate content using Claude 3 Sonnet via Bedrock
        
        Args:
            content: The prompt/content to send to the model
            
        Returns:
            Response object with text attribute
            
        Raises:
            ValueError: If client not initialized
            RuntimeError: If generation fails
        """
        if not self.client:
            raise ValueError("Bedrock client is not initialized (missing AWS credentials?)")
        
        try:
            # Prepare request body for Claude 3
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            # Extract text from Claude response
            text_content = response_body.get("content", [{}])[0].get("text", "")
            
            # Create response object with text attribute
            class Response:
                def __init__(self, text):
                    self.text = text
            
            return Response(text_content)
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise RuntimeError(f"Bedrock generation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise RuntimeError(f"Generation failed: {e}") from e

    async def generate_structured(
        self, 
        content: str, 
        response_schema: Type[BaseModel]
    ) -> BaseModel:
        """
        Generate structured output with JSON schema validation.
        Uses Claude 3's ability to follow JSON schema instructions.
        
        Args:
            content: The prompt/content to send to the model
            response_schema: Pydantic model class defining expected structure
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If client not initialized or validation fails
            ValidationError: If response doesn't match schema
        """
        if not self.client:
            raise ValueError("Bedrock client is not initialized (missing AWS credentials?)")
        
        # Convert Pydantic schema to JSON schema
        json_schema = response_schema.model_json_schema()
        
        # Create enhanced prompt with schema instructions
        schema_prompt = f"""You must respond with valid JSON that matches this exact schema:

{json.dumps(json_schema, indent=2)}

CRITICAL RULES:
1. Respond ONLY with valid JSON
2. Do not include any markdown formatting or code blocks
3. Do not include any explanatory text before or after the JSON
4. Ensure all required fields are present
5. Match the exact structure specified in the schema

User Request:
{content}

JSON Response:"""
        
        try:
            # Prepare request body for Claude 3
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": schema_prompt
                    }
                ],
                "temperature": 0.3,  # Lower temperature for more consistent JSON
                "top_p": 0.9
            }
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            # Extract text from Claude response
            response_text = response_body.get("content", [{}])[0].get("text", "")
            
            # Clean response text (remove markdown if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse and validate with Pydantic
            response_data = json.loads(response_text)
            validated_response = response_schema.model_validate(response_data)
            
            logger.info(
                "Structured output generated successfully for schema: %s",
                response_schema.__name__
            )
            return validated_response
            
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON from Bedrock response: %s", exc)
            logger.error("Response text: %s", response_text[:500])
            raise ValueError(f"Invalid JSON response from model: {exc}") from exc
        except ValidationError as exc:
            logger.error("Response validation failed: %s", exc)
            raise
        except ClientError as e:
            logger.error("Bedrock API error: %s", e)
            raise RuntimeError(f"Structured output generation failed: {e}") from e
        except Exception as exc:
            logger.error("Structured generation failed: %s", exc)
            raise RuntimeError(f"Structured output generation failed: {exc}") from exc

    async def generate_report(self, inputs: Dict[str, Any]) -> str:
        """
        Generate a text report using Claude 3 Sonnet
        
        Args:
            inputs: Dict containing problem_statement, context, report_type, etc.
            
        Returns:
            Generated report text
            
        Raises:
            RuntimeError: If generation fails
        """
        problem = inputs.get("problem_statement", "")
        context = inputs.get("context", {})
        report_type = inputs.get("report_type", "summary")

        prompt = (
            f"Generate a {report_type} report for the following civic issue:\n\n"
            f"Issue: {problem}\n\n"
        )
        if context:
            prompt += f"Additional context:\n{context}\n\n"
        prompt += (
            "Provide a clear, structured report with findings, "
            "recommendations, and next steps."
        )

        logger.info("LLM report generation via Bedrock Claude 3 — type=%s", report_type)

        try:
            response = await self.generate_async(prompt)
            report_text = response.text if hasattr(response, "text") else str(response)
            return report_text
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise RuntimeError(f"LLM report generation failed: {exc}") from exc
