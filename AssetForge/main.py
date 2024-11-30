from AssetForge.images import *
import typer
from typing_extensions import Annotated
from typing import Optional
import os, sys

app = typer.Typer()
last_pic = Image.new("RGB", (1,1))

@app.command()
def find_res(current_picture: str):
    """Finds the resolution of an image"""
    typer.echo(f"image resolution is: {image_resolution(current_picture)}")
    
@app.command()
def resize(current_picture: str, width: int, height: int):
    """Resize the image to the specified width and height."""
    typer.echo(f"Resizing file: {current_picture} to {width}x{height}")
    image = resize_image(current_picture, width, height)
    image.show()
    return image
    
@app.command()
def rescale(current_picture: str, factor : float):
    """Rescales an image by a factor"""
    image = rescale_image(current_picture, factor)
    image.show()
    return image
    
@app.command()
def brightness(current_picture: str, percentage: float):
    """Adjust the brightness by a multiplier"""
    image = change_brightness(current_picture, percentage)
    image.show()
    return image

@app.command()
def contrast(current_picture: str, factor: float):
    """Adjust the contrast by a factor"""
    image = adjust_contrast(current_picture, factor)
    image.show()
    return image

@app.command()
def flip_x(current_picture: str):
    """Flip the image horizontally."""
    image = flip_by_x(current_picture)
    image.show()
    return image

@app.command()
def flip_y(current_picture: str):
    """Flip the image vertically"""
    image = flip_by_y(current_picture)
    image.show()
    return image
    
@app.command()
def flip_dig(current_picture: str):
    """Flip the image by the decending diagonal"""
    image = flip_by_diagonal(current_picture)
    image.show()
    return image

@app.command()
def flip_antidig(current_picture: str):
    """Flip the image by the ascending diagonal"""
    image = flip_by_anti_diagonal(current_picture)
    image.show()
    return image

@app.command()
def grayscale(current_picture: str = None):
    """Convert the image to grayscale."""
    image = convert_to_grayscale(current_picture)
    image.show()
    return image

@app.command("apply-noise")
def apply_noise_to_image(current_picture: str, intensity: float):
    "Apply random noise to image"
    image = apply_noise(current_picture,intensity)
    image.show()
    return image

@app.command()
def rotate(current_picture: str, degrees: float):
    """Rotate an image by the anti-clockwise direction"""
    image = transpose_by(current_picture, degrees)
    image.show()
    return image

@app.command()
def warp_pers(current_picture: str,
              perspective_matrix: Annotated[Optional[list[int]],typer.Argument()] = None):
    """warp the perspective of the image with a 8 tuple"""
    if perspective_matrix != None and len(perspective_matrix) != 8:
        message = "Invalid Input, perspective matrix should be 8 floats long\nDefaulting to built-in perspective matrix"
        message = typer.style(message, fg=typer.colors.RED, bold=True)
        typer.echo(message)
    image = perspective_warp_image(current_picture,perspective_matrix)
    image.show()
    return image

@app.command()
def overlay_img(current_picture: str,
                other_picture: str,
                alpha: float,
                offset: Annotated[Optional[tuple[int,int]],typer.Argument()] = (0,0)):
    """overlay an image on top of the other, the other image will be overlaid by alpha"""
    image = overlay_image(current_picture,other_picture,offset, alpha)
    image.show()
    return image

@app.command()
def save_img(current_picture: str, 
             path: Annotated[Optional[str],typer.Argument()] = os.getcwd(),
             format: Annotated[Optional[str],typer.Argument()] = "PNG"):
    """Save image current picture at path (default is current working directory) and default format is png"""
    with load_image(current_picture) as im:
        image = save_image(im,format,path)
        return image
    
@app.command()
def pipeline(input_path: str, output_path: str, operations: str):
    """Pipeline commands and save the resulting image
    syntax:
    asfr pipeline [command1]=[arg1]:[arg2]:[arg...],[command2]:[arg ...], ...
    """
    image = Image.open(input_path)
    op_names = {
        "contrast": contrast,
        "flip-x": flip_x,
        "flip-y": flip_y,
        "flip-dig": flip_dig,
        "flip-antidig": flip_antidig,
        "grayscale": grayscale,
        "rotate": rotate,
        "warp-pers": warp_pers,
        "overlay-img": overlay_img,
        "resize": resize,
        "rescale": rescale,
        "brightness": brightness,
    }

    operations = [op.strip() for op in operations.split(",") if op.strip()]

    for operation in operations:
        if "=" in operation:
            op_name, params = operation.split("=", 1)
            op_name = op_name.strip()
            params = params.strip()

            if op_name in op_names:
                func = op_names[op_name]
                args = []
                kwargs = {}

                if op_name == "resize":
                    width, height = map(int, params.split(":"))
                    args = [image, width, height]
                elif op_name in {"contrast", "brightness", "rescale", "rotate"}:
                    args = [image, float(params)]
                elif op_name == "overlay-img":
                    args = params.split(":")
                    if len(args) < 2:
                        raise ValueError(f"Invalid parameters for overlay-img: {params}")
                    other_picture = args[0]
                    alpha = float(args[1])
                    offset = eval(args[2]) if len(args) > 2 else (0, 0)  # Parse offset or default to (0, 0)
                    kwargs = {"current_picture":image, "other_picture": other_picture, "alpha": alpha, "offset": offset}
                else:
                    args = [image]
            else:
                raise ValueError(f"Unknown operation: {op_name}")
        else:
            op_name = operation.strip()
            if op_name in op_names:
                func = op_names[op_name]
                args = [image]
            else:
                raise ValueError(f"Unknown operation: {op_name}")

        if len(kwargs) > 0:
            image = func(**kwargs)
        else:
            image = func(*args, **kwargs)

    save_image(image, path=output_path, format="PNG")
    image.show()
    
if __name__ == "__main__":
    app()
