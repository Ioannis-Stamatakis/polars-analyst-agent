"""
Memory compaction callback for token usage optimization.

This module provides a callback system that truncates tool observations
after each agent step to reduce token accumulation in the conversation history.
"""
from typing import Any


def truncate_text(text: str, max_chars: int, suffix: str = "... [truncated]") -> str:
    """
    Truncate text to a maximum character count.

    Args:
        text: The text to truncate
        max_chars: Maximum number of characters to keep
        suffix: Suffix to append when truncated

    Returns:
        Truncated text with suffix if necessary
    """
    if len(text) <= max_chars:
        return text

    return text[:max_chars - len(suffix)] + suffix


def compact_memory_callback(step: Any) -> None:
    """
    Callback that truncates observations after each agent step.

    This callback is called after each action step and reduces the size of
    tool observations to prevent excessive token usage. Errors are preserved
    with a higher character limit for debugging purposes.

    Args:
        step: ActionStep object from smolagents
    """
    if not hasattr(step, 'observations'):
        return

    if step.observations:
        original_len = len(str(step.observations))
        # Preserve errors with higher limit for debugging
        if hasattr(step, 'error') and step.error:
            step.observations = truncate_text(step.observations, max_chars=1200)
        else:
            # Normal observations get aggressive truncation
            step.observations = truncate_text(step.observations, max_chars=800)

        new_len = len(str(step.observations))
        if original_len > new_len:
            print(f"[MemoryCompact] Truncated observation: {original_len} → {new_len} chars")


def get_compact_memory_callbacks() -> list:
    """
    Get the list of memory compaction callbacks to pass to CodeAgent.

    Returns:
        List containing the compact_memory_callback function

    Example:
        >>> from smolagents import CodeAgent
        >>> from src.memory import get_compact_memory_callbacks
        >>>
        >>> agent = CodeAgent(..., step_callbacks=get_compact_memory_callbacks())
    """
    return [compact_memory_callback]


def register_compact_memory(agent: Any) -> None:
    """
    Register the memory compaction callback with an existing agent.

    This hooks into the smolagents callback system to automatically
    truncate observations after each step, reducing token usage by ~60%.

    Note: This function attempts to add callbacks post-initialization.
    For best results, pass callbacks during agent creation using
    get_compact_memory_callbacks().

    Args:
        agent: CodeAgent or MultiStepAgent instance

    Example:
        >>> from smolagents import CodeAgent
        >>> from src.memory import register_compact_memory
        >>>
        >>> agent = CodeAgent(...)
        >>> register_compact_memory(agent)  # Enable token optimization
    """
    if not hasattr(agent, 'step_callbacks'):
        print("[Memory Optimization] Warning: Agent doesn't have step_callbacks attribute")
        return

    # Try to register callback with the CallbackRegistry
    try:
        from smolagents.agents import ActionStep
        agent.step_callbacks.register(ActionStep, compact_memory_callback)
        print(f"[Memory Optimization] Registered compaction callback (max 800 chars/observation)")
    except Exception as e:
        print(f"[Memory Optimization] Warning: Could not register callback: {e}")
