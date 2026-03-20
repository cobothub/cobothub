"""DeepCoBot 内置技能包

提供常用的内置技能：
- core: cron, weather
- office: pdf, xlsx, docx, pptx
- dev: github
- media: news
"""

from pathlib import Path

# Skills 目录路径
SKILLS_DIR = Path(__file__).parent

# 内置技能列表
BUILTIN_SKILLS = [
    "core/cron",
    "core/weather",
    "office/pdf",
    "office/xlsx",
    "office/docx",
    "office/pptx",
    "dev/github",
    "media/news",
]


def get_skill_paths() -> list[str]:
    """获取所有内置技能的路径"""
    return [str(SKILLS_DIR / skill) for skill in BUILTIN_SKILLS]


def list_builtin_skills() -> list[dict[str, str]]:
    """列出所有内置技能及其描述

    Returns:
        技能信息列表，每项包含 name, description, path
    """
    import re

    skills = []
    for skill_path in BUILTIN_SKILLS:
        skill_md = SKILLS_DIR / skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")

            # 解析 YAML frontmatter
            name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
            desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)

            name = name_match.group(1).strip().strip('"\'') if name_match else skill_path.split('/')[-1]
            description = desc_match.group(1).strip().strip('"\'') if desc_match else ""

            skills.append({
                "name": name,
                "description": description,
                "path": str(skill_md.parent),
            })

    return skills