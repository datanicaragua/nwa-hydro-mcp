import asyncio

from nwa_hydro.tools.fusion import fetch_climate_data
from nwa_hydro.tools.intelligence import generate_agronomist_insight
from nwa_hydro.tools.science import calculate_hargreaves_eto


async def verify():
    print("🚀 Starting Verification...")

    # 1. Test Fusion (API)
    print("\nTesting Fusion Tool (API)...")
    try:
        data = await fetch_climate_data(12.8654, -85.2072, "2023-01-01")
        print(f"✅ API Fetch Success: {data.date} | Tmean: {data.tmean}")
    except Exception as e:
        print(f"❌ API Fetch Failed: {e}")

    # 2. Test Fusion (CSV Fallback)
    # To test this we'd need to simulate API failure, but we're trusting the unit tests for now.

    # 3. Test Science
    print("\nTesting Science Tool...")
    try:
        eto = calculate_hargreaves_eto(data)
        print(f"✅ ETo Calculation Success: {eto.eto:.2f} mm/day")
    except Exception as e:
        print(f"❌ ETo Calculation Failed: {e}")

    # 4. Test Intelligence
    print("\nTesting Intelligence Tool...")
    # We might not have an API key, so we expect a graceful handling or success if key is present.
    try:
        insight = await generate_agronomist_insight(eto)
        print(f"✅ Insight Generation Success: {insight.summary}")
    except Exception as e:
        print(f"❌ Insight Generation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
