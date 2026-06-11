# StoryBoard Frame-Level Consistency System

A comprehensive system for maintaining visual consistency across storyboard frames, including character consistency, scene consistency, and reference-based image generation.

## Project Status

This project was developed during the CineHack Hackathon as a proof-of-concept prototype.

The goal was to build an AI-assisted system capable of transforming scripts into storyboard-driven videos while maintaining character and scene consistency.

Development reached the prototype stage and successfully demonstrated the core architecture involving script analysis, storyboard processing, computer vision, and AI-assisted video generation concepts. Further development was limited by technical constraints and available hardware resources during the hackathon.


...


## 🎯 Features

### Frame-Level Consistency
- **Character Consistency**: Maintains character appearance, traits, and recurring elements across all scenes
- **Scene Consistency**: Preserves backgrounds, props, lighting, and mood continuity
- **Reference-Based Generation**: Uses reference images for consistent visual elements
- **Automated Analysis**: Extracts characters, scenes, and context from scripts automatically

### AI Integration Ready
- **Stable Diffusion Support**: Ready for integration with AUTOMATIC1111, ComfyUI, and other SD interfaces
- **ControlNet Integration**: Supports pose and style consistency
- **Batch Processing**: Efficient generation of multiple scenes
- **Quality Control**: Built-in consistency checking and quality assessment

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the system
git clone <repository-url>
cd StoryBoard

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Analyze a script and generate storyboard
python complete_pipeline.py your_script.txt

# Or run individual components
python storyboard_analyzer.py your_script.txt -o analysis.json
python ai_image_generator.py analysis.json --batch
```

### 3. Example Script Format

```
Scene 1: The Living Room - Morning

Sarah, a tall blonde woman with glasses, sits on the couch in her living room. 
She's wearing a blue sweater and reading a book. The morning sun streams through 
the window, creating bright lighting. The room has a cozy, peaceful atmosphere 
with a coffee table and lamp nearby.

Scene 2: The Kitchen - Morning

Sarah walks into the kitchen, still wearing her blue sweater and glasses. She 
puts the book on the counter and starts making coffee. The kitchen has bright 
morning lighting and feels warm and inviting.
```

## 📁 System Architecture

### Core Components

1. **`storyboard_analyzer.py`** - Script analysis and character/scene extraction
2. **`ai_image_generator.py`** - AI image generation with consistency management
3. **`complete_pipeline.py`** - End-to-end pipeline demonstration

### Data Flow

```
Script Text → Character Analysis → Scene Context → Reference Management → AI Generation → Video Output
```

## 🔧 Configuration

### Character Analysis Settings

The system automatically detects:
- **Physical traits**: height, hair color, eye color, build
- **Personality traits**: brave, smart, funny, etc.
- **Clothing**: consistent outfits and accessories
- **Recurring elements**: glasses, hat, specific items

### Scene Analysis Settings

Extracts:
- **Location**: house, office, park, etc.
- **Time of day**: morning, afternoon, evening, night
- **Weather**: sunny, rainy, cloudy, etc.
- **Lighting**: bright, dim, dramatic, etc.
- **Mood**: tense, relaxed, mysterious, etc.

## 🎨 AI Integration

### Stable Diffusion Integration

```python
# Example integration with AUTOMATIC1111
def generate_with_sd(prompt, reference_image=None):
    if reference_image:
        # Use img2img for consistency
        return img2img_generation(prompt, reference_image)
    else:
        # Initial generation
        return txt2img_generation(prompt)
```

### Custom Model Integration

```python
# Example with local model
from diffusers import StableDiffusionPipeline

def setup_pipeline():
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5"
    )
    return pipe
```

## 📊 Output Structure

### Analysis JSON Format

```json
{
  "characters": [
    {
      "name": "Sarah",
      "visual_description": "Physical: tall, blonde; Clothing: blue sweater; Accessories: glasses",
      "recurring_elements": ["glasses", "blue sweater"],
      "importance_score": 8.5,
      "traits": [...]
    }
  ],
  "scene_contexts": [
    {
      "scene_number": 1,
      "location": "Living Room",
      "time_of_day": "Morning",
      "lighting": "Bright",
      "mood": "Peaceful",
      "characters_present": ["Sarah"]
    }
  ],
  "generation_instructions": {
    "scene_1": {
      "generation_type": "initial",
      "scene_context": {...},
      "characters": {...},
      "consistency_requirements": {...}
    }
  }
}
```

## 🔄 Pipeline Workflow

### 1. Script Analysis
- Extract character names and traits
- Identify scene contexts and settings
- Detect recurring elements
- Calculate importance scores

### 2. Reference Management
- Create reference templates for unique scene types
- Track character consistency requirements
- Manage recurring element continuity

### 3. Image Generation
- Generate initial images for new scene types
- Use reference-based generation for recurring scenes
- Maintain character and scene consistency
- Apply quality control measures

### 4. Video Compilation
- Sequence generated images
- Create smooth transitions
- Export final storyboard video

## 🛠️ Advanced Features

### Batch Processing

```bash
# Process multiple scripts
python storyboard_analyzer.py script1.txt script2.txt script3.txt

# Generate all scenes in batch
python ai_image_generator.py analysis.json --batch
```

### Custom Character Templates

```python
# Add custom character traits
analyzer.character_traits_db['custom'] = ['magical', 'mystical', 'enchanted']
```

### Scene Pattern Recognition

```python
# Add custom scene patterns
analyzer.scene_patterns['locations'].extend(['castle', 'dungeon', 'tower'])
```

## 📈 Consistency Metrics

The system tracks:
- **Character Consistency Score**: How well characters maintain appearance
- **Scene Consistency Score**: Background and setting continuity
- **Overall Pipeline Score**: Combined consistency rating
- **Generation Success Rate**: Percentage of successful image generations

## 🔍 Troubleshooting

### Common Issues

1. **Character not detected**: Ensure character names are capitalized and appear multiple times
2. **Scene context missing**: Add more descriptive text about locations and settings
3. **Generation failures**: Check AI model availability and API keys

### Debug Mode

```bash
# Enable detailed logging
python storyboard_analyzer.py script.txt --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for storyboard creators and animators
- Compatible with major AI image generation platforms
- Designed for both individual creators and production teams

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the INTEGRATION_GUIDE.md for technical details
- Review example scripts in the examples/ directory

---

**Happy Storyboarding! 🎬✨**
