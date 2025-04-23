import pytest
import numpy as np
import cv2
from PIL import Image
from app.ml.preprocessors.image_preprocessor import ImagePreprocessor

@pytest.fixture
def preprocessor():
    return ImagePreprocessor()

@pytest.fixture
def sample_image():
    # Create a sample KTP-like image for testing
    width, height = 800, 500
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add a rectangle to simulate KTP card
    cv2.rectangle(img, (50, 50), (750, 450), (0, 0, 0), 2)
    
    # Convert to PIL Image
    return Image.fromarray(img)

@pytest.fixture
def skewed_image():
    # Create a skewed image for testing perspective correction
    width, height = 800, 500
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Create a skewed rectangle
    pts = np.array([
        [100, 50],    # Top-left
        [700, 100],   # Top-right
        [650, 400],   # Bottom-right
        [150, 450]    # Bottom-left
    ], dtype=np.int32)
    
    cv2.polylines(img, [pts], True, (0, 0, 0), 2)
    
    return Image.fromarray(img)

@pytest.fixture
def noisy_image():
    # Create a noisy image for testing denoising
    width, height = 800, 500
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add Gaussian noise
    noise = np.random.normal(0, 25, (height, width, 3))
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img)

@pytest.fixture
def dark_image():
    # Create a dark image for testing contrast enhancement
    width, height = 800, 500
    img = np.ones((height, width, 3), dtype=np.uint8) * 100  # Dark gray
    
    return Image.fromarray(img)

def test_init(preprocessor):
    assert preprocessor.target_size == (800, 500)
    assert preprocessor.min_area == 5000

def test_resize_image(preprocessor, sample_image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(sample_image), cv2.COLOR_RGB2BGR)
    
    # Test resizing
    resized = preprocessor._resize_image(img)
    height, width = resized.shape[:2]
    
    # Check if dimensions are within target size
    assert width <= preprocessor.target_size[0]
    assert height <= preprocessor.target_size[1]
    
    # Check aspect ratio is maintained
    original_ratio = sample_image.width / sample_image.height
    new_ratio = width / height
    assert abs(original_ratio - new_ratio) < 0.1

def test_denoise(preprocessor, noisy_image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(noisy_image), cv2.COLOR_RGB2BGR)
    
    # Test denoising
    denoised = preprocessor._denoise(img)
    
    # Calculate noise reduction
    original_std = np.std(img)
    denoised_std = np.std(denoised)
    
    # Verify noise reduction
    assert denoised_std < original_std

def test_correct_perspective(preprocessor, skewed_image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(skewed_image), cv2.COLOR_RGB2BGR)
    
    # Test perspective correction
    corrected = preprocessor._correct_perspective(img)
    
    # Verify dimensions
    assert corrected.shape[1] == preprocessor.target_size[0]
    assert corrected.shape[0] == preprocessor.target_size[1]

def test_enhance_contrast(preprocessor, dark_image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(dark_image), cv2.COLOR_RGB2BGR)
    
    # Add some variation to ensure non-uniform image
    height, width = img.shape[:2]
    cv2.rectangle(img, (width//4, height//4), (3*width//4, 3*height//4), (150, 150, 150), -1)
    
    # Test contrast enhancement
    enhanced = preprocessor._enhance_contrast(img)
    
    # Calculate contrast using standard deviation of image intensities
    original_std = np.std(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    enhanced_std = np.std(cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY))
    
    # Verify contrast improvement
    assert enhanced_std > original_std

def test_full_preprocessing_pipeline(preprocessor, sample_image):
    # Test complete preprocessing pipeline
    preprocessed = preprocessor.preprocess(sample_image)
    
    # Check output type
    assert isinstance(preprocessed, Image.Image)
    
    # Check dimensions
    assert preprocessed.width <= preprocessor.target_size[0]
    assert preprocessed.height <= preprocessor.target_size[1]

def test_preprocessing_with_invalid_input(preprocessor):
    with pytest.raises(Exception):
        preprocessor.preprocess(None)
    
    with pytest.raises(Exception):
        preprocessor.preprocess("not an image")

def test_preprocessing_empty_image(preprocessor):
    # Create an empty (all white) image
    empty_img = Image.new('RGB', (800, 500), color='white')
    
    # Should process without errors
    result = preprocessor.preprocess(empty_img)
    
    # Check output is valid
    assert isinstance(result, Image.Image)
    assert result.width <= preprocessor.target_size[0]
    assert result.height <= preprocessor.target_size[1]