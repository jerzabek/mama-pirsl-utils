import argparse
from PIL import Image
import os


def parse_args() -> argparse.Namespace:
    """Utility function that parses stdin arguments"""

    parser = argparse.ArgumentParser()

    # Mutually exclusive input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-r",
        "--recursive",
        help="The path to the folder that will be recursively ",
        type=str,
    )
    input_group.add_argument(
        "-i",
        "--image",
        help="The path to a single image that should be processed",
        type=str,
    )

    # Rest of the arguments
    parser.add_argument(
        "-w",
        "--watermark",
        help="The path to the watermark image to be added",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="The path where the script will output the processed photos coming from a recursive execution.",
    )

    return parser.parse_args()


def is_image_file(filename):
    """A utility function that checks if a file is an image file"""

    # Check if the file is an image based on its extension
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    _, ext = os.path.splitext(filename)
    return ext.lower() in image_extensions


def process_image(
    root_path: str | None, watermark_path: str, output_path: str | None, image_path: str
) -> None:
    """
    Utility function that performs processing on an image\n
    Processing includes:\n
        * Converting image to 16:9 ratio
        * Possibly adding transparent padding
        * Adding a watermark at the center of the image
    Function returns the path to the processed image on local disk.\n
    """

    if not image_path:
        raise ValueError()

    print(f"Processing image: {image_path}")

    # Open the image file
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    # Calculate the target dimensions for a 16:9 ratio
    target_width = width
    target_height = int(width / 16 * 9)
    if target_height < height:
        target_height = height
        target_width = int(height / 9 * 16)

    # Create a new image with a transparent background
    new_image = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))

    # Calculate padding to center the original image in the new image
    padding_left = (target_width - width) // 2
    padding_top = (target_height - height) // 2

    # Paste the original image into the new image
    new_image.paste(image, (padding_left, padding_top))

    # Load the watermark image
    watermark = Image.open(watermark_path).convert("RGBA")

    # Resize the watermark to be 0.2 times the height of the new image
    watermark_width, watermark_height = watermark.size
    new_watermark_height = int(target_height * 0.2)
    new_watermark_width = int(
        watermark_width * (new_watermark_height / watermark_height)
    )
    watermark = watermark.resize(
        (new_watermark_width, new_watermark_height), Image.Resampling.LANCZOS
    )

    # Calculate the position to center the watermark
    position = (
        (target_width - new_watermark_width) // 2,
        (target_height - new_watermark_height) // 2,
    )

    # Paste the watermark into the new image
    new_image.paste(watermark, position, watermark)

    # Save the processed image
    new_image_path = ""
    image_base_path = os.path.basename(image_path)
    image_parent_path = os.path.dirname(image_path)
    new_image_base_path = f"processed_{image_base_path}"

    if root_path is None:

        new_image_path = os.path.join(image_parent_path, new_image_base_path)
    else:
        output_path = os.path.abspath(
            "processed_images" if output_path is None else output_path
        )

        relative_path_to_image_parent = os.path.dirname(
            os.path.relpath(image_path, root_path)
        )
        output_path = os.path.join(output_path, relative_path_to_image_parent)

        os.makedirs(output_path, exist_ok=True)

        new_image_path = os.path.join(output_path, new_image_base_path)

    # Change the file extension to .png
    base, _ = os.path.splitext(new_image_path)
    new_image_path = f"{base}.png"

    new_image.save(new_image_path, format="PNG")

    image.close()

    return new_image_path


def find_and_process_images(
    root_path: str, watermark_path: str, output_path: str | None, path: str
):
    """A recursive utility function that looks in a given directory for image files and processes them"""

    if os.path.isfile(path):
        if not is_image_file(path):
            return

        process_image(
            root_path=root_path,
            image_path=path,
            output_path=output_path,
            watermark_path=watermark_path,
        )

    elif os.path.isdir(path):
        sub_paths: list[str] = list(
            map(lambda entry: os.path.join(path, entry), os.listdir(path))
        )

        for sub_path in sub_paths:
            find_and_process_images(
                root_path=root_path,
                watermark_path=watermark_path,
                output_path=output_path,
                path=sub_path,
            )
    else:
        raise Exception(f"Unknown type for item at path: {path}")


def main() -> None:
    # Parse the arguments
    args = parse_args()

    watermark_path: str = os.path.abspath(args.watermark)
    output_path: str | None = (
        os.path.abspath(args.output) if args.output is not None else None
    )

    # Process image(s)
    if args.recursive:
        root_path = os.path.abspath(args.recursive)
        find_and_process_images(
            root_path=root_path,
            watermark_path=watermark_path,
            output_path=output_path,
            path=root_path,
        )

    elif args.image:
        image_path = os.path.abspath(args.image)
        process_image(
            root_path=None,
            watermark_path=watermark_path,
            output_path=output_path,
            image_path=image_path,
        )


if __name__ == "__main__":
    main()
