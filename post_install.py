import os
import subprocess
import sys

def build_assets():
    """
    Silicon Valley Asset Builder
    Compiles Tailwind CSS and Rollup JS during Vercel build phase.
    """
    print("🎨 [ ASSET BUILDER ] Starting Static Asset Compilation...")
    
    # 1. Install Node dependencies
    static_dir = os.path.join(os.getcwd(), "static")
    if not os.path.exists(static_dir):
        print(f"❌ Static directory not found at {static_dir}")
        return

    print(f"📂 Changing directory to: {static_dir}")
    os.chdir(static_dir)

    try:
        print("📦 Installing npm dependencies...")
        subprocess.run(["npm", "install"], check=True, shell=True)
        
        print("🔨 Building assets (CSS + JS)...")
        subprocess.run(["npm", "run", "build"], check=True, shell=True)
        
        print("✅ Asset Compilation Successful.")
    except subprocess.CalledProcessError as e:
        print(f"🔥 Asset Build Failed: {e}")
        # We don't exit(1) here to allow the python build to continue, 
        # but assets might be missing.
        sys.exit(1)

if __name__ == "__main__":
    build_assets()
