import json

from tools.analysis.composition_validator import CompositionValidator


def test_atelier_virtual_source_validates_bespoke_files(tmp_path):
    entry = tmp_path / "index.tsx"
    props = tmp_path / "props.json"
    public = tmp_path / "public"
    entry.write_text("export {};", encoding="utf-8")
    props.write_text("{}", encoding="utf-8")
    public.mkdir()

    composition = {
        "render_runtime": "remotion",
        "composition_mode": "atelier",
        "cuts": [
            {
                "id": "whole",
                "source": "composition:Sawasdee",
                "in_seconds": 0,
                "out_seconds": 10,
            }
        ],
        "bespoke": {
            "entry": str(entry),
            "props_path": str(props),
            "public_dir": str(public),
            "composition_id": "Sawasdee",
        },
    }
    composition_path = tmp_path / "edit_decisions.json"
    composition_path.write_text(json.dumps(composition), encoding="utf-8")

    result = CompositionValidator().execute({"composition_path": str(composition_path)})

    assert result.success
    assert result.data["valid"]
    assert result.data["warnings"] == []
    assert any("atelier composition" in line for line in result.data["info"])
