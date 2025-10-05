#!/usr/bin/env python3
"""
AI Image Generation Pipeline for StoryBoard Consistency
======================================================

This module handles the AI image generation process using the frame consistency
data from the storyboard analyzer. It supports both initial generation and
reference-based generation for maintaining visual consistency.

Features:
- Reference image management
- Character consistency across scenes
- Scene background consistency
- Prop and lighting continuity
- Integration with Stable Diffusion and ControlNet
- Batch processing for multiple scenes

Author: AI Assistant
Version: 1.0
"""

import json
import os
import shutil
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from PIL import Image
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Represents a single image generation request"""
    scene_id: str
    prompt: str
    negative_prompt: str
    reference_image_path: Optional[str]
    controlnet_image_path: Optional[str]
    generation_params: Dict
    consistency_tags: List[str]

@dataclass
class GenerationResult:
    """Represents the result of an image generation"""
    scene_id: str
    image_path: str
    generation_time: float
    success: bool
    error_message: Optional[str]
    metadata: Dict

class ReferenceImageManager:
    """Manages reference images for consistency"""
    
    def __init__(self, reference_dir: str = "reference_images"):
        self.reference_dir = Path(reference_dir)
        self.reference_dir.mkdir(exist_ok=True)
        self.reference_registry = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load the reference image registry"""
        registry_file = self.reference_dir / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                self.reference_registry = json.load(f)
    
    def _save_registry(self):
        """Save the reference image registry"""
        registry_file = self.reference_dir / "registry.json"
        with open(registry_file, 'w') as f:
            json.dump(self.reference_registry, f, indent=2)
    
    def register_reference(self, scene_signature: str, image_path: str, metadata: Dict):
        """Register a reference image for a scene signature"""
        self.reference_registry[scene_signature] = {
            "image_path": str(image_path),
            "metadata": metadata,
            "created_at": str(Path(image_path).stat().st_mtime)
        }
        self._save_registry()
    
    def get_reference(self, scene_signature: str) -> Optional[str]:
        """Get the reference image path for a scene signature"""
        if scene_signature in self.reference_registry:
            ref_path = Path(self.reference_registry[scene_signature]["image_path"])
            if ref_path.exists():
                return str(ref_path)
        return None
    
    def create_scene_signature(self, scene_context: Dict) -> str:
        """Create a unique signature for a scene type"""
        location = scene_context.get("location", "unknown")
        time_of_day = scene_context.get("time_of_day", "unknown")
        weather = scene_context.get("weather", "unknown")
        lighting = scene_context.get("lighting", "unknown")
        
        return f"{location}_{time_of_day}_{weather}_{lighting}".lower().replace(" ", "_")
    
    def list_references(self) -> Dict[str, Dict]:
        """List all registered reference images"""
        return self.reference_registry.copy()

