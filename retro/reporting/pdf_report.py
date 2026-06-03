from __future__ import annotations

from retro.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_pdf_report(incident: dict, output_path: str) -> str:
    try:
        from weasyprint import HTML
        from retro.reporting.html_report import generate_html_report
        html = await generate_html_report(incident)
        HTML(string=html).write_pdf(output_path)
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    except ImportError:
        logger.warning("weasyprint not installed, falling back to text report")
        with open(output_path, "w") as f:
            f.write(f"RETRO Incident Report\n{'='*40}\n\n")
            for k, v in incident.items():
                f.write(f"{k}: {v}\n")
        return output_path
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return ""
