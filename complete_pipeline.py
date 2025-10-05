#!/usr/bin/env python3
"""
Complete StoryBoard Pipeline - Example Usage
============================================

This script demonstrates the complete frame-level consistency pipeline:
1. Script analysis → Character & scene extraction
2. Reference image management
3. AI image generation with consistency
4. Video compilation

Usage:
    python complete_pipeline.py sample_script.txt
"""

import json
import os
import sys
from pathlib import Path
import logging

# Import our modules
from storyboard_analyzer import StoryboardAnalyzer
from ai_image_generator import StoryboardPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_script():
    """Create a sample script for demonstration"""
    sample_script = """
Scene 1: The Living Room - Morning

Sarah, a tall blonde woman with glasses, sits on the couch in her living room. She's wearing a blue sweater and reading a book. The morning sun streams through the window, creating bright lighting. The room has a cozy, peaceful atmosphere with a coffee table and lamp nearby.

Scene 2: The Kitchen - Morning

Sarah walks into the kitchen, still wearing her blue sweater and glasses. She puts the book on the counter and starts making coffee. The kitchen has bright morning lighting and feels warm and inviting.

Scene 3: The Living Room - Evening

Later that day, Sarah returns to the living room, still in her blue sweater and glasses. She sits on the same couch, but now the room has dim evening lighting. The lamp on the coffee table provides soft illumination, creating a relaxed atmosphere.

Scene 4: The Kitchen - Evening

Sarah goes back to the kitchen in the evening, maintaining her consistent appearance with the blue sweater and glasses. The kitchen now has warm artificial lighting, creating a cozy evening mood.

Scene 5: The Living Room - Night

At night, Sarah is back in the living room, still wearing her blue sweater and glasses. The room is now dark with only the lamp providing dramatic lighting, creating a mysterious atmosphere.
"""
    
    with open("sample_script.txt", "w") as f:
        f.write(sample_script)
    
    logger.info("Created sample_script.txt")
    return "sample_script.txt"

def demonstrate_analysis():
    """Demonstrate the script analysis functionality"""
    logger.info("=" * 60)
    logger.info("DEMONSTRATING SCRIPT ANALYSIS")
    logger.info("=" * 60)
    
    # Create sample script if it doesn't exist
    script_file = "sample_script.txt"
    if not os.path.exists(script_file):
        script_file = create_sample_script()
    
    # Analyze the script
    analyzer = StoryboardAnalyzer()
    
    with open(script_file, 'r') as f:
        script_text = f.read()
    
    # Perform analysis
    analysis_data = analyzer.analyze_script(script_text)
    
    # Save analysis results
    analyzer.save_analysis(analysis_data, "storyboard_analysis.json")
    
    # Generate and display summary report
    report = analyzer.generate_summary_report(analysis_data)
    print(report)
    
    return analysis_data

def demonstrate_image_generation(analysis_data):
    """Demonstrate the AI image generation pipeline"""
    logger.info("=" * 60)
    logger.info("DEMONSTRATING AI IMAGE GENERATION")
    logger.info("=" * 60)
    
    # Save analysis data to file for pipeline
    with open("storyboard_analysis.json", "w") as f:
        json.dump({
            "characters": [asdict(char) for char in analysis_data.characters],
            "scene_contexts": [asdict(scene) for scene in analysis_data.scene_contexts],
            "recurring_elements": [asdict(elem) for elem in analysis_data.recurring_elements],
            "reference_templates": analysis_data.reference_templates,
            "generation_instructions": analysis_data.generation_instructions,
            "metadata": {
                "total_characters": len(analysis_data.characters),
                "total_scenes": len(analysis_data.scene_contexts),
                "total_recurring_elements": len(analysis_data.recurring_elements),
                "analysis_version": "1.0"
            }
        }, f, indent=2)
    
    # Run the pipeline
    pipeline = StoryboardPipeline("storyboard_analysis.json", "storyboard_output")
    results = pipeline.run_full_pipeline()
    
    logger.info("Image generation pipeline completed!")
    logger.info(f"Generated {results['pipeline_metadata']['successful_generations']} images")
    logger.info(f"Overall consistency score: {results['consistency_report']['overall_score']:.2f}")
    
    return results

def demonstrate_consistency_features():
    """Demonstrate specific consistency features"""
    logger.info("=" * 60)
    logger.info("DEMONSTRATING CONSISTENCY FEATURES")
    logger.info("=" * 60)
    
    # Load analysis data
    with open("storyboard_analysis.json", "r") as f:
        analysis_data = json.load(f)
    
    print("\nCHARACTER CONSISTENCY:")
    print("-" * 30)
    for char in analysis_data["characters"]:
        print(f"• {char['name']}:")
        print(f"  - Visual: {char['visual_description']}")
        print(f"  - Recurring elements: {char['recurring_elements']}")
        print(f"  - Importance score: {char['importance_score']:.1f}")
        print()
    
    print("\nSCENE CONSISTENCY:")
    print("-" * 30)
    for scene in analysis_data["scene_contexts"]:
        print(f"• Scene {scene['scene_number']}: {scene['location']}")
        print(f"  - Time: {scene['time_of_day']}, Weather: {scene['weather']}")
        print(f"  - Lighting: {scene['lighting']}, Mood: {scene['mood']}")
        print(f"  - Characters: {scene['characters_present']}")
        print()
    
    print("\nRECURRING ELEMENTS:")
    print("-" * 30)
    for elem in analysis_data["recurring_elements"]:
        print(f"• {elem['name']} ({elem['element_type']}) - Scenes: {elem['scene_numbers']}")
    
    print("\nGENERATION STRATEGY:")
    print("-" * 30)
    initial_scenes = [k for k, v in analysis_data["generation_instructions"].items() 
                     if v["generation_type"] == "initial"]
    reference_scenes = [k for k, v in analysis_data["generation_instructions"].items() 
                       if v["generation_type"] == "reference_based"]
    
    print(f"• Initial generation scenes: {len(initial_scenes)}")
    print(f"• Reference-based scenes: {len(reference_scenes)}")
    
    print("\nREFERENCE TEMPLATES:")
    print("-" * 30)
    for scene_id, template_path in analysis_data["reference_templates"].items():
        print(f"• {scene_id}: {template_path}")

