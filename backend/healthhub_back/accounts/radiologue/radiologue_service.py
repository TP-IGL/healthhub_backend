from decouple import config
import logging


import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


# Configuration       
cloudinary.config( 
    cloud_name = config('CLOUDINARY_CLOUD_NAME'), 
    api_key = config('CLOUDINARY_API_KEY'), 
    api_secret = config("CLOUDINARY_API_SECRET"), 
    secure=True
)

def upload_image(image):
    """
    Uploads an image to Cloudinary.
    """
    upload = cloudinary.uploader.upload(
        image,
        asset_folder="TP-IGL/Resultat-Radiologie",
        resource_type="image")
    return upload['secure_url']

    
async def delete_image_from_cloudinary(self, image_url: str) -> None:
    """
        Delete an image from Cloudinary by public ID and resource type.
    """
    public_id = extract_public_id(self, image_url)
    try:
        result = cloudinary.api.delete_resources(
            [f"TP-IGL/Resultat-Radiologie/{public_id}"],
            resource_type="image",
            type="upload"
        )
        self.logger.info(f"Deleted Resultat-Radiologie with public_id {public_id}: {result}")
    except Exception as error:
        self.logger.error(f"Error deleting Resultat-Radiologie with public_id {public_id}: {str(error)}")   



def extract_public_id(self, image_url: str):
        """
        Extract the public ID from a Cloudinary image URL.
        """
        try:
            parts = image_url.split('/')
            last_part = parts[-1] if parts else None
            if not last_part:
                raise ValueError("Invalid URL format")
            public_id = last_part.split('.')[0]
            return public_id
        except Exception as error:
            self.logger.error(f"Error extracting public_id: {str(error)}")
            return None



