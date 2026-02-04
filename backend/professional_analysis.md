# Professional Script Analysis vs Current Agent Output

## The Benchmark: example_script.txt

This is a **Hollywood-level** sci-fi trailer script with:

### 1. Technical Cinematography Precision
- **Shot Types**: СУПЕР-ТОТАЛ (super-wide), КРУПНЫЙ ПЛАН (close-up), СУБЪЕКТИВНАЯ КАМЕРА (POV)
- **Camera Movements**: "плавный облет" (smooth orbit), "Crane Shot" (rising camera)
- **Timing Precision**: Exact timestamps (0:35-0:50, 1:10-1:40)
- **Transitions**: "КАДР-ВСПЫШКА" (flash frame), "Затемнение" (fade to black)

### 2. Visual Effects Specifications
- **Glitch Effects**: "текстуры земли накладываются друг на друга" (textures overlaying)
- **Physics Breaking**: "океан ЗАМЕР" (ocean frozen - stasis), "дождь летит снизу вверх" (rain falling upward)
- **Color Theory**: "электрический синий" (electric blue dome), "фиолетовый" (violet compression)
- **Material Properties**: "подобно гелевой линзе" (like gel lens), "твердый синий пластик" (solid blue plastic)

### 3. Sound Design Mastery
- **Specific SFX**: "ВЖУХ" (digital TV off sound), "ГУЛ → ПИСК" (rumble to screech)
- **Layered Audio**: "Какофония" - cacophony of sounds
- **Silence as Weapon**: "абсолютная тишина океана" (absolute ocean silence)
- **Rhythmic Elements**: "ТУМ. ТУМ. ТУМ." (heartbeat rhythm)

### 4. Production-Ready Details
- **Character Actions**: Precise blocking ("срывает шлемы", "бьет кулаком по рации")
- **Set Design**: "LED-панели гаснут одна за другой" (LED panels dying sequentially)
- **Costume/Props**: "помятые латы" (dented armor), "острие копья до капота" (spear point to hood)
- **VFX Breakdown**: "пули высекают искры" (bullets spark off shields)

### 5. Narrative Architecture
- **Parallel Timelines**: Ancient, Modern, Future colliding
- **Symbolic Imagery**: Physics = math breaking down
- **Emotional Arc**: Tension → Confusion → Realization → Defeat
- **Thematic Depth**: "Цивилизация — это электричество. Без него мы снова звери."

## Current Agent Output (from our test)

### Scenario Agent (OpenAI GPT-4o):
```
"A wide shot captures the vastness of an ancient stone temple shrouded in darkness..."
```
**Issues**: Generic, no technical specs, no timing, no visual language

### Prompt Agent (Claude):
```
"8K cinematic shot, {camera} with {lens}, teal and orange grading..."
```
**Issues**: Template-based, lacks specificity, no emotional direction

### Sound Design Agent (Gemini fallback):
Returns empty due to quota issues

## The Gap

| Aspect | Professional Script | Our Agents | Gap |
|--------|-------------------|------------|-----|
| Shot specificity | Exact types, angles, movements | "wide shot", "close-up" | ❌ |
| Visual language | Glitch effects, physics breaking | "dramatic lighting" | ❌ |
| Sound design | Precise SFX, silence, rhythm | "ambient drone" | ❌ |
| Timing | Exact timestamps | Duration in seconds | ⚠️ |
| VFX specs | Detailed breakdown | Generic | ❌ |
| Color theory | Specific palettes with meaning | "teal and orange" | ❌ |

## What We Need to Fix

1. **Enhance prompts with professional cinematography vocabulary**
2. **Add visual effects specification language**
3. **Include precise sound design requirements**
4. **Add timing and rhythm considerations**
5. **Incorporate color theory and lighting specifics**
6. **Add production-ready shot breakdowns**

Let me now create a test using this script and analyze the gaps.