def create_integration_guide():
    """Create a guide for integrating with real AI systems"""
    integration_guide = """
# Integration Guide for Real AI Systems

## Stable Diffusion Integration

### 1. AUTOMATIC1111 WebUI
```python
import requests

def generate_with_automatic1111(prompt, negative_prompt, reference_image=None):
    url = "http://localhost:7860/sdapi/v1/txt2img"
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": 1024,
        "height": 1024,
        "steps": 20,
        "cfg_scale": 7.5
    }
    
    if reference_image:
        # Use img2img for reference-based generation
        payload["init_images"] = [reference_image]
        url = "http://localhost:7860/sdapi/v1/img2img"
    
    response = requests.post(url, json=payload)
    return response.json()
```

### 2. ComfyUI Integration
```python
def generate_with_comfyui(prompt, reference_image=None):
    # ComfyUI workflow JSON would go here
    workflow = {
        "prompt": prompt,
        "reference_image": reference_image,
        "workflow_type": "reference_based" if reference_image else "initial"
    }
    return workflow
```

### 3. ControlNet for Pose Consistency
```python
def generate_with_controlnet(scene_data, pose_image=None):
    if pose_image:
        # Use ControlNet for pose consistency
        controlnet_params = {
            "controlnet_model": "openpose",
            "control_image": pose_image,
            "strength": 0.8
        }
    return controlnet_params
```

## API Integration Examples

### OpenAI DALL-E
```python
import openai

def generate_with_dalle(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']
```

### Midjourney API
```python
def generate_with_midjourney(prompt, reference_image=None):
    if reference_image:
        prompt = f"{prompt} --reference {reference_image}"
    
    # Midjourney API call would go here
    return prompt
```

## Custom Model Integration

### Local Model Setup
```python
from diffusers import StableDiffusionPipeline
import torch

def setup_local_model():
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, 
        torch_dtype=torch.float16
    )
    pipe = pipe.to("cuda")
    return pipe

def generate_local(prompt, negative_prompt, reference_image=None):
    pipe = setup_local_model()
    
    if reference_image:
        # Use img2img pipeline
        image = pipe.img2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=reference_image,
            strength=0.7
        ).images[0]
    else:
        # Use txt2img pipeline
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt
        ).images[0]
    
    return image
```

## Batch Processing Optimization

### Parallel Generation
```python
import concurrent.futures
from multiprocessing import Pool

def parallel_generate_scenes(scene_list, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(generate_scene_image, scene) 
            for scene in scene_list
        ]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    return results
```

### Memory Management
```python
def optimize_memory_usage():
    # Clear GPU memory between generations
    torch.cuda.empty_cache()
    
    # Use lower precision for faster generation
    pipe.enable_attention_slicing()
    pipe.enable_xformers_memory_efficient_attention()
```

## Quality Control

### Consistency Checking
```python
def check_consistency(generated_images, reference_images):
    consistency_scores = []
    
    for gen_img, ref_img in zip(generated_images, reference_images):
        # Use perceptual similarity metrics
        similarity = calculate_perceptual_similarity(gen_img, ref_img)
        consistency_scores.append(similarity)
    
    return consistency_scores
```

### Automatic Quality Assessment
```python
def assess_image_quality(image_path):
    # Use CLIP or other models to assess quality
    quality_score = evaluate_image_quality(image_path)
    
    if quality_score < 0.7:
        return "regenerate"
    else:
        return "accept"
```
"""
    
    with open("INTEGRATION_GUIDE.md", "w") as f:
        f.write(integration_guide)
    
    logger.info("Created INTEGRATION_GUIDE.md")

def main():
    """Main demonstration function"""
    logger.info("Starting Complete StoryBoard Pipeline Demonstration")
    
    try:
        # Step 1: Demonstrate script analysis
        analysis_data = demonstrate_analysis()
        
        # Step 2: Demonstrate image generation
        generation_results = demonstrate_image_generation(analysis_data)
        
        # Step 3: Demonstrate consistency features
        demonstrate_consistency_features()
        
        # Step 4: Create integration guide
        create_integration_guide()
        
        logger.info("=" * 60)
        logger.info("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        print("\nGenerated Files:")
        print("• storyboard_analysis.json - Complete analysis data")
        print("• storyboard_output/ - Generated images and results")
        print("• INTEGRATION_GUIDE.md - Guide for real AI integration")
        print("• sample_script.txt - Example script for testing")
        
        print("\nNext Steps:")
        print("1. Review the analysis data in storyboard_analysis.json")
        print("2. Check generated images in storyboard_output/images/")
        print("3. Follow INTEGRATION_GUIDE.md to connect with real AI systems")
        print("4. Modify the pipeline for your specific needs")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise

if __name__ == "__main__":
    main()
