#!/usr/bin/env python3
"""
StoryBoard Analyzer - Frame-Level Consistency System
====================================================

This system provides comprehensive frame-level consistency for storyboard generation:
- Character consistency (appearance, traits, recurring elements)
- Scene consistency (backgrounds, props, lighting, mood)
- Reference-based image generation for maintaining visual continuity
- Structured JSON output for AI image generation pipeline

Author: AI Assistant
Version: 1.0
"""

import json
import re
import os
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CharacterTrait:
    """Represents a character trait with confidence score"""
    trait: str
    confidence: float
    context: str  # The sentence/phrase where this trait was found

@dataclass
class Character:
    """Represents a character with all their traits and visual elements"""
    name: str
    aliases: List[str]
    traits: List[CharacterTrait]
    visual_description: str
    recurring_elements: List[str]  # Items they always have (glasses, hat, etc.)
    importance_score: float  # How central they are to the story
    first_appearance: int  # Scene number where they first appear

@dataclass
class SceneElement:
    """Represents a scene element (prop, background, lighting)"""
    element_type: str  # 'prop', 'background', 'lighting', 'mood'
    name: str
    description: str
    recurring: bool
    scene_numbers: List[int]

@dataclass
class SceneContext:
    """Represents the context of a scene"""
    scene_number: int
    location: str
    time_of_day: str
    weather: str
    mood: str
    lighting: str
    props: List[str]
    characters_present: List[str]
    background_elements: List[str]

@dataclass
class FrameConsistencyData:
    """Complete frame consistency data for the storyboard"""
    characters: List[Character]
    scene_contexts: List[SceneContext]
    recurring_elements: List[SceneElement]
    reference_templates: Dict[str, str]  # Scene ID -> reference image path
    generation_instructions: Dict[str, Dict]  # Scene ID -> AI generation params

