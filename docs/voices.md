# Voice Control and Customization Guide

This guide explains how to use and customize voice settings in PDF2Audio for optimal speech synthesis results.

## Available Voices

PDF2Audio uses Piper TTS with high-quality neural voice models. Each voice is optimized for specific languages and use cases.

### English Voices

| Voice ID | Name | Gender | Quality | Best For |
|----------|------|--------|---------|----------|
| `en_US-lessac-medium` | Lessac (US English) | Male | Medium | Academic content, clear pronunciation |
| `en_US-libritts-high` | LibriTTS (US English) | Mixed | High | Natural reading, varied intonation |
| `en_GB-alan-medium` | Alan (British English) | Male | Medium | British pronunciation, formal content |

### International Voices

| Language | Voice ID | Name | Gender | Notes |
|----------|----------|------|--------|-------|
| Spanish | `es_ES-mls-medium` | MLS (Spanish) | Mixed | European Spanish |
| French | `fr_FR-mls-medium` | MLS (French) | Mixed | Metropolitan French |
| German | `de_DE-thorsten-medium` | Thorsten (German) | Male | Clear German pronunciation |
| Italian | `it_IT-riccardo-medium` | Riccardo (Italian) | Male | Standard Italian |

## Voice Settings

### Language Selection

Choose the primary language of your document:

```javascript
// API request
{
  "language": "en",  // English
  "voice": "en_US-lessac-medium"
}
```

**Supported Languages:**
- `en` - English
- `es` - Spanish  
- `fr` - French
- `de` - German
- `it` - Italian

### Voice Model Selection

Each language offers multiple voice models with different characteristics:

**For Academic Content:**
- Use `lessac` or `alan` voices for clear, formal pronunciation
- Avoid overly expressive voices for technical material

**For General Reading:**
- `libritts` models provide more natural intonation
- Mixed-gender models offer variety in longer documents

### Speech Speed Control

Adjust reading speed from 0.5x to 2.0x normal speed:

```javascript
{
  "speed": 1.0,  // Normal speed
  "speed": 0.8,  // Slower for complex content
  "speed": 1.3   // Faster for familiar material
}
```

**Recommended Speeds:**
- **0.5x - 0.7x**: Complex mathematical content, foreign language learners
- **0.8x - 0.9x**: Dense academic papers, detailed technical content
- **1.0x**: Standard reading speed (default)
- **1.1x - 1.3x**: Review material, familiar content
- **1.4x - 2.0x**: Quick overview, time-constrained listening

## Mathematical Expression Handling

PDF2Audio uses MathJax Speech Rule Engine to convert mathematical notation into spoken form.

### Supported Mathematical Elements

| Notation | Spoken As | Example |
|----------|-----------|---------|
| x² | "x squared" | Power notation |
| √x | "square root of x" | Radical expressions |
| ∫ | "integral" | Integration |
| ∑ | "sum" | Summation |
| α, β, γ | "alpha", "beta", "gamma" | Greek letters |
| ∞ | "infinity" | Special symbols |

### Mathematical Speech Rules

The system follows academic speech conventions:

**Fractions:**
- `1/2` → "one half"
- `x/y` → "x over y"
- `(a+b)/(c+d)` → "open parenthesis a plus b close parenthesis over open parenthesis c plus d close parenthesis"

**Equations:**
- `E = mc²` → "E equals m c squared"
- `f(x) = x + 1` → "f of x equals x plus 1"

**Complex Expressions:**
- Automatic pausing around mathematical expressions
- Clear pronunciation of variables and operators
- Proper grouping of parentheses and brackets

## Customization Options

### Frontend Voice Settings

Access voice settings through the web interface:

1. Click the "Settings" button in the header
2. Select your preferred language
3. Choose a voice model
4. Adjust speech speed with the slider
5. Preview settings before uploading

### API Configuration

Configure voices programmatically:

```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "language=en" \
  -F "voice=en_US-lessac-medium" \
  -F "speed=1.2" \
  http://localhost:5000/upload
```

### Advanced Configuration

For custom voice models or additional languages:

