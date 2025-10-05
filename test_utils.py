#!/usr/bin/env python3
"""
StoryBoard Testing and Validation Utilities
==========================================

This script provides utilities for testing and validating the storyboard system.
"""

import json
import os
from pathlib import Path
import logging

from storyboard_analyzer import StoryboardAnalyzer
from ai_image_generator import StoryboardPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_character_extraction():
    """Test character extraction functionality"""
    logger.info("Testing character extraction...")
    
    test_script = """
    Scene 1: The Office
    
    John, a tall man with glasses, sits at his desk. He's wearing a blue suit and looks professional.
    Sarah, a short woman with blonde hair, walks into the office. She's wearing a red dress.
    
    Scene 2: The Office
    
    John is still at his desk, wearing the same blue suit and glasses. He looks tired.
    Sarah returns, still in her red dress, carrying a coffee cup.
    """
    
    analyzer = StoryboardAnalyzer()
    analysis_data = analyzer.analyze_script(test_script)
    
    # Validate character extraction
    assert len(analysis_data.characters) >= 2, "Should extract at least 2 characters"
    
    character_names = [char.name for char in analysis_data.characters]
    assert "John" in character_names, "Should extract John"
    assert "Sarah" in character_names, "Should extract Sarah"
    
    # Check character traits
    john = next(char for char in analysis_data.characters if char.name == "John")
    assert "glasses" in john.recurring_elements, "John should have glasses as recurring element"
    assert john.visual_description, "John should have visual description"
    
    logger.info("✓ Character extraction test passed")

def test_scene_analysis():
    """Test scene analysis functionality"""
    logger.info("Testing scene analysis...")
    
    test_script = """
    Scene 1: The Living Room - Morning
    
    The living room is bright with morning sunlight streaming through the windows.
    The atmosphere is peaceful and cozy.
    
    Scene 2: The Kitchen - Afternoon
    
    The kitchen has warm afternoon lighting and feels inviting.
    The mood is relaxed and comfortable.
    """
    
    analyzer = StoryboardAnalyzer()
    analysis_data = analyzer.analyze_script(test_script)
    
    # Validate scene analysis
    assert len(analysis_data.scene_contexts) >= 2, "Should extract at least 2 scenes"
    
    scene1 = analysis_data.scene_contexts[0]
    assert scene1.location.lower() in ["living room", "livingroom"], "Should detect living room"
    assert scene1.time_of_day.lower() == "morning", "Should detect morning"
    assert scene1.lighting.lower() in ["bright", "natural"], "Should detect bright lighting"
    
    scene2 = analysis_data.scene_contexts[1]
    assert scene2.location.lower() in ["kitchen"], "Should detect kitchen"
    assert scene2.time_of_day.lower() == "afternoon", "Should detect afternoon"
    
    logger.info("✓ Scene analysis test passed")

def test_reference_management():
    """Test reference image management"""
    logger.info("Testing reference management...")
    
    from ai_image_generator import ReferenceImageManager
    
    ref_manager = ReferenceImageManager("test_references")
    
    # Test scene signature creation
    scene_context = {
        "location": "Living Room",
        "time_of_day": "Morning",
        "weather": "Sunny",
        "lighting": "Bright"
    }
    
    signature = ref_manager.create_scene_signature(scene_context)
    expected = "living_room_morning_sunny_bright"
    assert signature == expected, f"Expected {expected}, got {signature}"
    
    # Create a dummy image file for testing
    from PIL import Image
    test_image = Image.new('RGB', (100, 100), color='red')
    test_image.save("test_image.png")
    
    # Test reference registration
    ref_manager.register_reference(signature, "test_image.png", {"test": "data"})
    assert signature in ref_manager.reference_registry, "Should register reference"
    
    # Test reference retrieval
    retrieved = ref_manager.get_reference(signature)
    assert retrieved == "test_image.png", "Should retrieve correct reference"
    
    # Clean up
    os.remove("test_image.png")
    
    logger.info("✓ Reference management test passed")

