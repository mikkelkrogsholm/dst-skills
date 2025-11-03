#!/usr/bin/env python3
"""Generate HTML reports from templates."""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def load_template() -> str:
    """Load HTML template from dst-report skill."""
    skill_path = Path(__file__).parent.parent.parent / ".claude" / "skills" / "dst-report" / "SKILL.md"
    content = skill_path.read_text()

    # Extract HTML template between ```html and ```
    start = content.find("```html\n<!DOCTYPE html>")
    end = content.find("```\n</html>") + len("```\n</html>")

    if start == -1:
        raise ValueError("Could not find HTML template in dst-report skill")

    template = content[start+8:end-4]  # Remove ```html and ```
    return template


def fill_template(template: str, data: dict) -> str:
    """Fill template placeholders."""
    result = template
    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result


def create_report_folder(topic: str) -> Path:
    """Create organized folder structure."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean topic for filesystem
    topic_clean = topic.lower().replace(" ", "_").replace("/", "_")
    folder = Path("reports") / f"{topic_clean}_{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def generate_report(
    topic: str,
    title: str,
    executive_summary: str,
    sections: List[str],
    data_sources: List[str],
    charts: Optional[List[str]] = None
) -> Path:
    """
    Generate comprehensive HTML report.

    Args:
        topic: Short topic slug (e.g., "electric_vehicles")
        title: Full report title
        executive_summary: Executive summary HTML
        sections: List of section HTML blocks
        data_sources: List of DST tables used
        charts: Optional list of chart script blocks

    Returns:
        Path to generated report.html
    """
    template = load_template()
    folder = create_report_folder(topic)

    data = {
        "REPORT_TITLE": title,
        "TIMESTAMP": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "TABLE_COUNT": len(data_sources),
        "EXECUTIVE_SUMMARY": executive_summary,
        "CONTENT_SECTIONS": "\n\n".join(sections),
        "DATA_SOURCES": "\n".join(f"<li>{s}</li>" for s in data_sources),
        "CHART_SCRIPTS": "\n".join(charts or [])
    }

    html = fill_template(template, data)
    output_file = folder / "report.html"
    output_file.write_text(html, encoding="utf-8")

    return output_file.absolute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate DST HTML report")
    parser.add_argument("--topic", required=True, help="Topic slug")
    parser.add_argument("--title", required=True, help="Report title")
    parser.add_argument("--data", required=True, help="JSON file with report data")

    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    report_path = generate_report(
        topic=args.topic,
        title=args.title,
        executive_summary=data.get("summary", ""),
        sections=data.get("sections", []),
        data_sources=data.get("sources", []),
        charts=data.get("charts", [])
    )

    print(f"Report generated: {report_path}")
