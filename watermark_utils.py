# watermark_utils.py
import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional

class WatermarkProcessor:
    def __init__(self):
        self.font_path = "arial.ttf"  # Default font
    
    def apply_video_watermark(self, input_path: str, output_path: str, watermark_text: str,
                            position: str = "bottom-right", opacity: float = 0.7,
                            font_size: int = 24, color: str = "white") -> bool:
        """
        Apply watermark to video using ffmpeg
        Returns True if successful, False otherwise
        """
        try:
            # Create temporary watermark image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                watermark_img_path = temp_file.name
                self._create_watermark_image(watermark_text, watermark_img_path, font_size, opacity, color)

                # FFmpeg filter for position
                overlay_filter = self._get_position_filter(position)

                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-i', watermark_img_path,
                    '-filter_complex', overlay_filter,
                    '-codec:a', 'copy',
                    output_path
                ]

                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                return result.returncode == 0

        except Exception as e:
            print(f"Error applying video watermark: {e}")
            return False
        finally:
            if os.path.exists(watermark_img_path):
                os.remove(watermark_img_path)

    def apply_pdf_watermark(self, input_path: str, output_path: str, watermark_text: str,
                          opacity: float = 0.3, angle: int = 45, font_size: int = 48) -> bool:
        """
        Apply watermark to PDF using reportlab (requires ghostscript)
        Returns True if successful, False otherwise
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from PyPDF2 import PdfFileWriter, PdfFileReader
            
            # Create temporary watermark PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                watermark_pdf_path = temp_file.name
                c = canvas.Canvas(watermark_pdf_path, pagesize=letter)
                c.setFont("Helvetica", font_size)
                c.setFillAlpha(opacity)
                c.rotate(angle)
                
                # Draw watermark diagonally across page
                for i in range(-5, 10):
                    c.drawString(100, 100 + (i * 200), watermark_text)
                c.save()

                # Merge watermark with original PDF
                output = PdfFileWriter()
                input_pdf = PdfFileReader(input_path)
                watermark_pdf = PdfFileReader(watermark_pdf_path)

                for page_num in range(input_pdf.getNumPages()):
                    page = input_pdf.getPage(page_num)
                    page.mergePage(watermark_pdf.getPage(0))
                    output.addPage(page)

                with open(output_path, "wb") as output_stream:
                    output.write(output_stream)

            return True
        except Exception as e:
            print(f"Error applying PDF watermark: {e}")
            return False
        finally:
            if os.path.exists(watermark_pdf_path):
                os.remove(watermark_pdf_path)

    def _create_watermark_image(self, text: str, output_path: str,
                              font_size: int, opacity: float, color: str) -> None:
        """Create transparent PNG watermark image"""
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Calculate text size
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_width, text_height = draw.textsize(text, font=font)

        # Create watermark image with transparency
        watermark = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        draw.text((10, 10), text, font=font, fill=f"{color}@{int(opacity*255)}")
        watermark.save(output_path)

    def _get_position_filter(self, position: str) -> str:
        """Generate ffmpeg overlay position filter"""
        positions = {
            "top-left": "10:10",
            "top-right": "main_w-overlay_w-10:10",
            "bottom-left": "10:main_h-overlay_h-10",
            "bottom-right": "main_w-overlay_w-10:main_h-overlay_h-10",
            "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2"
        }
        return f'[1][0]scale2ref=w=oh1*mdar:h=ih1*0.1[wm][vid];[vid][wm]overlay={positions.get(position, positions["bottom-right"])}'
