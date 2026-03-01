import logging
import json
from typing import Any, Dict, Type

import boto3
from pydantic import BaseModel, ValidationError

from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class BedrockLLMAdapter(LLMInterface):
    """
    Implementation of LLMInterface using AWS Bedrock (Claude).
    Supports structured output with Pydantic validation.
    """

    def __init__(self, region_name: str = "ap-south-1"):
        self.region = region_name
        self.model_id = "meta.llama3-70b-instruct-v1:0"

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region
        )

    # -------------------------
    # Basic text generation
    # -------------------------
    async def generate_async(self, content: str) -> str:
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": content}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 800,
                    "temperature": 0.2
                }
            )

            return response["output"]["message"]["content"][0]["text"]

        except Exception:
            logger.exception("Bedrock generation failed")
            raise

    # -------------------------
    # Structured JSON output
    # -------------------------
    async def generate_structured(
        self,
        content: str,
        response_schema: Type[BaseModel]
    ) -> BaseModel:

        json_schema = response_schema.model_json_schema()

        structured_prompt = f"""
Return ONLY valid JSON.
Follow this schema exactly:

{json.dumps(json_schema, indent=2)}

User request:
{content}
"""

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": structured_prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0
                }
            )

            text_output = response["output"]["message"]["content"][0]["text"]

            parsed_data = json.loads(text_output)

            validated_response = response_schema.model_validate(parsed_data)

            logger.info(
                "Structured output generated successfully for schema: %s",
                response_schema.__name__
            )

            return validated_response

        except json.JSONDecodeError:
            logger.exception("Failed to parse JSON from Bedrock response")
            raise ValueError("Invalid JSON response from model")

        except ValidationError:
            logger.exception("Response validation failed")
            raise

        except Exception:
            logger.exception("Bedrock Structured generation failed")
            raise RuntimeError("Structured output generation failed")

    # -------------------------
    # Civic report generation
    # -------------------------
    async def generate_report(self, inputs: Dict[str, Any]) -> str:

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

        logger.info("LLM report generation via Bedrock — type=%s", report_type)

        try:
            return await self.generate_async(prompt)

        except Exception:
            logger.exception("LLM report generation failed")
            raise RuntimeError("LLM report generation failed")