import asyncio
import json
import logging
import os
from textwrap import dedent

from dotenv import load_dotenv  # Import the library
load_dotenv()  # Load environment variables from local .env file

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..schemas import AgronomistInsight, EToResult

logger = logging.getLogger(__name__)
GENERATION_TIMEOUT_SECONDS = 15.0
DEFAULT_RISK = "Medium"

# Configure Gemini
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "advice": {"type": "string"},
        "risk_level": {"type": "string", "enum": ["Low", "Medium", "High"]},
    },
    "required": ["summary", "advice", "risk_level"],
}


def _parse_risk(text: str) -> str:
    text_upper = text.upper()
    if "HIGH" in text_upper:
        return "High"
    if "LOW" in text_upper:
        return "Low"
    return DEFAULT_RISK


def _build_prompt(eto_result: EToResult) -> str:
    return dedent(
        f"""
        You are an expert Agronomist providing an executive summary for a farmer.

        Dashboard Data:
        - Date: {eto_result.date}
        - Mean Temperature: {eto_result.input_data.tmean:.1f} °C
        - Precipitation: {eto_result.input_data.precipitation:.1f} mm
        - Humidity: {eto_result.input_data.humidity:.1f} %
        - Reference Evapotranspiration (ETo): {eto_result.eto:.2f} mm/day

        Task:
        1. Analyze the water balance (Precipitation vs ETo).
        2. Determine the irrigation risk (Low, Medium, High).
        3. Provide a concise, professional executive summary (max 3 sentences).
        4. Give one specific, actionable recommendation.
        """
    ).strip()


def _get_fallback_insight(eto_value: float, reason: str) -> AgronomistInsight:
    """Return a sensible fallback when Gemini fails."""
    if eto_value < 3.0:
        risk = "Low"
        advice = "Low water demand. Standard irrigation schedule is adequate."
    elif eto_value < 5.0:
        risk = "Medium"
        advice = "Moderate demand. Consider irrigation every 2-3 days."
    else:
        risk = "High"
        advice = "High evapotranspiration. Daily irrigation recommended."

    return AgronomistInsight(
        summary=f"Automated analysis ({reason}).",
        advice=advice,
        risk_level=risk,
        eto_value=eto_value,
    )


async def _generate_with_timeout(
    model: genai.GenerativeModel,
    prompt: str,
    safety_settings: dict,
    generation_config: dict,
) -> str:
    response = await asyncio.wait_for(
        model.generate_content_async(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
        ),
        timeout=GENERATION_TIMEOUT_SECONDS,
    )

    # Check for blocked response BEFORE accessing .text
    if response.prompt_feedback:
        logger.debug("Gemini prompt feedback: %s", response.prompt_feedback)
    if not response.candidates:
        raise ValueError("No candidates returned")

    candidate = response.candidates[0]
    if candidate.finish_reason.name == "SAFETY":
        if getattr(candidate, "safety_ratings", None):
            logger.warning("Gemini blocked response: %s", candidate.safety_ratings)
        raise ValueError("Response blocked by safety filter")

    if not candidate.content or not candidate.content.parts:
        raise ValueError("Empty content returned")

    return candidate.content.parts[0].text


async def generate_agronomist_insight(eto_result: EToResult) -> AgronomistInsight:
    """
    Generate an agronomist insight using Google Gemini, with safe fallbacks for local/dev runs.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return AgronomistInsight(
            summary="API key missing",
            advice="Set GOOGLE_API_KEY to enable Gemini-powered insights.",
            risk_level="Unknown",
            eto_value=eto_result.eto,
        )

    model = genai.GenerativeModel(
        "gemini-2.5-flash-lite",
        system_instruction=(
            "You are an expert agronomist assistant for NWA. "
            "Analyze the provided water metrics scientifically and return only JSON "
            "matching the schema: summary (string), advice (string), risk_level "
            "as Low, Medium, or High."
        ),
    )
    prompt = _build_prompt(eto_result)

    # Safety settings to prevent false positives in agronomic advice
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    generation_config = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "response_mime_type": "application/json",
        "response_schema": RESPONSE_SCHEMA,
    }

    try:
        text = await _generate_with_timeout(
            model, prompt, safety_settings, generation_config
        )
        try:
            parsed = json.loads(text)
            summary = parsed.get("summary", "").strip() or "Analysis generated."
            advice = parsed.get("advice", "").strip() or text
            risk_level = parsed.get("risk_level", DEFAULT_RISK)
        except json.JSONDecodeError:
            summary = "Analysis generated."
            advice = text
            risk_level = _parse_risk(text)
    except asyncio.TimeoutError:
        logger.warning("Gemini insight generation timed out")
        summary = "Insight generation timed out."
        advice = "Try again or reduce request load."
        risk_level = DEFAULT_RISK
    except Exception as exc:  # noqa: BLE001
        logger.error("Gemini insight generation failed: %s", exc)
        return _get_fallback_insight(eto_result.eto, "API error")

    return AgronomistInsight(
        summary=summary,
        advice=advice,
        risk_level=risk_level,
        eto_value=eto_result.eto,
    )


# ==========================================
# TEST BLOCK (added for validation)
# ==========================================
if __name__ == "__main__":
    import sys

    # Basic logging to surface errors
    logging.basicConfig(level=logging.DEBUG)

    # 1) Mock input data matching the EToResult structure
    class MockInputData:
        tmean = 28.5  # Simulated temperature

    class MockEToResult:
        date = "2025-11-28"
        eto = 7.78  # Simulated ETo
        input_data = MockInputData()

    print("\n--- Starting Gemini 2.5 Lite connectivity test ---")
    print(f"API key detected: {'YES' if os.getenv('GOOGLE_API_KEY') else 'NO'}")

    # 2) Execute the async function
    try:
        test_data = MockEToResult()

        result = asyncio.run(generate_agronomist_insight(test_data))

        print("\n" + "=" * 40)
        print("Successful result (parsed JSON)")
        print("=" * 40)
        print(f"Summary:    {result.summary}")
        print(f"Advice:     {result.advice}")
        print(f"Risk Level: {result.risk_level}")
        print("=" * 40 + "\n")

    except Exception as e:  # noqa: BLE001
        print(f"\nFatal error during the test:\n{e}")