def test_prompt_building():
    """Test prompt building functionality"""
    logger.info("Testing prompt building...")
    
    from ai_image_generator import PromptBuilder
    
    builder = PromptBuilder()
    
    # Test character prompt
    character_data = {
        "name": "Alex",
        "visual_description": "Physical: tall, dark hair; Accessories: glasses",
        "recurring_elements": ["glasses", "blue hoodie"]
    }
    
    char_prompt = builder.build_character_prompt(character_data, "sitting at table")
    assert "Alex" in char_prompt, "Should include character name"
    assert "glasses" in char_prompt, "Should include recurring elements"
    assert "sitting at table" in char_prompt, "Should include action"
    
    # Test scene prompt
    scene_context = {
        "location": "Coffee Shop",
        "time_of_day": "Morning",
        "lighting": "Bright",
        "mood": "Peaceful"
    }
    
    scene_prompt = builder.build_scene_prompt(scene_context, [character_data], ["laptop", "coffee"])
    assert "Coffee Shop" in scene_prompt, "Should include location"
    assert "Morning" in scene_prompt, "Should include time"
    assert "laptop" in scene_prompt, "Should include props"
    
    logger.info("✓ Prompt building test passed")

def test_full_pipeline():
    """Test the complete pipeline"""
    logger.info("Testing full pipeline...")
    
    # Use the sample script
    script_file = "sample_script.txt"
    if not os.path.exists(script_file):
        logger.warning("Sample script not found, skipping full pipeline test")
        return
    
    # Run analysis
    analyzer = StoryboardAnalyzer()
    with open(script_file, 'r') as f:
        script_text = f.read()
    
    analysis_data = analyzer.analyze_script(script_text)
    
    # Validate analysis results
    assert len(analysis_data.characters) > 0, "Should extract characters"
    assert len(analysis_data.scene_contexts) > 0, "Should extract scenes"
    assert len(analysis_data.generation_instructions) > 0, "Should create generation instructions"
    
    # Test that we have both initial and reference-based scenes
    generation_types = [inst["generation_type"] for inst in analysis_data.generation_instructions.values()]
    assert "initial" in generation_types, "Should have initial generation scenes"
    
    logger.info("✓ Full pipeline test passed")

def run_all_tests():
    """Run all tests"""
    logger.info("Running all tests...")
    
    try:
        test_character_extraction()
        test_scene_analysis()
        test_reference_management()
        test_prompt_building()
        test_full_pipeline()
        
        logger.info("=" * 50)
        logger.info("ALL TESTS PASSED! ✓")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

def validate_analysis_file(analysis_file: str):
    """Validate an analysis JSON file"""
    logger.info(f"Validating analysis file: {analysis_file}")
    
    if not os.path.exists(analysis_file):
        logger.error(f"Analysis file not found: {analysis_file}")
        return False
    
    try:
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        
        # Check required fields
        required_fields = ["characters", "scene_contexts", "generation_instructions"]
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate structure
        assert isinstance(data["characters"], list), "Characters should be a list"
        assert isinstance(data["scene_contexts"], list), "Scene contexts should be a list"
        assert isinstance(data["generation_instructions"], dict), "Generation instructions should be a dict"
        
        logger.info("✓ Analysis file validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Analysis file validation failed: {e}")
        return False

def benchmark_performance():
    """Benchmark the system performance"""
    logger.info("Running performance benchmark...")
    
    import time
    
    script_file = "sample_script.txt"
    if not os.path.exists(script_file):
        logger.warning("Sample script not found, skipping benchmark")
        return
    
    # Benchmark analysis
    analyzer = StoryboardAnalyzer()
    with open(script_file, 'r') as f:
        script_text = f.read()
    
    start_time = time.time()
    analysis_data = analyzer.analyze_script(script_text)
    analysis_time = time.time() - start_time
    
    logger.info(f"Analysis time: {analysis_time:.2f} seconds")
    logger.info(f"Characters extracted: {len(analysis_data.characters)}")
    logger.info(f"Scenes analyzed: {len(analysis_data.scene_contexts)}")
    logger.info(f"Recurring elements: {len(analysis_data.recurring_elements)}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='StoryBoard Testing Utilities')
    parser.add_argument('--test', action='store_true', help='Run all tests')
    parser.add_argument('--validate', help='Validate analysis file')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark')
    
    args = parser.parse_args()
    
    if args.test:
        run_all_tests()
    elif args.validate:
        validate_analysis_file(args.validate)
    elif args.benchmark:
        benchmark_performance()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
