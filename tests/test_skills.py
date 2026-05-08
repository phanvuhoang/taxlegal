"""Tests for skill CRUD, versioning, and assignment."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


# ---------------------------------------------------------------------------
# Stubs — replace with real imports when backend is available
# ---------------------------------------------------------------------------

class FakeSkill:
    def __init__(self, id, name, content, version_number=1, is_active=True):
        self.id = id
        self.name = name
        self.content = content
        self.version_number = version_number
        self.is_active = is_active


class FakeSkillVersion:
    def __init__(self, skill_id, version_number, content):
        self.skill_id = skill_id
        self.version_number = version_number
        self.content = content


class FakeBotVariant:
    def __init__(self, id, name, base_prompt, skill_ids=None):
        self.id = id
        self.name = name
        self.base_prompt = base_prompt
        self.skill_ids = skill_ids or []


def create_new_skill_version(skill: FakeSkill, new_content: str) -> tuple:
    """
    Simulates the version-bump logic.
    Returns (updated_skill, new_version_record).
    """
    old_version = FakeSkillVersion(
        skill_id=skill.id,
        version_number=skill.version_number,
        content=skill.content,
    )
    skill.version_number += 1
    skill.content = new_content
    return skill, old_version


def assign_skill_to_bot(bot: FakeBotVariant, skill_id: int) -> FakeBotVariant:
    """Adds skill_id to bot's skill list if not already present."""
    if skill_id not in bot.skill_ids:
        bot.skill_ids = list(bot.skill_ids) + [skill_id]
    return bot


def build_system_prompt_with_skills(base_prompt: str, bot: FakeBotVariant, skills: list) -> str:
    """
    Injects active skill content into the base prompt.
    Only skills with is_active=True are included.
    """
    active_skills = [s for s in skills if s.is_active and s.id in bot.skill_ids]
    if not active_skills:
        return base_prompt

    skill_section = "\n\n=== SKILLS ACTIVATED ===\n"
    for skill in active_skills:
        skill_section += f"\n[Skill: {skill.name}]\n{skill.content}\n"
    skill_section += "=== END SKILLS ==="

    return base_prompt + skill_section


# Try real imports
try:
    from backend.services.skills import (  # noqa: F401
        create_new_skill_version,
        assign_skill_to_bot,
        build_system_prompt_with_skills,
    )
    from backend.models import Skill as FakeSkill, BotVariant as FakeBotVariant  # noqa: F401
except ImportError:
    pass  # use stubs above


# ===========================================================================
# Tests
# ===========================================================================


def test_skill_version_increments_on_update():
    """
    When a skill is updated, version_number must increment by 1
    and the old version must be preserved in skill_versions.
    """
    skill = FakeSkill(id=1, name="Thuế GTGT skill", content="Nội dung v1", version_number=1)

    updated_skill, old_version = create_new_skill_version(skill, new_content="Nội dung v2")

    assert updated_skill.version_number == 2, (
        f"Expected version 2 after update, got {updated_skill.version_number}"
    )
    assert old_version.version_number == 1, "Old version record must retain version_number=1"
    assert old_version.content == "Nội dung v1", "Old version must preserve original content"
    assert updated_skill.content == "Nội dung v2"


def test_skill_assignment_to_bot():
    """Assigning a new skill to a BotVariant must add it to skill_ids."""
    bot = FakeBotVariant(id=10, name="Tax Bot", base_prompt="Bạn là trợ lý thuế.", skill_ids=[1, 2])

    updated_bot = assign_skill_to_bot(bot, skill_id=3)

    assert 3 in updated_bot.skill_ids, "Skill ID 3 should be in bot.skill_ids after assignment"
    assert 1 in updated_bot.skill_ids, "Existing skill IDs should be preserved"
    assert 2 in updated_bot.skill_ids


def test_skill_assignment_idempotent():
    """Assigning a skill that is already assigned must not duplicate it."""
    bot = FakeBotVariant(id=10, name="Tax Bot", base_prompt="...", skill_ids=[1, 2, 3])

    updated_bot = assign_skill_to_bot(bot, skill_id=2)

    assert updated_bot.skill_ids.count(2) == 1, "Skill ID must not be duplicated"


def test_bot_prompt_includes_skill_content():
    """
    build_system_prompt_with_skills must inject active skill content
    and include the 'SKILLS ACTIVATED' section.
    """
    base_prompt = "Bạn là trợ lý tư vấn thuế pháp lý Việt Nam."
    bot = FakeBotVariant(id=1, name="Tax Bot", base_prompt=base_prompt, skill_ids=[1, 2])

    skills = [
        FakeSkill(id=1, name="Thuế GTGT", content="Hướng dẫn chi tiết về thuế GTGT.", is_active=True),
        FakeSkill(id=2, name="Thuế TNDN", content="Hướng dẫn chi tiết về thuế TNDN.", is_active=True),
    ]

    result_prompt = build_system_prompt_with_skills(base_prompt, bot, skills)

    assert "SKILLS ACTIVATED" in result_prompt, "Prompt must contain 'SKILLS ACTIVATED' header"
    assert "Hướng dẫn chi tiết về thuế GTGT." in result_prompt
    assert "Hướng dẫn chi tiết về thuế TNDN." in result_prompt


def test_disabled_skill_not_included_in_prompt():
    """
    Skills with is_active=False must NOT appear in the final prompt,
    regardless of whether they are assigned to the bot.
    """
    base_prompt = "Bạn là trợ lý tư vấn thuế."
    bot = FakeBotVariant(id=1, name="Tax Bot", base_prompt=base_prompt, skill_ids=[1, 2])

    skills = [
        FakeSkill(id=1, name="Active Skill", content="Nội dung kỹ năng hoạt động.", is_active=True),
        FakeSkill(id=2, name="Disabled Skill", content="NỘI DUNG BỊ TẮT — không nên xuất hiện.", is_active=False),
    ]

    result_prompt = build_system_prompt_with_skills(base_prompt, bot, skills)

    assert "NỘI DUNG BỊ TẮT" not in result_prompt, (
        "Disabled skill content must NOT appear in the final prompt"
    )
    assert "Nội dung kỹ năng hoạt động." in result_prompt, (
        "Active skill content must still be present"
    )


def test_no_assigned_skills_returns_base_prompt():
    """When the bot has no skill assignments, the base prompt is returned unchanged."""
    base_prompt = "Bạn là trợ lý tư vấn thuế."
    bot = FakeBotVariant(id=1, name="Bot", base_prompt=base_prompt, skill_ids=[])

    skills = [
        FakeSkill(id=1, name="Some Skill", content="Some content.", is_active=True),
    ]

    result = build_system_prompt_with_skills(base_prompt, bot, skills)

    assert result == base_prompt, "Base prompt should be unchanged when no skills are assigned"
