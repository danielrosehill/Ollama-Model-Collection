#!/usr/bin/env python3
"""
Ollama Model Benchmarking Script
Measures inference speed across all available models with standardized prompts.
"""

import json
import time
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import psutil
import os

class OllamaBenchmark:
    def __init__(self):
        self.results = []
        self.test_prompts = [
            {
                "name": "Creative Writing",
                "prompt": "Write a short story about a robot discovering emotions for the first time.",
                "expected_tokens": 150
            },
            {
                "name": "Technical Explanation", 
                "prompt": "Explain how neural networks work in simple terms that a beginner could understand.",
                "expected_tokens": 200
            },
            {
                "name": "Code Generation",
                "prompt": "Write a Python function that calculates the factorial of a number using recursion.",
                "expected_tokens": 100
            }
        ]
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]  # First column is model name
                    models.append(model_name)
            return models
        except subprocess.CalledProcessError as e:
            print(f"Error getting model list: {e}")
            return []
    
    def count_tokens(self, text: str) -> int:
        """Rough token count estimation (1 token ≈ 4 characters for English)"""
        return len(text.split())
    
    def run_inference(self, model: str, prompt: str) -> Tuple[str, float, float, Dict]:
        """Run inference and measure performance metrics"""
        print(f"  Testing prompt: {prompt[:50]}...")
        
        # Record system state before inference
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Prepare ollama command
        cmd = ['ollama', 'run', model, prompt]
        
        # Measure total inference time
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            end_time = time.time()
            
            if result.returncode != 0:
                return "", 0.0, 0.0, {"error": result.stderr}
            
            response = result.stdout.strip()
            total_time = end_time - start_time
            
            # Calculate metrics
            token_count = self.count_tokens(response)
            tokens_per_second = token_count / total_time if total_time > 0 else 0
            
            # Memory usage after inference
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            metrics = {
                "total_time": round(total_time, 2),
                "tokens_generated": token_count,
                "tokens_per_second": round(tokens_per_second, 2),
                "memory_delta_mb": round(memory_used, 2),
                "response_length": len(response)
            }
            
            return response, total_time, tokens_per_second, metrics
            
        except subprocess.TimeoutExpired:
            return "", 0.0, 0.0, {"error": "Timeout after 120 seconds"}
        except Exception as e:
            return "", 0.0, 0.0, {"error": str(e)}
    
    def benchmark_model(self, model: str) -> Dict:
        """Benchmark a single model across all test prompts"""
        print(f"\n🔍 Benchmarking model: {model}")
        
        model_results = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "prompts": [],
            "average_tps": 0.0,
            "average_time": 0.0
        }
        
        total_tps = 0.0
        total_time = 0.0
        successful_tests = 0
        
        for test_prompt in self.test_prompts:
            print(f"  📝 {test_prompt['name']}")
            
            response, inference_time, tps, metrics = self.run_inference(
                model, test_prompt['prompt']
            )
            
            prompt_result = {
                "name": test_prompt['name'],
                "prompt": test_prompt['prompt'],
                "response": response[:200] + "..." if len(response) > 200 else response,
                "metrics": metrics
            }
            
            model_results["prompts"].append(prompt_result)
            
            if "error" not in metrics:
                total_tps += tps
                total_time += inference_time
                successful_tests += 1
                print(f"    ✅ {tps:.1f} tokens/sec, {inference_time:.1f}s total")
            else:
                print(f"    ❌ Error: {metrics['error']}")
        
        # Calculate averages
        if successful_tests > 0:
            model_results["average_tps"] = round(total_tps / successful_tests, 2)
            model_results["average_time"] = round(total_time / successful_tests, 2)
            model_results["success_rate"] = round(successful_tests / len(self.test_prompts), 2)
        
        return model_results
    
    def run_full_benchmark(self) -> None:
        """Run benchmark across all available models"""
        models = self.get_available_models()
        
        if not models:
            print("❌ No Ollama models found!")
            return
        
        print(f"🚀 Starting benchmark for {len(models)} models...")
        print(f"📊 Test prompts: {len(self.test_prompts)}")
        print("=" * 60)
        
        for i, model in enumerate(models, 1):
            print(f"\n[{i}/{len(models)}] Processing {model}")
            
            try:
                result = self.benchmark_model(model)
                self.results.append(result)
            except KeyboardInterrupt:
                print(f"\n⚠️  Benchmark interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error benchmarking {model}: {e}")
                continue
        
        self.save_results()
        self.print_summary()
    
    def save_results(self) -> None:
        """Save benchmark results to JSON file"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"benchmark-results-{timestamp}.json"
        
        benchmark_data = {
            "benchmark_date": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / 1024**3, 1),
                "python_version": sys.version
            },
            "test_configuration": {
                "prompts": self.test_prompts,
                "timeout_seconds": 120
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
    
    def print_summary(self) -> None:
        """Print benchmark summary table"""
        if not self.results:
            print("❌ No results to display")
            return
        
        print(f"\n{'='*80}")
        print("🏆 BENCHMARK SUMMARY")
        print(f"{'='*80}")
        print(f"{'Model':<35} {'Avg TPS':<12} {'Avg Time':<12} {'Success':<10}")
        print("-" * 80)
        
        # Sort by average TPS (descending)
        sorted_results = sorted(
            [r for r in self.results if r.get('average_tps', 0) > 0], 
            key=lambda x: x.get('average_tps', 0), 
            reverse=True
        )
        
        for result in sorted_results:
            model = result['model'][:34]  # Truncate long model names
            avg_tps = f"{result.get('average_tps', 0):.1f}"
            avg_time = f"{result.get('average_time', 0):.1f}s"
            success = f"{result.get('success_rate', 0)*100:.0f}%"
            
            print(f"{model:<35} {avg_tps:<12} {avg_time:<12} {success:<10}")
        
        print("-" * 80)
        
        if sorted_results:
            fastest = sorted_results[0]
            print(f"🥇 Fastest model: {fastest['model']} ({fastest['average_tps']:.1f} tokens/sec)")

def main():
    """Main execution function"""
    print("🤖 Ollama Model Benchmark Suite")
    print("=" * 50)
    
    # Check if ollama is available
    try:
        subprocess.run(['ollama', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not found! Please install Ollama first.")
        sys.exit(1)
    
    benchmark = OllamaBenchmark()
    
    try:
        benchmark.run_full_benchmark()
    except KeyboardInterrupt:
        print(f"\n⚠️  Benchmark interrupted by user")
        if benchmark.results:
            benchmark.save_results()
            benchmark.print_summary()

if __name__ == "__main__":
    main()