class PromptBuilder:
    """Builds detailed prompts for AI image generation"""
    
    def __init__(self):
        self.character_templates = self._load_character_templates()
        self.scene_templates = self._load_scene_templates()
        self.style_keywords = self._load_style_keywords()
    
    def _load_character_templates(self) -> Dict[str, str]:
        """Load character description templates"""
        return {
            "physical": "{trait} {character_name}",
            "clothing": "{character_name} wearing {trait}",
            "accessories": "{character_name} with {trait}",
            "personality": "{character_name}, {trait}",
            "action": "{character_name} {action}"
        }
    
    def _load_scene_templates(self) -> Dict[str, str]:
        """Load scene description templates"""
        return {
            "location": "{location}",
            "time": "{time_of_day}",
            "weather": "{weather} weather",
            "lighting": "{lighting} lighting",
            "mood": "{mood} atmosphere"
        }
    
    def _load_style_keywords(self) -> List[str]:
        """Load style keywords for consistent art direction"""
        return [
            "cinematic lighting",
            "detailed character design",
            "consistent art style",
            "storyboard quality",
            "professional illustration",
            "clear character expressions",
            "detailed backgrounds"
        ]
    
    def build_character_prompt(self, character_data: Dict, action: str = "") -> str:
        """Build a detailed character prompt"""
        prompt_parts = []
        
        # Character name
        character_name = character_data.get("name", "character")
        prompt_parts.append(character_name)
        
        # Visual description
        visual_desc = character_data.get("visual_description", "")
        if visual_desc:
            prompt_parts.append(visual_desc)
        
        # Recurring elements
        recurring = character_data.get("recurring_elements", [])
        if recurring:
            prompt_parts.append(f"with {', '.join(recurring)}")
        
        # Action
        if action:
            prompt_parts.append(action)
        
        return ", ".join(prompt_parts)
    
    def build_scene_prompt(self, scene_context: Dict, characters: List[Dict], props: List[str]) -> str:
        """Build a detailed scene prompt"""
        prompt_parts = []
        
        # Location and setting
        location = scene_context.get("location", "")
        time_of_day = scene_context.get("time_of_day", "")
        weather = scene_context.get("weather", "")
        lighting = scene_context.get("lighting", "")
        mood = scene_context.get("mood", "")
        
        if location and location != "Unknown":
            prompt_parts.append(f"{location}")
        
        if time_of_day and time_of_day != "Unknown":
            prompt_parts.append(f"during {time_of_day}")
        
        if weather and weather != "Unknown":
            prompt_parts.append(f"with {weather} weather")
        
        if lighting and lighting != "Normal":
            prompt_parts.append(f"with {lighting} lighting")
        
        if mood and mood != "Neutral":
            prompt_parts.append(f"creating a {mood} atmosphere")
        
        # Characters
        for char in characters:
            char_prompt = self.build_character_prompt(char)
            prompt_parts.append(char_prompt)
        
        # Props
        if props:
            prompt_parts.append(f"with {', '.join(props)}")
        
        # Style keywords
        prompt_parts.extend(self.style_keywords)
        
        return ", ".join(prompt_parts)
    
    def build_negative_prompt(self) -> str:
        """Build negative prompt to avoid unwanted elements"""
        return ", ".join([
            "blurry",
            "low quality",
            "inconsistent character design",
            "inconsistent lighting",
            "poor composition",
            "text",
            "watermark",
            "signature",
            "multiple characters in same pose",
            "distorted proportions"
        ])

