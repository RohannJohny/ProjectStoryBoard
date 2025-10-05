#!/usr/bin/env python3
"""
StoryBoard Frame-Level Consistency System - Main Entry Point
============================================================

This is the main entry point for the complete storyboard pipeline.
It integrates all components and provides a unified interface.

Usage:
    python main.py <script_file> [options]
    python main.py --demo  # Run demonstration
"""

import argparse
import json
import os
import sys
from pathlib import Path
import logging

# Import our modules
from storyboard_analyzer import StoryboardAnalyzer
from ai_image_generator import StoryboardPipeline
from complete_pipeline import demonstrate_analysis, demonstrate_image_generation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        logger.warning(f"Config file {config_file} not found, using defaults")
        return {}

def run_analysis_only(script_file: str, output_file: str, config: dict):
    """Run only the script analysis"""
    logger.info(f"Analyzing script: {script_file}")
    
    analyzer = StoryboardAnalyzer()
    
    with open(script_file, 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    analysis_data = analyzer.analyze_script(script_text)
    analyzer.save_analysis(analysis_data, output_file)
    
    # Generate summary report
    report = analyzer.generate_summary_report(analysis_data)
    print(report)
    
    return analysis_data

def run_generation_only(analysis_file: str, output_dir: str, config: dict):
    """Run only the image generation"""
    logger.info(f"Generating images from analysis: {analysis_file}")
    
    pipeline = StoryboardPipeline(analysis_file, output_dir)
    results = pipeline.run_full_pipeline()
    
    logger.info(f"Generation completed. Generated {results['pipeline_metadata']['successful_generations']} images")
    return results

def run_full_pipeline(script_file: str, output_dir: str, config: dict):
    """Run the complete pipeline"""
    logger.info("Running complete storyboard pipeline...")
    
    # Step 1: Analysis
    analysis_file = os.path.join(output_dir, "analysis.json")
    analysis_data = run_analysis_only(script_file, analysis_file, config)
    
    # Step 2: Generation
    results = run_generation_only(analysis_file, output_dir, config)
    
    return analysis_data, results

def run_demo():
    """Run the demonstration"""
    logger.info("Running demonstration...")
    
    from complete_pipeline import main as demo_main
    demo_main()

def validate_script(script_file: str) -> bool:
    """Validate that the script file exists and has content"""
    if not os.path.exists(script_file):
        logger.error(f"Script file not found: {script_file}")
        return False
    
    with open(script_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        logger.error("Script file is empty")
        return False
    
    # Check for basic scene structure
    if "Scene" not in content:
        logger.warning("Script doesn't appear to have scene markers. Consider adding 'Scene X:' markers.")
    
    return True

def create_output_directory(output_dir: str):
    """Create output directory if it doesn't exist"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='StoryBoard Frame-Level Consistency System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py script.txt                    # Run full pipeline
  python main.py script.txt --analysis-only   # Run only analysis
  python main.py analysis.json --generate-only # Run only generation
  python main.py --demo                       # Run demonstration
  python main.py script.txt -o my_output     # Custom output directory
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='Script file or analysis file')
    parser.add_argument('-o', '--output', default='storyboard_output', 
                       help='Output directory (default: storyboard_output)')
    parser.add_argument('-c', '--config', default='config.json',
                       help='Configuration file (default: config.json)')
    parser.add_argument('--analysis-only', action='store_true',
                       help='Run only script analysis')
    parser.add_argument('--generate-only', action='store_true',
                       help='Run only image generation (requires analysis file)')
    parser.add_argument('--demo', action='store_true',
                       help='Run demonstration with sample script')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config(args.config)
    
    # Handle demo mode
    if args.demo:
        run_demo()
        return
    
    # Validate input
    if not args.input_file:
        parser.error("Input file is required (unless using --demo)")
    
    # Create output directory
    create_output_directory(args.output)
    
    try:
        if args.generate_only:
            # Generation only mode
            if not os.path.exists(args.input_file):
                logger.error(f"Analysis file not found: {args.input_file}")
                return
            
            results = run_generation_only(args.input_file, args.output, config)
            logger.info("Generation completed successfully!")
            
        elif args.analysis_only:
            # Analysis only mode
            if not validate_script(args.input_file):
                return
            
            analysis_data = run_analysis_only(args.input_file, 
                                            os.path.join(args.output, "analysis.json"), 
                                            config)
            logger.info("Analysis completed successfully!")
            
        else:
            # Full pipeline mode
            if not validate_script(args.input_file):
                return
            
            analysis_data, results = run_full_pipeline(args.input_file, args.output, config)
            logger.info("Full pipeline completed successfully!")
            
            # Print summary
            print("\n" + "="*60)
            print("PIPELINE SUMMARY")
            print("="*60)
            print(f"Total characters: {len(analysis_data.characters)}")
            print(f"Total scenes: {len(analysis_data.scene_contexts)}")
            print(f"Recurring elements: {len(analysis_data.recurring_elements)}")
            print(f"Generated images: {results['pipeline_metadata']['successful_generations']}")
            print(f"Consistency score: {results['consistency_report']['overall_score']:.2f}")
            print(f"Output directory: {args.output}")
            print("="*60)
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
