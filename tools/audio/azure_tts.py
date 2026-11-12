"""Azure Speech F0 standard Neural text-to-speech provider."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape, quoteattr

import requests

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class AzureTTS(BaseTool):
    name = "azure_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "azure"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API
    dependencies = ["cmd:az"]
    agent_skills = ["azure-tts"]
    install_instructions = "Sign in with Azure CLI and use an existing SpeechServices F0 resource."
    capabilities = ["text_to_speech", "voice_selection", "ssml_support"]
    supports = {"multilingual": True, "ssml": True, "offline": False}
    best_for = ["standard Mandarin and Thai narration on an existing Azure Speech F0 resource"]
    not_good_for = ["HD voices", "paid-tier production"]
    input_schema = {
        "type": "object",
        "required": ["text", "resource_name", "resource_group", "region"],
        "properties": {
            "text": {"type": "string"},
            "resource_name": {"type": "string"},
            "resource_group": {"type": "string"},
            "region": {"type": "string"},
            "voice": {"type": "string", "default": "zh-CN-XiaoxiaoNeural"},
            "style": {"type": "string", "default": "chat-casual for Mandarin; plain for Thai"},
            "output_path": {"type": "string"},
        },
    }
    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=256, disk_mb=10, network_required=True)
    idempotency_key_fields = ["text", "resource_name", "region", "voice", "style"]
    side_effects = ["writes an audio sample", "calls the Azure Speech F0 API"]
    user_visible_verification = ["listen to the sample for naturalness and pronunciation"]

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if shutil.which("az") else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0  # execute() rejects all non-F0 resources.

    def __init__(self) -> None:
        super().__init__()
        self._f0_key_cache: dict[tuple[str, str, str], str] = {}

    @staticmethod
    def _az(*args: str) -> str:
        result = subprocess.run(["az", "cognitiveservices", "account", *args],
                                capture_output=True, text=True, timeout=45)
        if result.returncode:
            raise RuntimeError("Azure CLI resource check failed; confirm login and resource access.")
        return result.stdout.strip()

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        try:
            name = str(inputs["resource_name"])
            group = str(inputs["resource_group"])
            region = str(inputs["region"])
            voice = str(inputs.get("voice", "zh-CN-XiaoxiaoNeural"))
            mandarin = voice.startswith("zh-CN-") and voice.endswith("Neural") and ":" not in voice
            thai = voice == "th-TH-PremwadeeNeural"
            if not (mandarin or thai):
                return ToolResult(success=False, error="Azure F0 requires an approved standard Mandarin or Thai Neural voice.")
            style = str(inputs.get("style", "chat-casual" if mandarin else "plain"))
            if mandarin and style not in {"chat-casual", "chat", "cheerful", "friendly", "gentle", "calm"}:
                return ToolResult(success=False, error="Unsupported Mandarin style for this F0 resource.")
            if thai and style != "plain":
                return ToolResult(success=False, error="The standard Thai voice is used without an expressive style.")

            resource = (name, group, region)
            key = self._f0_key_cache.get(resource)
            if key is None:
                sku = self._az("show", "--name", name, "--resource-group", group,
                               "--query", "sku.name", "-o", "tsv")
                if sku != "F0":
                    return ToolResult(success=False, error="Azure TTS refused: resource is not F0.")
                key = self._az("keys", "list", "--name", name, "--resource-group", group,
                               "--query", "key1", "-o", "tsv")
                self._f0_key_cache[resource] = key
            if not key:
                return ToolResult(success=False, error="Azure Speech key is unavailable.")
            text = str(inputs["text"])
            locale = "zh-CN" if mandarin else "th-TH"
            spoken = escape(text)
            if mandarin:
                spoken = f'<mstts:express-as style={quoteattr(style)}>{spoken}</mstts:express-as>'
            ssml = (
                '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
                f'xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang={quoteattr(locale)}>'
                f'<voice name={quoteattr(voice)}>{spoken}</voice></speak>'
            )
            response = requests.post(
                f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
                headers={
                    "Ocp-Apim-Subscription-Key": key,
                    "Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3",
                    "User-Agent": "OpenMontage-voice-sample",
                },
                data=ssml.encode("utf-8"), timeout=60,
            )
            if not response.ok:
                return ToolResult(success=False, error=f"Azure Speech F0 HTTP {response.status_code}: {response.text[:180]}")
            output = Path(inputs.get("output_path", "azure_tts_sample.mp3"))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(response.content)
            return ToolResult(success=True,
                              data={"output": str(output), "voice": voice, "style": style,
                                    "resource_tier": "F0", "text_length": len(text)},
                              artifacts=[str(output)], model=f"azure-speech/{voice}", cost_usd=0.0)
        except (OSError, requests.RequestException, RuntimeError, KeyError) as exc:
            return ToolResult(success=False, error=str(exc))