class StoryboardAnalyzer:
    """Main analyzer class for frame-level consistency"""
    
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.scene_contexts: List[SceneContext] = []
        self.recurring_elements: Dict[str, SceneElement] = {}
        self.character_traits_db = self._load_character_traits_db()
        self.scene_patterns = self._load_scene_patterns()
        
    def _load_character_traits_db(self) -> Dict[str, List[str]]:
        """Load database of common character traits and their indicators"""
        return {
            'physical': [
                'tall', 'short', 'thin', 'fat', 'muscular', 'slim', 'athletic',
                'blonde', 'brunette', 'redhead', 'bald', 'curly hair', 'straight hair',
                'blue eyes', 'brown eyes', 'green eyes', 'glasses', 'beard', 'mustache'
            ],
            'personality': [
                'brave', 'cowardly', 'smart', 'dumb', 'funny', 'serious', 'kind',
                'mean', 'angry', 'happy', 'sad', 'confident', 'shy', 'outgoing',
                'quiet', 'loud', 'patient', 'impatient', 'careful', 'reckless'
            ],
            'clothing': [
                'suit', 'dress', 'jeans', 'shirt', 'hat', 'cap', 'jacket',
                'coat', 'shoes', 'boots', 'uniform', 'casual', 'formal'
            ],
            'accessories': [
                'glasses', 'watch', 'necklace', 'ring', 'bag', 'backpack',
                'phone', 'camera', 'weapon', 'tool', 'book'
            ]
        }
    
    def _load_scene_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting scene elements"""
        return {
            'locations': [
                'house', 'apartment', 'office', 'school', 'hospital', 'restaurant',
                'park', 'street', 'car', 'bus', 'train', 'airport', 'beach',
                'forest', 'mountain', 'city', 'countryside', 'kitchen', 'bedroom',
                'living room', 'garden', 'garage', 'basement', 'attic'
            ],
            'time_indicators': [
                'morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk',
                'sunrise', 'sunset', 'midday', 'midnight', 'early', 'late'
            ],
            'weather': [
                'sunny', 'cloudy', 'rainy', 'stormy', 'snowy', 'foggy',
                'windy', 'hot', 'cold', 'warm', 'cool'
            ],
            'mood_indicators': [
                'tense', 'relaxed', 'exciting', 'scary', 'romantic', 'sad',
                'happy', 'mysterious', 'dramatic', 'peaceful', 'chaotic'
            ],
            'lighting': [
                'bright', 'dim', 'dark', 'shadowy', 'sunlit', 'moonlit',
                'artificial', 'natural', 'harsh', 'soft', 'dramatic'
            ]
        }
    
    def analyze_script(self, script_text: str) -> FrameConsistencyData:
        """
        Main analysis function that processes the script and extracts
        all frame consistency information
        """
        logger.info("Starting script analysis for frame-level consistency...")
        
        # Step 1: Extract characters and their traits
        characters = self._extract_characters(script_text)
        
        # Step 2: Analyze scene contexts
        scene_contexts = self._analyze_scene_contexts(script_text)
        
        # Step 3: Identify recurring elements
        recurring_elements = self._identify_recurring_elements(scene_contexts)
        
        # Step 4: Generate reference templates
        reference_templates = self._generate_reference_templates(scene_contexts, characters)
        
        # Step 5: Create generation instructions
        generation_instructions = self._create_generation_instructions(
            scene_contexts, characters, recurring_elements
        )
        
        return FrameConsistencyData(
            characters=list(characters.values()),
            scene_contexts=scene_contexts,
            recurring_elements=list(recurring_elements.values()),
            reference_templates=reference_templates,
            generation_instructions=generation_instructions
        )
    
    def _extract_characters(self, script_text: str) -> Dict[str, Character]:
        """Extract characters and analyze their traits"""
        logger.info("Extracting characters and traits...")
        
        # Find character names (capitalized words that appear multiple times)
        character_names = self._find_character_names(script_text)
        
        characters = {}
        for name in character_names:
            aliases = self._find_character_aliases(name, script_text)
            traits = self._extract_character_traits(name, aliases, script_text)
            visual_description = self._build_visual_description(traits)
            recurring_elements = self._find_recurring_elements(name, aliases, script_text)
            importance_score = self._calculate_importance_score(name, aliases, script_text)
            first_appearance = self._find_first_appearance(name, aliases, script_text)
            
            characters[name] = Character(
                name=name,
                aliases=aliases,
                traits=traits,
                visual_description=visual_description,
                recurring_elements=recurring_elements,
                importance_score=importance_score,
                first_appearance=first_appearance
            )
        
        return characters
    
    def _find_character_names(self, script_text: str) -> Set[str]:
        """Find potential character names in the script"""
        # Look for capitalized words that appear multiple times
        words = re.findall(r'\b[A-Z][a-z]+\b', script_text)
        word_counts = Counter(words)
        
        # Filter out common non-character words
        common_words = {
            'The', 'A', 'An', 'And', 'But', 'Or', 'In', 'On', 'At', 'To', 'For',
            'Of', 'With', 'By', 'From', 'Up', 'Down', 'Out', 'Off', 'Over',
            'Under', 'Again', 'Further', 'Then', 'Once', 'Here', 'There',
            'When', 'Where', 'Why', 'How', 'All', 'Any', 'Both', 'Each',
            'Few', 'More', 'Most', 'Other', 'Some', 'Such', 'No', 'Nor',
            'Not', 'Only', 'Own', 'Same', 'So', 'Than', 'Too', 'Very',
            'Can', 'Will', 'Just', 'Should', 'Now', 'Scene', 'Morning',
            'Afternoon', 'Evening', 'Night', 'Living', 'Room', 'Kitchen',
            'Office', 'Coffee', 'Shop', 'House', 'Apartment', 'Park',
            'Street', 'Car', 'Bus', 'Train', 'Airport', 'Beach', 'Forest',
            'Mountain', 'City', 'Countryside', 'Garden', 'Garage', 'Basement',
            'Attic', 'Bright', 'Dim', 'Dark', 'Sunny', 'Cloudy', 'Rainy',
            'Stormy', 'Snowy', 'Foggy', 'Windy', 'Hot', 'Cold', 'Warm',
            'Cool', 'Tense', 'Relaxed', 'Exciting', 'Scary', 'Romantic',
            'Sad', 'Happy', 'Mysterious', 'Dramatic', 'Peaceful', 'Chaotic',
            'He', 'She', 'It', 'They', 'We', 'You', 'Me', 'Him', 'Her',
            'Us', 'Them', 'This', 'That', 'These', 'Those', 'What', 'Who',
            'Which', 'Whose', 'Whom', 'Where', 'When', 'Why', 'How'
        }
        
        # Return words that appear at least 2 times and aren't common words
        character_names = {
            word for word, count in word_counts.items()
            if count >= 2 and word not in common_words
        }
        
        return character_names
    
    def _find_character_aliases(self, name: str, script_text: str) -> List[str]:
        """Find aliases and nicknames for a character"""
        aliases = set()
        
        # Look for patterns like "John (nickname)" or "John, called nickname"
        patterns = [
            rf'{re.escape(name)}\s*\(([^)]+)\)',
            rf'{re.escape(name)},\s*called\s+([^,\.]+)',
            rf'{re.escape(name)},\s*known\s+as\s+([^,\.]+)',
            rf'{re.escape(name)},\s*also\s+called\s+([^,\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, script_text, re.IGNORECASE)
            aliases.update(matches)
        
        return list(aliases)
    
    def _extract_character_traits(self, name: str, aliases: List[str], script_text: str) -> List[CharacterTrait]:
        """Extract character traits from the script"""
        traits = []
        all_names = [name] + aliases
        
        # Split script into sentences for context
        sentences = re.split(r'[.!?]+', script_text)
        
        for sentence in sentences:
            # Check if this sentence mentions the character
            if not any(n.lower() in sentence.lower() for n in all_names):
                continue
            
            # Look for trait indicators
            for trait_category, trait_list in self.character_traits_db.items():
                for trait in trait_list:
                    if trait.lower() in sentence.lower():
                        # Calculate confidence based on context
                        confidence = self._calculate_trait_confidence(trait, sentence, name)
                        if confidence > 0.3:  # Threshold for inclusion
                            traits.append(CharacterTrait(
                                trait=trait,
                                confidence=confidence,
                                context=sentence.strip()
                            ))
        
        # Remove duplicates and sort by confidence
        unique_traits = {}
        for trait in traits:
            if trait.trait not in unique_traits or trait.confidence > unique_traits[trait.trait].confidence:
                unique_traits[trait.trait] = trait
        
        return sorted(unique_traits.values(), key=lambda x: x.confidence, reverse=True)
    
    def _calculate_trait_confidence(self, trait: str, sentence: str, character_name: str) -> float:
        """Calculate confidence score for a character trait"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if trait is close to character name
        trait_pos = sentence.lower().find(trait.lower())
        name_pos = sentence.lower().find(character_name.lower())
        
        if trait_pos != -1 and name_pos != -1:
            distance = abs(trait_pos - name_pos)
            if distance < 50:  # Within 50 characters
                confidence += 0.3
        
        # Increase confidence for direct descriptions
        direct_patterns = [
            rf'{re.escape(character_name)}\s+is\s+{re.escape(trait)}',
            rf'{re.escape(character_name)}\s+looks\s+{re.escape(trait)}',
            rf'{re.escape(character_name)}\s+appears\s+{re.escape(trait)}',
            rf'{re.escape(character_name)}\s+seems\s+{re.escape(trait)}'
        ]
        
        for pattern in direct_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                confidence += 0.4
        
        return min(confidence, 1.0)
    
    def _build_visual_description(self, traits: List[CharacterTrait]) -> str:
        """Build a visual description from character traits"""
        physical_traits = []
        clothing_traits = []
        accessory_traits = []
        
        for trait in traits:
            if trait.trait in self.character_traits_db['physical']:
                physical_traits.append(trait.trait)
            elif trait.trait in self.character_traits_db['clothing']:
                clothing_traits.append(trait.trait)
            elif trait.trait in self.character_traits_db['accessories']:
                accessory_traits.append(trait.trait)
        
        description_parts = []
        if physical_traits:
            description_parts.append(f"Physical: {', '.join(physical_traits)}")
        if clothing_traits:
            description_parts.append(f"Clothing: {', '.join(clothing_traits)}")
        if accessory_traits:
            description_parts.append(f"Accessories: {', '.join(accessory_traits)}")
        
        return "; ".join(description_parts)
    
    def _find_recurring_elements(self, name: str, aliases: List[str], script_text: str) -> List[str]:
        """Find recurring visual elements associated with a character"""
        recurring = []
        all_names = [name] + aliases
        
        # Look for items that appear multiple times with the character
        sentences = re.split(r'[.!?]+', script_text)
        item_counts = defaultdict(int)
        
        for sentence in sentences:
            if not any(n.lower() in sentence.lower() for n in all_names):
                continue
            
            # Look for common items
            items = ['glasses', 'hat', 'coat', 'bag', 'phone', 'watch', 'ring', 'necklace']
            for item in items:
                if item in sentence.lower():
                    item_counts[item] += 1
        
        # Return items that appear at least twice
        for item, count in item_counts.items():
            if count >= 2:
                recurring.append(item)
        
        return recurring
    
    def _calculate_importance_score(self, name: str, aliases: List[str], script_text: str) -> float:
        """Calculate how important a character is to the story"""
        all_names = [name] + aliases
        total_mentions = 0
        
        for n in all_names:
            total_mentions += len(re.findall(rf'\b{re.escape(n)}\b', script_text, re.IGNORECASE))
        
        # Normalize by script length
        script_length = len(script_text.split())
        importance = total_mentions / script_length * 1000  # Scale up for readability
        
        return min(importance, 10.0)  # Cap at 10
    
    def _find_first_appearance(self, name: str, aliases: List[str], script_text: str) -> int:
        """Find the scene number where character first appears"""
        all_names = [name] + aliases
        
        # Split script into scenes (simple approach)
        scenes = re.split(r'\n\s*Scene\s+\d+', script_text)
        
        for i, scene in enumerate(scenes):
            if any(n.lower() in scene.lower() for n in all_names):
                return i + 1
        
        return 1  # Default to scene 1
    
    def _analyze_scene_contexts(self, script_text: str) -> List[SceneContext]:
        """Analyze each scene for context information"""
        logger.info("Analyzing scene contexts...")
        
        # Split script into scenes
        scenes = re.split(r'\n\s*Scene\s+\d+', script_text)
        scene_contexts = []
        
        for i, scene in enumerate(scenes):
            if not scene.strip():
                continue
            
            scene_number = i + 1
            location = self._extract_location(scene)
            time_of_day = self._extract_time_of_day(scene)
            weather = self._extract_weather(scene)
            mood = self._extract_mood(scene)
            lighting = self._extract_lighting(scene)
            props = self._extract_props(scene)
            characters_present = self._extract_characters_in_scene(scene)
            background_elements = self._extract_background_elements(scene)
            
            scene_contexts.append(SceneContext(
                scene_number=scene_number,
                location=location,
                time_of_day=time_of_day,
                weather=weather,
                mood=mood,
                lighting=lighting,
                props=props,
                characters_present=characters_present,
                background_elements=background_elements
            ))
        
        return scene_contexts
    
    def _extract_location(self, scene_text: str) -> str:
        """Extract location from scene text"""
        scene_lower = scene_text.lower()
        
        for location in self.scene_patterns['locations']:
            if location in scene_lower:
                return location.title()
        
        # Look for location indicators
        location_patterns = [
            r'in\s+the\s+([a-z\s]+)',
            r'at\s+the\s+([a-z\s]+)',
            r'inside\s+the\s+([a-z\s]+)',
            r'outside\s+the\s+([a-z\s]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, scene_lower)
            if match:
                return match.group(1).strip().title()
        
        return "Unknown"
    
    def _extract_time_of_day(self, scene_text: str) -> str:
        """Extract time of day from scene text"""
        scene_lower = scene_text.lower()
        
        for time_indicator in self.scene_patterns['time_indicators']:
            if time_indicator in scene_lower:
                return time_indicator.title()
        
        return "Unknown"
    
    def _extract_weather(self, scene_text: str) -> str:
        """Extract weather from scene text"""
        scene_lower = scene_text.lower()
        
        for weather_type in self.scene_patterns['weather']:
            if weather_type in scene_lower:
                return weather_type.title()
        
        return "Unknown"
    
    def _extract_mood(self, scene_text: str) -> str:
        """Extract mood from scene text"""
        scene_lower = scene_text.lower()
        
        for mood_indicator in self.scene_patterns['mood_indicators']:
            if mood_indicator in scene_lower:
                return mood_indicator.title()
        
        return "Neutral"
    
    def _extract_lighting(self, scene_text: str) -> str:
        """Extract lighting information from scene text"""
        scene_lower = scene_text.lower()
        
        for lighting_type in self.scene_patterns['lighting']:
            if lighting_type in scene_lower:
                return lighting_type.title()
        
        return "Normal"
    
    def _extract_props(self, scene_text: str) -> List[str]:
        """Extract props and objects from scene text"""
        props = []
        
        # Common prop patterns
        prop_patterns = [
            r'a\s+([a-z\s]+)\s+(?:sits|stands|lies)',
            r'the\s+([a-z\s]+)\s+(?:is|was)',
            r'holding\s+a\s+([a-z\s]+)',
            r'carrying\s+a\s+([a-z\s]+)',
            r'with\s+a\s+([a-z\s]+)'
        ]
        
        for pattern in prop_patterns:
            matches = re.findall(pattern, scene_text.lower())
            props.extend([match.strip() for match in matches])
        
        # Filter out common non-prop words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        props = [prop for prop in props if prop not in common_words and len(prop) > 2]
        
        return list(set(props))  # Remove duplicates
    
    def _extract_characters_in_scene(self, scene_text: str) -> List[str]:
        """Extract characters present in this scene"""
        characters_present = []
        
        for char_name in self.characters.keys():
            if char_name.lower() in scene_text.lower():
                characters_present.append(char_name)
        
        return characters_present
    
    def _extract_background_elements(self, scene_text: str) -> List[str]:
        """Extract background elements from scene text"""
        background_elements = []
        
        # Look for background descriptions
        background_patterns = [
            r'in\s+the\s+background',
            r'behind\s+them',
            r'around\s+the\s+([a-z\s]+)',
            r'surrounded\s+by\s+([a-z\s]+)'
        ]
        
        for pattern in background_patterns:
            matches = re.findall(pattern, scene_text.lower())
            background_elements.extend([match.strip() for match in matches])
        
        return list(set(background_elements))
    
    def _identify_recurring_elements(self, scene_contexts: List[SceneContext]) -> Dict[str, SceneElement]:
        """Identify elements that appear in multiple scenes"""
        logger.info("Identifying recurring elements...")
        
        element_counts = defaultdict(list)
        recurring_elements = {}
        
        # Collect all elements by type
        for scene in scene_contexts:
            # Props
            for prop in scene.props:
                element_counts[f"prop_{prop}"].append(scene.scene_number)
            
            # Background elements
            for bg in scene.background_elements:
                element_counts[f"background_{bg}"].append(scene.scene_number)
            
            # Locations
            if scene.location != "Unknown":
                element_counts[f"location_{scene.location}"].append(scene.scene_number)
        
        # Identify recurring elements (appear in 2+ scenes)
        for element_key, scene_numbers in element_counts.items():
            if len(scene_numbers) >= 2:
                element_type, name = element_key.split('_', 1)
                
                recurring_elements[element_key] = SceneElement(
                    element_type=element_type,
                    name=name,
                    description=f"Recurring {element_type}: {name}",
                    recurring=True,
                    scene_numbers=scene_numbers
                )
        
        return recurring_elements
    
    def _generate_reference_templates(self, scene_contexts: List[SceneContext], characters: Dict[str, Character]) -> Dict[str, str]:
        """Generate reference template paths for each unique scene"""
        logger.info("Generating reference templates...")
        
        reference_templates = {}
        scene_signatures = {}
        
        for scene in scene_contexts:
            # Create a signature for this scene type
            signature = f"{scene.location}_{scene.time_of_day}_{scene.weather}_{scene.lighting}"
            
            if signature not in scene_signatures:
                scene_signatures[signature] = scene.scene_number
                reference_templates[f"scene_{scene.scene_number}"] = f"reference_{signature}.png"
        
        return reference_templates
    
    def _create_generation_instructions(self, scene_contexts: List[SceneContext], 
                                     characters: Dict[str, Character], 
                                     recurring_elements: Dict[str, SceneElement]) -> Dict[str, Dict]:
        """Create detailed generation instructions for each scene"""
        logger.info("Creating generation instructions...")
        
        generation_instructions = {}
        
        for scene in scene_contexts:
            scene_id = f"scene_{scene.scene_number}"
            
            # Character descriptions for this scene
            character_descriptions = {}
            for char_name in scene.characters_present:
                if char_name in characters:
                    char = characters[char_name]
                    character_descriptions[char_name] = {
                        "visual_description": char.visual_description,
                        "recurring_elements": char.recurring_elements,
                        "traits": [t.trait for t in char.traits[:5]]  # Top 5 traits
                    }
            
            # Scene-specific instructions
            instructions = {
                "scene_context": {
                    "location": scene.location,
                    "time_of_day": scene.time_of_day,
                    "weather": scene.weather,
                    "mood": scene.mood,
                    "lighting": scene.lighting
                },
                "characters": character_descriptions,
                "props": scene.props,
                "background_elements": scene.background_elements,
                "recurring_elements": [
                    elem.name for elem in recurring_elements.values() 
                    if scene.scene_number in elem.scene_numbers
                ],
                "generation_type": "reference_based" if scene_id in self._get_reference_scenes(scene_contexts) else "initial",
                "consistency_requirements": {
                    "maintain_character_appearance": True,
                    "maintain_scene_background": True,
                    "maintain_lighting_mood": True,
                    "maintain_prop_consistency": True
                }
            }
            
            generation_instructions[scene_id] = instructions
        
        return generation_instructions
    
    def _get_reference_scenes(self, scene_contexts: List[SceneContext]) -> Set[str]:
        """Get scene IDs that should use reference-based generation"""
        reference_scenes = set()
        scene_signatures = {}
        
        for scene in scene_contexts:
            signature = f"{scene.location}_{scene.time_of_day}_{scene.weather}_{scene.lighting}"
            
            if signature in scene_signatures:
                # This is a recurring scene type, use reference
                reference_scenes.add(f"scene_{scene.scene_number}")
            else:
                scene_signatures[signature] = scene.scene_number
        
        return reference_scenes
    
    def save_analysis(self, data: FrameConsistencyData, output_file: str):
        """Save the analysis results to a JSON file"""
        logger.info(f"Saving analysis results to {output_file}")
        
        # Convert dataclasses to dictionaries
        output_data = {
            "characters": [asdict(char) for char in data.characters],
            "scene_contexts": [asdict(scene) for scene in data.scene_contexts],
            "recurring_elements": [asdict(elem) for elem in data.recurring_elements],
            "reference_templates": data.reference_templates,
            "generation_instructions": data.generation_instructions,
            "metadata": {
                "total_characters": len(data.characters),
                "total_scenes": len(data.scene_contexts),
                "total_recurring_elements": len(data.recurring_elements),
                "analysis_version": "1.0"
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis saved successfully to {output_file}")
    
    def generate_summary_report(self, data: FrameConsistencyData) -> str:
        """Generate a human-readable summary report"""
        report = []
        report.append("=" * 60)
        report.append("STORYBOARD FRAME CONSISTENCY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Character summary
        report.append("CHARACTERS:")
        report.append("-" * 20)
        for char in sorted(data.characters, key=lambda x: x.importance_score, reverse=True):
            report.append(f"• {char.name} (Importance: {char.importance_score:.1f})")
            report.append(f"  - Visual: {char.visual_description}")
            report.append(f"  - Recurring elements: {', '.join(char.recurring_elements) if char.recurring_elements else 'None'}")
            report.append(f"  - Top traits: {', '.join([t.trait for t in char.traits[:3]])}")
            report.append("")
        
        # Scene summary
        report.append("SCENE BREAKDOWN:")
        report.append("-" * 20)
        for scene in data.scene_contexts:
            report.append(f"Scene {scene.scene_number}: {scene.location}")
            report.append(f"  - Time: {scene.time_of_day}, Weather: {scene.weather}")
            report.append(f"  - Mood: {scene.mood}, Lighting: {scene.lighting}")
            report.append(f"  - Characters: {', '.join(scene.characters_present)}")
            report.append(f"  - Props: {', '.join(scene.props) if scene.props else 'None'}")
            report.append("")
        
        # Recurring elements
        if data.recurring_elements:
            report.append("RECURRING ELEMENTS:")
            report.append("-" * 20)
            for elem in data.recurring_elements:
                report.append(f"• {elem.name} ({elem.element_type}) - Scenes: {elem.scene_numbers}")
            report.append("")
        
        # Generation strategy
        report.append("GENERATION STRATEGY:")
        report.append("-" * 20)
        initial_scenes = [k for k, v in data.generation_instructions.items() if v["generation_type"] == "initial"]
        reference_scenes = [k for k, v in data.generation_instructions.items() if v["generation_type"] == "reference_based"]
        
        report.append(f"• Initial generation scenes: {len(initial_scenes)}")
        report.append(f"• Reference-based scenes: {len(reference_scenes)}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='StoryBoard Frame Consistency Analyzer')
    parser.add_argument('script_file', help='Path to the script file to analyze')
    parser.add_argument('-o', '--output', default='storyboard_analysis.json', 
                       help='Output JSON file (default: storyboard_analysis.json)')
    parser.add_argument('-r', '--report', help='Generate summary report file')
    
    args = parser.parse_args()
    
    # Read script file
    try:
        with open(args.script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
    except FileNotFoundError:
        logger.error(f"Script file not found: {args.script_file}")
        return
    except Exception as e:
        logger.error(f"Error reading script file: {e}")
        return
    
    # Analyze script
    analyzer = StoryboardAnalyzer()
    try:
        analysis_data = analyzer.analyze_script(script_text)
        
        # Save results
        analyzer.save_analysis(analysis_data, args.output)
        
        # Generate report if requested
        if args.report:
            report = analyzer.generate_summary_report(analysis_data)
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Summary report saved to {args.report}")
        
        # Print summary to console
        print(analyzer.generate_summary_report(analysis_data))
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
