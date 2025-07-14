#!/usr/bin/env python3
"""
Test script to identify what's blocking Django startup
"""
import os
import sys
import time
import traceback
from threading import Thread

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def monitor_startup():
    """Monitor Django startup"""
    print("🔍 Monitoring Django startup...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    try:
        print("📦 Importing Django...")
        import django
        print("✅ Django imported successfully")
        
        print("🔧 Calling django.setup()...")
        start_time = time.time()
        django.setup()
        setup_time = time.time() - start_time
        print(f"✅ Django setup completed in {setup_time:.2f}s")
        
        print("🚀 Testing app loading...")
        from django.apps import apps
        
        for app in apps.get_app_configs():
            print(f"   📱 App: {app.name}")
            
        print("✅ All apps loaded successfully")
        
        print("🌐 Testing basic imports...")
        from django.conf import settings
        print(f"   ✅ Settings: {settings.DEBUG}")
        
        print("🔌 Testing chat app imports...")
        from apps.chat import models
        print("   ✅ Chat models imported")
        
        from apps.chat import views
        print("   ✅ Chat views imported")
        
        # Test problematic imports
        print("⚠️  Testing potentially problematic imports...")
        try:
            from apps.chat import views_langchain
            print("   ✅ views_langchain imported")
        except Exception as e:
            print(f"   ❌ views_langchain failed: {e}")
            
        try:
            from apps.chat import views_llama_agents
            print("   ✅ views_llama_agents imported")
        except Exception as e:
            print(f"   ❌ views_llama_agents failed: {e}")
            
        try:
            from apps.chat import views_llama_stats
            print("   ✅ views_llama_stats imported")
        except Exception as e:
            print(f"   ❌ views_llama_stats failed: {e}")
            
        try:
            from agents.lazy_llama_manager import lazy_llama_manager
            print("   ✅ lazy_llama_manager imported")
        except Exception as e:
            print(f"   ❌ lazy_llama_manager failed: {e}")
            
        print("🎯 Testing Django URLs...")
        from django.urls import get_resolver
        resolver = get_resolver()
        print(f"   ✅ URL resolver created: {len(resolver.url_patterns)} patterns")
        
        print("🏁 Django startup test completed successfully!")
        
    except Exception as e:
        print(f"❌ Django startup failed: {e}")
        traceback.print_exc()
        return False
        
    return True

def timeout_handler():
    """Handle timeout for Django startup"""
    time.sleep(30)  # 30 second timeout
    print("⏰ Django startup timeout reached!")
    os._exit(1)

if __name__ == "__main__":
    # Start timeout monitor
    timeout_thread = Thread(target=timeout_handler, daemon=True)
    timeout_thread.start()
    
    # Monitor startup
    success = monitor_startup()
    
    if success:
        print("\n✅ Django startup successful!")
        sys.exit(0)
    else:
        print("\n❌ Django startup failed!")
        sys.exit(1)