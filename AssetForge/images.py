import random
from PIL import Image, ImageEnhance
import os

# slight depth change
DEFAULT_PERSPECTIVE_MATRIX = (
        1, 0, 0,
        0, 1, 0,
        0.00005, 0.00005)

SKEW_PERSPECTIVE_MATRIX = ( 
        1,0.5,0,
        0,1,0,
        0,0
)

def load_image(pic):
    """Helper to load an image if input is a file path,
    else return the Image object."""
    if isinstance(pic, str):
        return Image.open(pic)
    elif isinstance(pic, Image.Image):
        return pic
    else:
        raise ValueError("Input must be a file path (str) or an Image.Image object.")

def image_resolution(current_picture) -> tuple[int,int]:
    image = load_image(current_picture)
    image_res = image.size
    image.close()
    return image_res

def resize_image(current_picture, x : int, y : int) -> Image.Image:
    """Changes the resolution of an image
    to (x,y)->(width,height)"""
    size = (x,y)
    
    with load_image(current_picture) as image:
        return image.resize(size)

def cut_image(current_picture, coords) -> Image.Image:
    """Cuts an image in the rectangle defined by coords"""
    if (len(coords) == 2):
        (t1,t2) = coords
        coords = (0,0,t1,t2)
        
    elif (len(coords) != 4):
        raise Exception("non-valid coordinates")
    
    (x1,x2,y1,y2) = coords
    
    with load_image(current_picture) as image:
        return image.crop((x1,x2,y1,y2))

def tile_image(current_picture, x : int, y : int) -> Image.Image:
    """Tiles by itself x times in the row direction
    and y times in the column direction"""
    if (x <= 0 or y <= 0):
        raise Exception("x and y need to be bigger than zero")
    
    image = load_image(current_picture)
    tile_width, tile_height = image.size
    new_width, new_height = tile_width * y, tile_height * x
    
    tiled_image = Image.new("RGB", (new_width, new_height))
    
    for i in range(x):
        for j in range(y):
            tiled_image.paste(image, (j * tile_width, i * tile_height))
    
    image.close()
    return tiled_image

def apply_function(current_picture, func) -> Image.Image:
    """Apply a function that takes 
    (r,g,b) -> (r,g,b) and applies it to all pixels"""
    im = load_image(current_picture)
    pixelMap = im.load()

    with Image.new(im.mode, im.size) as img:
        pixelsNew = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                pixelsNew[i,j] = func(pixelMap[i,j])

        im.close()
        return img
    
def goldify(current_picture, rgb) -> tuple[int,int,int]:
    """Makes images look golden"""
    if isinstance(rgb,tuple):
        (r,g,b) = rgb
        return (int(r/3)+g,g+1,abs(128-(r)))
    else:
        return (r,g,b)

def change_brightness(current_picture, percentage : float) -> Image.Image:
    """Increases the brightness of every pixel by percentage
    and clamps pixels that pass 255 at 255"""
    def func(rgb):
        if isinstance(rgb, tuple):  # For RGB images
            return (
                min(255, int(rgb[0] * percentage)),
                min(255, int(rgb[1] * percentage)),
                min(255, int(rgb[2] * percentage)),
            )
        else:  # For grayscale images (mode 'L')
            return min(255, int(rgb * percentage))
    
    image = apply_function(current_picture,func)
    return image

def transpose_by(current_picture, theta : float) -> Image.Image:
    """Transposes an image by theta degrees
    in the anti-clockwise direction"""
    theta %= 360
    with load_image(current_picture) as im:
        return im.rotate(theta)

def flip_by_x(current_picture) -> Image.Image:
    """Flip an image by the x axis"""
    with load_image(current_picture) as im:
        return im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

def flip_by_y(current_picture) -> Image.Image:
    """Flip an image by the y axis"""
    with load_image(current_picture) as im:
        return im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    
def flip_by_diagonal(current_picture) -> Image.Image:
    """Flip an image by the descending diagonal"""
    with load_image(current_picture) as im:
        im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return im

def flip_by_anti_diagonal(current_picture) -> Image.Image:
    """Flip an image by the ascending diagonal"""
    with load_image(current_picture) as im:
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return im

def perspective_warp_image(current_picture,
                           coords = DEFAULT_PERSPECTIVE_MATRIX) -> Image.Image:
    """Applies a perspective warp based on the given coordinates."""
    if coords is None or len(coords) != 8:
        coords = SKEW_PERSPECTIVE_MATRIX
    with load_image(current_picture) as im:
        return im.transform(im.size, 2, coords, Image.Resampling.BICUBIC)
    
def noise_default(x,percent) -> tuple[int,int,int]:
    "The default noise function"
    return max(0, min(255, int(x + percent * 255 * (random.random() - 0.5))))
    
def apply_noise(current_picture,
                percent : float = 0.2,
                noise = noise_default) -> Image.Image:
    """apply a noise function at certain percentage"""
    with load_image(current_picture) as image:
        noisy_image = image.copy()
        pixels = noisy_image.load()
        
        for i in range(noisy_image.size[0]):
            for j in range(noisy_image.size[1]):
                r, g, b = pixels[i, j]
                pixels[i, j] = (noise(r,percent), noise(g,percent), noise(b,percent))
                
        return noisy_image
        
def overlay_image(current_picture,
                  overlay_path: str,
                  position: tuple, alpha: float = 0.5) -> Image.Image:
    """Overlays an image with transparency at a specified position."""
    with load_image(current_picture) as image:
        overlay = Image.open(overlay_path).convert("RGBA")
        overlay = overlay.resize(image.size)
        overlay.putalpha(int(255 * alpha))
        
        image.paste(overlay, position, overlay)
        overlay.close()
        return image

def adjust_contrast(current_picture, factor: float) -> Image.Image:
    """Adjusts the contrast of the image by a given factor."""
    with load_image(current_picture) as image:
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

def convert_to_grayscale(current_picture) -> Image.Image:
    """Converts the image to grayscale."""
    with load_image(current_picture) as image:
        return image.convert("L")

def rescale_image(current_picture, scale: float) -> Image.Image:
    """Rescales the image by a given scale percentage."""
    with load_image(current_picture) as image:
        new_size = (int(image.width * scale), int(image.height * scale))
        return image.resize(new_size)

def save_image(image: Image.Image, format: str, path: str) -> Image.Image:
    """Saves the image in the specified format, And returns the saved image"""
        
    if format == "JPG":
        format = "JPEG"

    if not path.lower().endswith(f".{format.lower()}"):
        path += f".{format.lower()}"
    print(f"saving in: {path}")
    image = image.convert('RGB')
    try:
        image.save(path, format=format)
        print(f"Image saved successfully in {path}.")
    except Exception as e:
        print(f"Error saving image: {e}")
        
    return image