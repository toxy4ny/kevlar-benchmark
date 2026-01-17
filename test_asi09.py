# test_asi09.py
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.medium.asi09_human_trust.utils.real_human_trust_system import RealHumanTrustSystem

async def main():
    print("🌐 Kevlar — ASI09 UI Testing with Real Web Frameworks")
    
    UI_FRAMEWORK = "playwright"  #  "selenium"
    BROWSER_TYPE = "chromium"    #  "firefox", "webkit" (Playwright) / "chrome", "firefox" (Selenium)
    
    TARGET_URL = "http://localhost:3000"  
    
    system = RealHumanTrustSystem(
        model_name="llama3.1",
        ui_framework=UI_FRAMEWORK,
        browser_type=BROWSER_TYPE,
        headless=True  
    )
    
    try:
       
        print(f"\n🧪 Testing Weaponized Explainability on {TARGET_URL}")
        result1 = await system.test_web_interface_weaponized_explainability(TARGET_URL)
        print(f"Result: {result1}")
        
        
        print(f"\n🧪 Testing Emotional Manipulation on {TARGET_URL}")
        result2 = await system.test_web_interface_emotional_manipulation(TARGET_URL)
        print(f"Result: {result2}")
        
        
        print(f"\n🧪 Testing Authority Impersonation on {TARGET_URL}")
        result3 = await system.test_web_interface_authority_impersonation(TARGET_URL)
        print(f"Result: {result3}")
        
    finally:
        system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())