1. **Download Voice Models:**
   ```bash
   # Download from Piper voices repository
   wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/[language]/[voice].onnx
   wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/[language]/[voice].onnx.json
   ```

2. **Add to Piper Service:**
   ```bash
   # Copy models to container
   docker cp voice.onnx pdf2audio_piper_1:/app/models/
   docker cp voice.onnx.json pdf2audio_piper_1:/app/models/
   ```

3. **Update Configuration:**
   ```python
   # In docker-services/piper-service/app.py
   AVAILABLE_VOICES['new_language'] = [{
       'id': 'new_voice_id',
       'model': 'voice.onnx',
       'config': 'voice.onnx.json',
       'language': 'new_language',
       'gender': 'male/female',
       'quality': 'medium/high'
   }]
   ```

## Best Practices

### Document Preparation

**For Optimal Results:**
- Use text-based PDFs rather than scanned images
- Ensure mathematical notation is properly formatted
- Avoid complex layouts with multiple columns
- Check that fonts are embedded in the PDF

**Mathematical Content:**
- Use standard LaTeX notation when possible
- Avoid handwritten equations in scanned documents
- Ensure mathematical symbols are clearly rendered

### Voice Selection Guidelines

**Academic Papers:**
- Choose clear, formal voices (Lessac, Alan)
- Use moderate speed (0.9x - 1.1x) for comprehension
- Consider British English for international audiences

**Technical Documentation:**
- Prioritize clarity over naturalness
- Use consistent voice throughout long documents
- Slower speeds for complex terminology

**Review and Study:**
- Faster speeds (1.2x - 1.5x) for familiar material
- Natural voices (LibriTTS) for extended listening
- Adjust speed based on content complexity

### Accessibility Considerations

**For Visually Impaired Users:**
- Provide clear audio descriptions of figures and tables
- Use consistent voice settings across related documents
- Include chapter/section announcements

**For Learning Disabilities:**
- Slower speech rates for processing time
- Clear pronunciation of technical terms
- Consistent pacing throughout document

**For Language Learners:**
- Native speaker voices for pronunciation models
- Slower speeds for comprehension
- Clear articulation of mathematical terms

## Troubleshooting Voice Issues

### Common Problems

**Robotic or Unnatural Speech:**
- Try different voice models
- Adjust speech speed
- Check for text extraction errors

**Mathematical Expressions Not Spoken:**
- Verify MathML extraction in processing logs
- Check PDF mathematical notation format
- Consider OCR fallback for scanned documents

**Incorrect Pronunciation:**
- Switch to different language/voice combination
- Report pronunciation issues for improvement
- Use phonetic spelling in source documents

**Audio Quality Issues:**
- Ensure sufficient system resources
- Check Piper TTS service logs
- Verify voice model files are complete

### Performance Optimization

**For Large Documents:**
- Process in smaller chunks
- Use medium-quality voices for faster generation
- Monitor system memory usage

**For Real-time Applications:**
- Pre-load frequently used voice models
- Cache common mathematical expressions
- Use streaming audio delivery

## Voice Model Development

### Contributing New Voices

To add support for additional languages or voices:

1. **Training Data Requirements:**
   - High-quality audio recordings
   - Phonetically balanced text corpus
   - Native speaker pronunciation

2. **Model Training:**
   - Use Piper training pipeline
   - Follow voice quality guidelines
   - Test with academic content

3. **Integration:**
   - Add model files to service
   - Update voice configuration
   - Test with mathematical content

### Quality Standards

All voice models should meet:
- Clear pronunciation of technical terms
- Proper mathematical expression handling
- Consistent audio quality
- Appropriate speaking pace
- Natural intonation patterns

## Future Enhancements

**Planned Features:**
- Voice cloning for personalized speech
- Emotion and emphasis control
- Multi-speaker support for dialogues
- Real-time voice switching
- Custom pronunciation dictionaries

**Community Contributions:**
- Additional language support
- Specialized academic voices
- Mathematical notation improvements
- Accessibility enhancements

For the latest voice models and updates, check the [Piper Voices repository](https://huggingface.co/rhasspy/piper-voices) and our project documentation.