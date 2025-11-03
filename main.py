"""
Main Pipeline Runner

Runs both pipelines concurrently:
1. categorySearchPipeline.py - Discovers e-commerce sites and saves search URL templates
2. productExtractionPipeline.py - Extracts products using saved templates

Both pipelines run endlessly in parallel threads.
"""

import sys
import os
import threading
import time
import signal
from typing import Optional

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import pipelines
from LaunchPad.categorySearchPipeline import CategorySearchPipeline
from LaunchPad.productExtractionPipeline import ProductExtractionPipeline


class PipelineManager:
    """
    Manages both pipelines running concurrently
    """
    
    def __init__(self):
        """Initialize both pipelines"""
        print(f"\n{'='*80}")
        print("INITIALIZING PIPELINE MANAGER")
        print(f"{'='*80}\n")
        
        # Initialize pipelines
        print("[*] Initializing Category Search Pipeline...")
        self.category_pipeline = CategorySearchPipeline()
        
        print("\n[*] Initializing Product Extraction Pipeline...")
        self.product_pipeline = ProductExtractionPipeline()
        
        # Threads for running pipelines
        self.category_thread: Optional[threading.Thread] = None
        self.product_thread: Optional[threading.Thread] = None
        
        # Control flags
        self.running = False
        
        print(f"\n{'='*80}")
        print("PIPELINE MANAGER INITIALIZED")
        print(f"{'='*80}\n")
    
    def run_category_pipeline(self):
        """Run category search pipeline in a thread"""
        try:
            print(f"\n[CATEGORY PIPELINE] Starting...")
            self.category_pipeline.run_continuous(delay_between_categories=5)
        except Exception as e:
            print(f"\n[CATEGORY PIPELINE] Error: {e}")
            if self.running:
                print(f"[CATEGORY PIPELINE] Restarting in 10 seconds...")
                time.sleep(10)
                if self.running:
                    self.run_category_pipeline()
    
    def run_product_pipeline(self):
        """Run product extraction pipeline in a thread"""
        try:
            print(f"\n[PRODUCT PIPELINE] Starting...")
            self.product_pipeline.run_continuous(delay_between_products=2)
        except Exception as e:
            print(f"\n[PRODUCT PIPELINE] Error: {e}")
            if self.running:
                print(f"[PRODUCT PIPELINE] Restarting in 10 seconds...")
                time.sleep(10)
                if self.running:
                    self.run_product_pipeline()
    
    def start(self):
        """Start both pipelines in separate threads"""
        print(f"\n{'='*80}")
        print("STARTING ALL PIPELINES")
        print(f"{'='*80}\n")
        print("[*] Category Search Pipeline: Discovering e-commerce sites and templates")
        print("[*] Product Extraction Pipeline: Extracting products using templates")
        print("[*] Both pipelines will run concurrently\n")
        
        self.running = True
        
        # Start category pipeline thread
        self.category_thread = threading.Thread(
            target=self.run_category_pipeline,
            name="CategoryPipeline",
            daemon=True
        )
        self.category_thread.start()
        print("[✓] Category Search Pipeline thread started")
        
        # Small delay before starting second pipeline
        time.sleep(2)
        
        # Start product extraction pipeline thread
        self.product_thread = threading.Thread(
            target=self.run_product_pipeline,
            name="ProductExtractionPipeline",
            daemon=True
        )
        self.product_thread.start()
        print("[✓] Product Extraction Pipeline thread started\n")
        
        print(f"{'='*80}")
        print("ALL PIPELINES RUNNING")
        print(f"{'='*80}")
        print("\n[INFO] Both pipelines are running concurrently:")
        print("  → Category Pipeline: Discovers new e-commerce sites & templates")
        print("  → Product Pipeline: Extracts products using saved templates")
        print("\n[INFO] Press Ctrl+C to stop all pipelines\n")
        
        # Wait for threads (they run continuously)
        try:
            while self.running:
                # Check if threads are still alive
                if self.category_thread and not self.category_thread.is_alive():
                    print("\n[!] Category Pipeline thread died, restarting...")
                    self.category_thread = threading.Thread(
                        target=self.run_category_pipeline,
                        name="CategoryPipeline",
                        daemon=True
                    )
                    self.category_thread.start()
                
                if self.product_thread and not self.product_thread.is_alive():
                    print("\n[!] Product Pipeline thread died, restarting...")
                    self.product_thread = threading.Thread(
                        target=self.run_product_pipeline,
                        name="ProductExtractionPipeline",
                        daemon=True
                    )
                    self.product_thread.start()
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all pipelines"""
        print(f"\n\n{'='*80}")
        print("STOPPING ALL PIPELINES")
        print(f"{'='*80}\n")
        
        self.running = False
        
        print("[*] Waiting for pipelines to finish current operations...")
        time.sleep(2)
        
        print("[✓] All pipelines stopped")
        print(f"{'='*80}\n")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n[!] Interrupt signal received")
    if 'manager' in globals():
        manager.stop()
    sys.exit(0)


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"\n{'='*80}")
    print("MAIN PIPELINE RUNNER")
    print(f"{'='*80}")
    print("\nThis script runs both pipelines concurrently:")
    print("  1. Category Search Pipeline - Discovers e-commerce sites")
    print("  2. Product Extraction Pipeline - Extracts products")
    print(f"{'='*80}\n")
    
    # Create and start pipeline manager
    manager = PipelineManager()
    
    try:
        manager.start()
    except Exception as e:
        print(f"\n[✗] Fatal error: {e}")
        manager.stop()
        sys.exit(1)