class AIImageGenerator:
    """Main AI image generation class"""
    
    def __init__(self, output_dir: str = "generated_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.reference_manager = ReferenceImageManager()
        self.prompt_builder = PromptBuilder()
        
        # Generation parameters
        self.default_params = {
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "seed": None
        }
    
    def generate_scene_image(self, scene_id: str, instructions: Dict, generation_type: str = "initial") -> GenerationResult:
        """Generate an image for a scene"""
        scene_context = instructions["scene_context"]
        characters = instructions["characters"]
        props = instructions["props"]
        background_elements = instructions["background_elements"]
        
        logger.info(f"Generating image for {scene_id} ({generation_type})")
        
        try:
            # Build prompts
            main_prompt = self.prompt_builder.build_scene_prompt(scene_context, characters, props)
            negative_prompt = self.prompt_builder.build_negative_prompt()
            
            # Handle reference-based generation
            reference_image_path = None
            if generation_type == "reference_based":
                scene_signature = self.reference_manager.create_scene_signature(scene_context)
                reference_image_path = self.reference_manager.get_reference(scene_signature)
                
                if not reference_image_path:
                    logger.warning(f"No reference found for {scene_signature}, falling back to initial generation")
                    generation_type = "initial"
            
            # Create generation request
            request = GenerationRequest(
                scene_id=scene_id,
                prompt=main_prompt,
                negative_prompt=negative_prompt,
                reference_image_path=reference_image_path,
                controlnet_image_path=None,  # Can be added later for pose control
                generation_params=self.default_params.copy(),
                consistency_tags=self._extract_consistency_tags(instructions)
            )
            
            # Generate image
            result = self._execute_generation(request)
            
            # Register as reference if this is the first of its type
            if generation_type == "initial":
                scene_signature = self.reference_manager.create_scene_signature(scene_context)
                self.reference_manager.register_reference(
                    scene_signature, 
                    result.image_path,
                    {"scene_id": scene_id, "generation_type": generation_type}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating image for {scene_id}: {e}")
            return GenerationResult(
                scene_id=scene_id,
                image_path="",
                generation_time=0.0,
                success=False,
                error_message=str(e),
                metadata={}
            )
    
    def _extract_consistency_tags(self, instructions: Dict) -> List[str]:
        """Extract tags for consistency tracking"""
        tags = []
        
        # Character consistency tags
        for char in instructions["characters"]:
            tags.append(f"char_{char['name']}")
            for element in char.get("recurring_elements", []):
                tags.append(f"element_{element}")
        
        # Scene consistency tags
        scene_context = instructions["scene_context"]
        if scene_context.get("location") != "Unknown":
            tags.append(f"location_{scene_context['location']}")
        if scene_context.get("time_of_day") != "Unknown":
            tags.append(f"time_{scene_context['time_of_day']}")
        
        return tags
    
    def _execute_generation(self, request: GenerationRequest) -> GenerationResult:
        """Execute the actual image generation"""
        import time
        start_time = time.time()
        
        # This is a placeholder for actual AI generation
        # In a real implementation, this would call Stable Diffusion API
        # or use local models like AUTOMATIC1111, ComfyUI, etc.
        
        logger.info(f"Generating image with prompt: {request.prompt[:100]}...")
        
        # Simulate generation time
        time.sleep(1)
        
        # Create output filename
        output_filename = f"{request.scene_id}_{int(time.time())}.png"
        output_path = self.output_dir / output_filename
        
        # In a real implementation, this would be the actual generated image
        # For now, create a placeholder
        self._create_placeholder_image(output_path, request.prompt)
        
        generation_time = time.time() - start_time
        
        return GenerationResult(
            scene_id=request.scene_id,
            image_path=str(output_path),
            generation_time=generation_time,
            success=True,
            error_message=None,
            metadata={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "generation_params": request.generation_params,
                "consistency_tags": request.consistency_tags
            }
        )
    
    def _create_placeholder_image(self, output_path: Path, prompt: str):
        """Create a placeholder image for demonstration"""
        # Create a simple colored rectangle as placeholder
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1024, 1024), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Split prompt into lines
        words = prompt.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 50:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text
        y_offset = 50
        for line in lines[:10]:  # Limit to 10 lines
            draw.text((50, y_offset), line, fill='black', font=font)
            y_offset += 30
        
        img.save(output_path)
    
    def batch_generate_scenes(self, analysis_data: Dict) -> List[GenerationResult]:
        """Generate images for all scenes in batch"""
        logger.info("Starting batch generation of all scenes...")
        
        results = []
        generation_instructions = analysis_data["generation_instructions"]
        
        # Sort scenes by generation type (initial first, then reference-based)
        scene_items = list(generation_instructions.items())
        initial_scenes = [(k, v) for k, v in scene_items if v["generation_type"] == "initial"]
        reference_scenes = [(k, v) for k, v in scene_items if v["generation_type"] == "reference_based"]
        
        # Process initial scenes first
        for scene_id, instructions in initial_scenes:
            result = self.generate_scene_image(scene_id, instructions, "initial")
            results.append(result)
        
        # Process reference-based scenes
        for scene_id, instructions in reference_scenes:
            result = self.generate_scene_image(scene_id, instructions, "reference_based")
            results.append(result)
        
        logger.info(f"Batch generation completed. Generated {len(results)} images.")
        return results
    
    def create_video_sequence(self, results: List[GenerationResult], output_video: str = "storyboard_video.mp4"):
        """Create a video sequence from generated images"""
        logger.info(f"Creating video sequence: {output_video}")
        
        # This would use ffmpeg or similar to create video from images
        # For now, just log the image sequence
        image_paths = [r.image_path for r in results if r.success]
        logger.info(f"Video sequence would be created from {len(image_paths)} images")
        logger.info(f"Image sequence: {image_paths}")
        
        return output_video

class StoryboardPipeline:
    """Complete storyboard generation pipeline"""
    
    def __init__(self, analysis_file: str, output_dir: str = "storyboard_output"):
        self.analysis_file = analysis_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.generator = AIImageGenerator(str(self.output_dir / "images"))
        
        # Load analysis data
        with open(analysis_file, 'r') as f:
            self.analysis_data = json.load(f)
    
    def run_full_pipeline(self) -> Dict:
        """Run the complete storyboard generation pipeline"""
        logger.info("Starting full storyboard generation pipeline...")
        
        # Step 1: Generate all scene images
        generation_results = self.generator.batch_generate_scenes(self.analysis_data)
        
        # Step 2: Create video sequence
        video_path = self.generator.create_video_sequence(generation_results)
        
        # Step 3: Generate consistency report
        consistency_report = self._generate_consistency_report(generation_results)
        
        # Step 4: Save pipeline results
        pipeline_results = {
            "generation_results": [asdict(r) for r in generation_results],
            "video_path": video_path,
            "consistency_report": consistency_report,
            "reference_images": self.generator.reference_manager.list_references(),
            "pipeline_metadata": {
                "total_scenes": len(generation_results),
                "successful_generations": len([r for r in generation_results if r.success]),
                "failed_generations": len([r for r in generation_results if not r.success]),
                "total_generation_time": sum(r.generation_time for r in generation_results)
            }
        }
        
        # Save results
        results_file = self.output_dir / "pipeline_results.json"
        with open(results_file, 'w') as f:
            json.dump(pipeline_results, f, indent=2)
        
        logger.info(f"Pipeline completed. Results saved to {results_file}")
        return pipeline_results
    
    def _generate_consistency_report(self, results: List[GenerationResult]) -> Dict:
        """Generate a consistency analysis report"""
        report = {
            "character_consistency": {},
            "scene_consistency": {},
            "overall_score": 0.0
        }
        
        # Analyze character consistency
        character_tags = {}
        for result in results:
            if result.success:
                for tag in result.metadata.get("consistency_tags", []):
                    if tag.startswith("char_"):
                        char_name = tag[5:]
                        if char_name not in character_tags:
                            character_tags[char_name] = []
                        character_tags[char_name].append(result.scene_id)
        
        report["character_consistency"] = character_tags
        
        # Analyze scene consistency
        scene_tags = {}
        for result in results:
            if result.success:
                for tag in result.metadata.get("consistency_tags", []):
                    if tag.startswith("location_"):
                        location = tag[9:]
                        if location not in scene_tags:
                            scene_tags[location] = []
                        scene_tags[location].append(result.scene_id)
        
        report["scene_consistency"] = scene_tags
        
        # Calculate overall consistency score
        total_scenes = len(results)
        successful_scenes = len([r for r in results if r.success])
        report["overall_score"] = successful_scenes / total_scenes if total_scenes > 0 else 0.0
        
        return report

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Image Generation Pipeline for StoryBoard')
    parser.add_argument('analysis_file', help='Path to the storyboard analysis JSON file')
    parser.add_argument('-o', '--output', default='storyboard_output', 
                       help='Output directory (default: storyboard_output)')
    parser.add_argument('--batch', action='store_true', 
                       help='Run batch generation for all scenes')
    parser.add_argument('--scene', help='Generate image for specific scene ID')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.analysis_file):
        logger.error(f"Analysis file not found: {args.analysis_file}")
        return
    
    pipeline = StoryboardPipeline(args.analysis_file, args.output)
    
    if args.scene:
        # Generate single scene
        scene_data = None
        for scene_id, instructions in pipeline.analysis_data["generation_instructions"].items():
            if scene_id == args.scene:
                scene_data = instructions
                break
        
        if scene_data:
            result = pipeline.generator.generate_scene_image(args.scene, scene_data)
            logger.info(f"Generated image for {args.scene}: {result.image_path}")
        else:
            logger.error(f"Scene {args.scene} not found in analysis data")
    
    elif args.batch:
        # Run full pipeline
        results = pipeline.run_full_pipeline()
        logger.info("Full pipeline completed successfully")
    
    else:
        logger.info("Use --batch to run full pipeline or --scene <scene_id> for single scene")

if __name__ == "__main__":
    main()
